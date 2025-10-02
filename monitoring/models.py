from django.db import models
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils import timezone
import json

class ServiceCheck(models.Model):
    CHECK_TYPE_CHOICES = [
        ('ping', 'Ping (ICMP)'),
        ('http', 'HTTP/HTTPS'),
        ('tcp', 'TCP Port'),
    ]

    STATUS_CHOICES = [
        ('ok', 'OK'),
        ('fail', 'Falha'),
        ('alert', 'Em Alerta'),
        ('maintenance', 'Em Manutenção'),
    ]

    name = models.CharField(max_length=200, unique=True)
    url_or_host = models.CharField(max_length=255)
    check_type = models.CharField(max_length=10, choices=CHECK_TYPE_CHOICES)
    interval = models.IntegerField(default=60, help_text="Intervalo de execução em segundos")
    timeout = models.IntegerField(default=10, help_text="Timeout em segundos")
    status_atual = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ok')
    last_check = models.DateTimeField(null=True, blank=True)
    periodic_task = models.ForeignKey(
        PeriodicTask,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Celery Periodic Task associated with this check."
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)  # Save the instance first to ensure self.id is available

        if is_new:
            schedule, created = IntervalSchedule.objects.get_or_create(
                every=self.interval,
                period=IntervalSchedule.SECONDS,
            )
            self.periodic_task = PeriodicTask.objects.create(
                interval=schedule,
                name=f'Service Check: {self.name}',
                task='monitoring.tasks.run_service_check', # Task to be executed
                args=json.dumps([self.id]), # Pass the ID as a JSON-encoded list
                enabled=True,
            )
        else:  # Existing ServiceCheck
            if self.periodic_task:
                # Ensure the schedule is updated or created if it doesn't exist
                schedule, created = IntervalSchedule.objects.get_or_create(
                    every=self.interval,
                    period=IntervalSchedule.SECONDS,
                )
                self.periodic_task.interval = schedule
                self.periodic_task.name = f'Service Check: {self.name}'
                self.periodic_task.task = 'monitoring.tasks.run_service_check'
                self.periodic_task.args = json.dumps([self.id])
                self.periodic_task.enabled = True
                self.periodic_task.save()
            else: # If for some reason periodic_task is null for an existing service check, create it
                schedule, created = IntervalSchedule.objects.get_or_create(
                    every=self.interval,
                    period=IntervalSchedule.SECONDS,
                )
                self.periodic_task = PeriodicTask.objects.create(
                    interval=schedule,
                    name=f'Service Check: {self.name}',
                    task='monitoring.tasks.run_service_check',
                    args=json.dumps([self.id]), # Pass the ID as a JSON-encoded list
                    enabled=True,
                )
        # Ensure the periodic_task foreign key is saved if it was just created or updated
        if is_new or (self.periodic_task and not self.periodic_task.pk):
            super().save(update_fields=['periodic_task'])

    def delete(self, *args, **kwargs):
        if self.periodic_task:
            self.periodic_task.delete()
        super().delete(*args, **kwargs)


class CheckResult(models.Model):
    service = models.ForeignKey(ServiceCheck, on_delete=models.CASCADE, related_name='results')
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    response_time = models.FloatField(null=True, blank=True, help_text="Tempo de resposta em segundos")
    status_code = models.IntegerField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.service.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {'OK' if self.success else 'FAIL'}"

class Alert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('email', 'Email'),
        ('telegram', 'Telegram'),
        ('webhook', 'Webhook'),
        ('command', 'Command'),
    ]

    TRIGGER_CHOICES = [
        ('on_fail', 'When service fails'),
        ('on_recovery', 'When service recovers'),
        ('on_fail_x_times', 'When service fails X times in a row'),
    ]

    service = models.ForeignKey(ServiceCheck, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPE_CHOICES)
    trigger = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default='on_fail')
    trigger_value = models.IntegerField(null=True, blank=True, help_text="Number of failures for 'on_fail_x_times' trigger")
    config = models.JSONField(default=dict, help_text="JSON configuration for the alert (e.g., email address, bot token, chat ID, webhook URL, command)")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Alert for {self.service.name} ({self.get_alert_type_display()})"

class AlertLog(models.Model):
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    message_sent = models.TextField()
    success = models.BooleanField(default=False)
    response_message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Log for {self.alert.service.name} ({self.alert.get_alert_type_display()}) - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

class MaintenanceWindow(models.Model):
    service = models.ForeignKey(ServiceCheck, on_delete=models.CASCADE, null=True, blank=True, related_name='maintenance_windows')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%Y-%m-%d %H:%M')} - {self.end_time.strftime('%Y-%m-%d %H:%M')})"

    def is_active(self):
        now = timezone.now()
        return self.active and self.start_time <= now <= self.end_time
