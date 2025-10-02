from django import forms
from .models import ServiceCheck, Alert, MaintenanceWindow

class ServiceCheckForm(forms.ModelForm):
    class Meta:
        model = ServiceCheck
        fields = [
            'name', 'url_or_host', 'check_type', 'interval', 'timeout'
        ]

class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = '__all__'

class MaintenanceWindowForm(forms.ModelForm):
    class Meta:
        model = MaintenanceWindow
        fields = '__all__'