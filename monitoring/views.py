from django.shortcuts import render, get_object_or_404
from .models import ServiceCheck, CheckResult, MaintenanceWindow, AlertLog
from datetime import timedelta
from django.utils import timezone

def status_page(request):
    services = ServiceCheck.objects.all()
    active_maintenance_windows = MaintenanceWindow.objects.filter(
        active=True,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    ).order_by('start_time')

    for service in services:
        # Check if service is under maintenance
        service.in_maintenance = False
        for mw in active_maintenance_windows:
            if mw.service == service or mw.service is None: # Global or service-specific maintenance
                service.in_maintenance = True
                service.display_status = 'maintenance'
                break
        
        if not service.in_maintenance:
            service.display_status = service.status_atual # Use actual status if not in maintenance

        # Fetch last 24 hours of results for charting
        time_threshold = timezone.now() - timedelta(hours=24)
        results = service.results.filter(timestamp__gte=time_threshold).order_by('timestamp')
        
        service.chart_labels = [result.timestamp.strftime('%H:%M') for result in results]
        service.chart_data = [result.response_time if result.success else 0 for result in results] # Use 0 for failures on chart
        service.uptime_data = [1 if result.success else 0 for result in results] # 1 for uptime, 0 for downtime

    context = {
        'services': services,
        'active_maintenance_windows': active_maintenance_windows,
    }
    return render(request, 'monitoring/status.html', context)

def service_detail(request, service_id):
    service = get_object_or_404(ServiceCheck, pk=service_id)
    
    # Check if service is under maintenance for detail page
    active_maintenance_windows = MaintenanceWindow.objects.filter(
        active=True,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    )
    service.in_maintenance = False
    for mw in active_maintenance_windows:
        if mw.service == service or mw.service is None:
            service.in_maintenance = True
            service.display_status = 'maintenance'
            break
    
    if not service.in_maintenance:
        service.display_status = service.status_atual

    # Fetch all historical results for the detail page
    results = service.results.all().order_by('-timestamp')[:100] # Limit to last 100 for performance
    
    # Prepare data for charts (e.g., last 7 days)
    time_threshold = timezone.now() - timedelta(days=7)
    chart_results = service.results.filter(timestamp__gte=time_threshold).order_by('timestamp')

    chart_labels = [result.timestamp.strftime('%Y-%m-%d %H:%M') for result in chart_results]
    chart_response_time_data = [result.response_time if result.success else 0 for result in chart_results]
    chart_uptime_data = [1 if result.success else 0 for result in chart_results]

    context = {
        'service': service,
        'results': results,
        'chart_labels': chart_labels,
        'chart_response_time_data': chart_response_time_data,
        'chart_uptime_data': chart_uptime_data,
    }
    return render(request, 'monitoring/service_detail.html', context)

from django.contrib.auth.decorators import login_required
from django.db.models import Count

@login_required
def dashboard_view(request):
    total_services = ServiceCheck.objects.count()
    services_up = ServiceCheck.objects.filter(status_atual='ok').count()
    services_down = ServiceCheck.objects.filter(status_atual='fail').count()
    services_alert = ServiceCheck.objects.filter(status_atual='alert').count()
    services_maintenance = ServiceCheck.objects.filter(status_atual='maintenance').count()

    recent_results = CheckResult.objects.all().order_by('-timestamp')[:10]
    recent_alerts = AlertLog.objects.all().order_by('-timestamp')[:10]
    upcoming_maintenance = MaintenanceWindow.objects.filter(
        end_time__gte=timezone.now()
    ).order_by('start_time')[:5]

    context = {
        'total_services': total_services,
        'services_up': services_up,
        'services_down': services_down,
        'services_alert': services_alert,
        'services_maintenance': services_maintenance,
        'recent_results': recent_results,
        'recent_alerts': recent_alerts,
        'upcoming_maintenance': upcoming_maintenance,
    }
    return render(request, 'monitoring/dashboard.html', context)
