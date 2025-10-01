from celery import shared_task
from django.core.mail import send_mail
import requests
import telegram
import json
import subprocess
from .models import Alert, AlertLog, ServiceCheck

@shared_task
def send_alert(alert_id, message):
    try:
        alert = Alert.objects.get(id=alert_id)
        success = False
        response_message = ""

        if alert.alert_type == 'email':
            try:
                send_mail(
                    subject=f"BatMon Alert: {alert.service.name}",
                    message=message,
                    from_email="noreply@batmon.com", # This should be configured in settings.py
                    recipient_list=[alert.config.get('email_address')],
                    fail_silently=False,
                )
                success = True
                response_message = "Email sent successfully."
            except Exception as e:
                response_message = f"Email sending failed: {e}"

        elif alert.alert_type == 'telegram':
            try:
                bot = telegram.Bot(token=alert.config.get('bot_token'))
                bot.send_message(chat_id=alert.config.get('chat_id'), text=message)
                success = True
                response_message = "Telegram message sent successfully."
            except Exception as e:
                response_message = f"Telegram message failed: {e}"

        elif alert.alert_type == 'webhook':
            try:
                headers = {'Content-Type': 'application/json'}
                payload = {'alert_message': message, 'service_name': alert.service.name, 'status': alert.service.status_atual}
                response = requests.post(alert.config.get('webhook_url'), headers=headers, data=json.dumps(payload), timeout=10)
                response.raise_for_status()
                success = True
                response_message = f"Webhook sent successfully. Status: {response.status_code}"
            except requests.exceptions.RequestException as e:
                response_message = f"Webhook failed: {e}"

        elif alert.alert_type == 'command':
            try:
                command = alert.config.get('command')
                process = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=alert.config.get('timeout', 60))
                if process.returncode == 0:
                    success = True
                    response_message = f"Command executed successfully. Output: {process.stdout}"
                else:
                    response_message = f"Command failed. Error: {process.stderr}"
            except subprocess.TimeoutExpired:
                response_message = f"Command timed out after {alert.config.get('timeout', 60)} seconds."
            except Exception as e:
                response_message = f"Command execution failed: {e}"

        AlertLog.objects.create(
            alert=alert,
            message_sent=message,
            success=success,
            response_message=response_message
        )

    except Alert.DoesNotExist:
        print(f"Alert with id {alert_id} not found.")
    except Exception as e:
        print(f"Error in send_alert task for alert {alert_id}: {e}")