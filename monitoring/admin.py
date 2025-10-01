from django.contrib import admin
from .models import ServiceCheck, CheckResult, Alert, AlertLog, MaintenanceWindow # Import MaintenanceWindow

@admin.register(ServiceCheck)
class ServiceCheckAdmin(admin.ModelAdmin):
    list_display = ('name', 'url_or_host', 'check_type', 'interval', 'timeout', 'status_atual', 'last_check', 'periodic_task')
    list_filter = ('check_type', 'status_atual')
    search_fields = ('name', 'url_or_host')
    readonly_fields = ('last_check', 'status_atual', 'periodic_task')

@admin.register(CheckResult)
class CheckResultAdmin(admin.ModelAdmin):
    list_display = ('service', 'timestamp', 'success', 'response_time', 'status_code')
    list_filter = ('service', 'success')
    search_fields = ('service__name', 'message')
    readonly_fields = ('service', 'timestamp', 'success', 'response_time', 'status_code', 'message')

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('service', 'alert_type', 'trigger', 'trigger_value', 'active')
    list_filter = ('alert_type', 'trigger', 'active')
    search_fields = ('service__name',)
    raw_id_fields = ('service',)

@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display = ('alert', 'timestamp', 'success', 'response_message')
    list_filter = ('alert__service__name', 'success')
    search_fields = ('alert__service__name', 'message_sent', 'response_message')
    readonly_fields = ('alert', 'timestamp', 'message_sent', 'success', 'response_message')

@admin.register(MaintenanceWindow)
class MaintenanceWindowAdmin(admin.ModelAdmin):
    list_display = ('title', 'service', 'start_time', 'end_time', 'active', 'is_active')
    list_filter = ('active', 'service')
    search_fields = ('title', 'description', 'service__name')
    raw_id_fields = ('service',)
    actions = ['activate_maintenance', 'deactivate_maintenance']

    def activate_maintenance(self, request, queryset):
        queryset.update(active=True)
        self.message_user(request, "Selected maintenance windows activated.")
    activate_maintenance.short_description = "Activate selected maintenance windows"

    def deactivate_maintenance(self, request, queryset):
        queryset.update(active=False)
        self.message_user(request, "Selected maintenance windows deactivated.")
    deactivate_maintenance.short_description = "Deactivate selected maintenance windows"
