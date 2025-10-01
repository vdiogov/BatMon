from celery import shared_task
from .models import ServiceCheck, CheckResult, Alert, MaintenanceWindow # Import Alert and MaintenanceWindow models
from .alert_tasks import send_alert # Import send_alert task
import subprocess
import requests
import socket
import time
from django.utils import timezone
import logging
import json # Import json module

logger = logging.getLogger(__name__)

@shared_task
def run_service_check(service_check_arg): # Use a generic name to inspect the raw argument
    logger.info(f"Received raw argument for service check: {service_check_arg} (Type: {type(service_check_arg)})")
    service_check_id = None
    try:
        # Attempt to parse if it's a JSON string
        if isinstance(service_check_arg, str):
            parsed_arg = json.loads(service_check_arg)
            if isinstance(parsed_arg, list) and len(parsed_arg) > 0:
                service_check_id = parsed_arg[0]
            else:
                logger.warning(f"JSON parsed but not a list or empty: {parsed_arg}")
        elif isinstance(service_check_arg, list) and len(service_check_arg) > 0:
            service_check_id = service_check_arg[0]
        else:
            logger.warning(f"Argument is not a string or list: {service_check_arg}")

        if service_check_id is None:
            logger.error("Could not extract service_check_id from the argument. Exiting task.")
            return # Exit if ID cannot be determined

        logger.info(f"Extracted service_check_id: {service_check_id}")
        service_check = ServiceCheck.objects.get(id=service_check_id)
        logger.info(f"ServiceCheck '{service_check.name}' found. Type: {service_check.check_type}")
        
        # Check for active maintenance windows
        active_maintenance = MaintenanceWindow.objects.filter(
            active=True,
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now()
        ).filter(models.Q(service=service_check) | models.Q(service__isnull=True)).exists()

        if active_maintenance:
            logger.info(f"Service '{service_check.name}' is in maintenance. Skipping check and alerts.")
            service_check.status_atual = 'maintenance'
            service_check.last_check = timezone.now()
            service_check.save()
            return # Do not proceed with checks or alerts if in maintenance
        
        result = {} # Initialize result

        if service_check.check_type == 'ping':
            result = check_ping(service_check)
        elif service_check.check_type == 'http':
            result = check_http(service_check)
        elif service_check.check_type == 'tcp':
            result = check_tcp(service_check)
        else:
            result = {
                'success': False,
                'message': f"Unknown check type: {service_check.check_type}"
            }
        
        logger.info(f"Check for '{service_check.name}' completed. Success: {result.get('success')}, Message: {result.get('message')}")

        CheckResult.objects.create(
            service=service_check,
            success=result.get('success', False),
            response_time=result.get('response_time'),
            status_code=result.get('status_code'),
            message=result.get('message')
        )
        logger.info(f"CheckResult created for '{service_check.name}'.")

        # Determine previous status for alert triggering
        previous_status = service_check.status_atual
        
        # Update service status
        service_check.last_check = timezone.now()
        if result.get('success'):
            service_check.status_atual = 'ok'
        else:
            service_check.status_atual = 'fail'
        service_check.save()
        logger.info(f"ServiceCheck '{service_check.name}' status updated to '{service_check.status_atual}'. Last check: {service_check.last_check}")

        # Alert triggering logic (only if not in maintenance)
        if not active_maintenance:
            if service_check.status_atual == 'fail' and previous_status != 'fail':
                # Service just failed, trigger 'on_fail' alerts
                for alert in service_check.alerts.filter(active=True, trigger='on_fail'):
                    send_alert.delay(alert.id, f"Service '{service_check.name}' just went DOWN! Message: {result.get('message')}")
            
            if service_check.status_atual == 'ok' and previous_status == 'fail':
                # Service just recovered, trigger 'on_recovery' alerts
                for alert in service_check.alerts.filter(active=True, trigger='on_recovery'):
                    send_alert.delay(alert.id, f"Service '{service_check.name}' has recovered! Message: {result.get('message')}")

            if service_check.status_atual == 'fail':
                # Check for 'on_fail_x_times' alerts
                for alert in service_check.alerts.filter(active=True, trigger='on_fail_x_times', trigger_value__isnull=False):
                    recent_failures = service_check.results.filter(success=False).order_by('-timestamp')[:alert.trigger_value]
                    if len(recent_failures) == alert.trigger_value and all(not r.success for r in recent_failures):
                        # Ensure we only send the alert once per failure streak
                        last_alert_log = alert.logs.filter(success=True).order_by('-timestamp').first()
                        if not last_alert_log or last_alert_log.timestamp < recent_failures.last().timestamp:
                            send_alert.delay(alert.id, f"Service '{service_check.name}' has failed {alert.trigger_value} times in a row! Message: {result.get('message')}")

    except ServiceCheck.DoesNotExist:
        logger.error(f"ServiceCheck with id {service_check_id} not found.")
    except Exception as e:
        logger.error(f"Error in run_service_check for service {service_check_id}: {e}", exc_info=True)

def check_ping(service_check):
    start_time = time.time()
    try:
        # The '-c 1' option sends only one packet.
        # The '-W' option sets the timeout in seconds.
        command = ['ping', '-c', '1', '-W', str(service_check.timeout), service_check.url_or_host]
        result = subprocess.run(command, capture_output=True, text=True, timeout=service_check.timeout)
        response_time = (time.time() - start_time)
        
        if result.returncode == 0:
            return {
                'success': True,
                'response_time': response_time,
                'message': result.stdout
            }
        else:
            return {
                'success': False,
                'response_time': response_time,
                'message': result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'message': f"Ping timed out after {service_check.timeout} seconds."
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

def check_http(service_check):
    start_time = time.time()
    try:
        response = requests.get(service_check.url_or_host, timeout=service_check.timeout)
        response_time = (time.time() - start_time)
        
        if 200 <= response.status_code < 300:
            return {
                'success': True,
                'response_time': response_time,
                'status_code': response.status_code,
                'message': f"Status code: {response.status_code}"
            }
        else:
            return {
                'success': False,
                'response_time': response_time,
                'status_code': response.status_code,
                'message': f"Unexpected status code: {response.status_code}"
            }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'message': f"Request timed out after {service_check.timeout} seconds."
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'message': str(e)
        }

def check_tcp(service_check):
    start_time = time.time()
    try:
        host, port = service_check.url_or_host.split(':')
        port = int(port)
        
        with socket.create_connection((host, port), timeout=service_check.timeout) as sock:
            response_time = (time.time() - start_time)
            return {
                'success': True,
                'response_time': response_time,
                'message': f"Successfully connected to {host}:{port}"
            }
    except socket.timeout:
        return {
            'success': False,
            'message': f"Connection to {service_check.url_or_host} timed out after {service_check.timeout} seconds."
        }
    except (socket.error, ValueError) as e:
        return {
            'success': False,
            'message': str(e)
        }