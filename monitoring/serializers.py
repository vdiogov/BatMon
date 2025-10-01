from rest_framework import serializers
from .models import ServiceCheck, CheckResult, Alert, AlertLog, MaintenanceWindow

class ServiceCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCheck
        fields = '__all__'
        read_only_fields = ('status_atual', 'last_check', 'periodic_task')

class CheckResultSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    class Meta:
        model = CheckResult
        fields = '__all__'
        read_only_fields = ('service', 'timestamp')

class AlertSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = ('service',)

class AlertLogSerializer(serializers.ModelSerializer):
    alert_service_name = serializers.CharField(source='alert.service.name', read_only=True)
    alert_type = serializers.CharField(source='alert.alert_type', read_only=True)
    class Meta:
        model = AlertLog
        fields = '__all__'
        read_only_fields = ('alert', 'timestamp')

class MaintenanceWindowSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    class Meta:
        model = MaintenanceWindow
        fields = '__all__'