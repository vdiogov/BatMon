from rest_framework import viewsets
from .models import ServiceCheck, CheckResult, Alert, AlertLog, MaintenanceWindow
from .serializers import ServiceCheckSerializer, CheckResultSerializer, AlertSerializer, AlertLogSerializer, MaintenanceWindowSerializer

class ServiceCheckViewSet(viewsets.ModelViewSet):
    queryset = ServiceCheck.objects.all().order_by('name')
    serializer_class = ServiceCheckSerializer

class CheckResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CheckResult.objects.all().order_by('-timestamp')
    serializer_class = CheckResultSerializer

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all().order_by('service__name', 'alert_type')
    serializer_class = AlertSerializer

class AlertLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AlertLog.objects.all().order_by('-timestamp')
    serializer_class = AlertLogSerializer

class MaintenanceWindowViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceWindow.objects.all().order_by('-start_time')
    serializer_class = MaintenanceWindowSerializer