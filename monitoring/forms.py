from django import forms
from .models import ServiceCheck, Alert, MaintenanceWindow

class ServiceCheckForm(forms.ModelForm):
    class Meta:
        model = ServiceCheck
        fields = [
            'name', 'url_or_host', 'check_type', 'interval', 'timeout'
        ]

class AlertForm(forms.ModelForm):
    email_address = forms.EmailField(required=False, label="Endereço de Email")
    email_subject = forms.CharField(required=False, label="Assunto do Email")
    email_message = forms.CharField(widget=forms.Textarea, required=False, label="Corpo da Mensagem do Email")

    telegram_chat_id = forms.CharField(required=False, label="Telegram Chat ID")
    telegram_token = forms.CharField(widget=forms.PasswordInput, required=False, label="Telegram Bot Token")
    telegram_message = forms.CharField(widget=forms.Textarea, required=False, label="Corpo da Mensagem do Telegram")

    webhook_url = forms.URLField(required=False, label="Webhook URL")
    webhook_method = forms.ChoiceField(choices=[('POST', 'POST'), ('GET', 'GET'), ('PUT', 'PUT')], required=False, label="Método HTTP")
    webhook_headers = forms.CharField(widget=forms.Textarea, required=False, help_text="Cabeçalhos JSON (opcional)", label="Cabeçalhos")
    webhook_body = forms.CharField(widget=forms.Textarea, required=False, help_text="Corpo JSON (opcional)", label="Corpo")
    webhook_username = forms.CharField(required=False, label="Usuário de Autenticação (opcional)")
    webhook_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Senha de Autenticação (opcional)")
    
    command_to_execute = forms.CharField(required=False, label="Comando a Executar")

    class Meta:
        model = Alert
        fields = ['service', 'alert_type', 'trigger', 'trigger_value', 'active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate initial data for dynamic fields if editing an existing alert
        if self.instance.pk and self.instance.config:
            config = self.instance.config
            if self.instance.alert_type == 'email':
                self.fields['email_address'].initial = config.get('email_address')
                self.fields['email_subject'].initial = config.get('subject')
                self.fields['email_message'].initial = config.get('message')
            elif self.instance.alert_type == 'telegram':
                self.fields['telegram_chat_id'].initial = config.get('chat_id')
                self.fields['telegram_token'].initial = config.get('token')
                self.fields['telegram_message'].initial = config.get('message')
            elif self.instance.alert_type == 'webhook':
                self.fields['webhook_url'].initial = config.get('url')
                self.fields['webhook_method'].initial = config.get('method', 'POST')
                self.fields['webhook_headers'].initial = json.dumps(config.get('headers', {}), indent=2) if config.get('headers') else ''
                self.fields['webhook_body'].initial = json.dumps(config.get('body', {}), indent=2) if config.get('body') else ''
                self.fields['webhook_username'].initial = config.get('username')
                self.fields['webhook_password'].initial = config.get('password')
            elif self.instance.alert_type == 'command':
                self.fields['command_to_execute'].initial = config.get('command')

        # Make dynamic fields not required by default, their requirement will be handled by clean method
        self.fields['email_address'].required = False
        self.fields['email_subject'].required = False
        self.fields['email_message'].required = False
        self.fields['telegram_chat_id'].required = False
        self.fields['telegram_token'].required = False
        self.fields['telegram_message'].required = False
        self.fields['webhook_url'].required = False
        self.fields['webhook_method'].required = False
        self.fields['webhook_headers'].required = False
        self.fields['webhook_body'].required = False
        self.fields['webhook_username'].required = False
        self.fields['webhook_password'].required = False
        self.fields['command_to_execute'].required = False

    def clean(self):
        cleaned_data = super().clean()
        alert_type = cleaned_data.get('alert_type')

        if alert_type == 'email':
            if not cleaned_data.get('email_address'):
                self.add_error('email_address', "Este campo é obrigatório para alertas de Email.")
            if not cleaned_data.get('email_subject'):
                self.add_error('email_subject', "Este campo é obrigatório para alertas de Email.")
            if not cleaned_data.get('email_message'):
                self.add_error('email_message', "Este campo é obrigatório para alertas de Email.")
        elif alert_type == 'telegram':
            if not cleaned_data.get('telegram_chat_id'):
                self.add_error('telegram_chat_id', "Este campo é obrigatório para alertas de Telegram.")
            if not cleaned_data.get('telegram_token'):
                self.add_error('telegram_token', "Este campo é obrigatório para alertas de Telegram.")
            if not cleaned_data.get('telegram_message'):
                self.add_error('telegram_message', "Este campo é obrigatório para alertas de Telegram.")
        elif alert_type == 'webhook':
            if not cleaned_data.get('webhook_url'):
                self.add_error('webhook_url', "Este campo é obrigatório para alertas de Webhook.")
            if not cleaned_data.get('webhook_method'):
                self.add_error('webhook_method', "Este campo é obrigatório para alertas de Webhook.")
            
            # Validate JSON fields if provided
            webhook_headers = cleaned_data.get('webhook_headers')
            if webhook_headers:
                try:
                    json.loads(webhook_headers)
                except json.JSONDecodeError:
                    self.add_error('webhook_headers', "Formato JSON inválido para cabeçalhos.")
            
            webhook_body = cleaned_data.get('webhook_body')
            if webhook_body:
                try:
                    json.loads(webhook_body)
                except json.JSONDecodeError:
                    self.add_error('webhook_body', "Formato JSON inválido para corpo.")

        elif alert_type == 'command':
            if not cleaned_data.get('command_to_execute'):
                self.add_error('command_to_execute', "Este campo é obrigatório para alertas de Comando.")
        
        return cleaned_data

    def save(self, commit=True):
        alert = super().save(commit=False)
        config = {}
        alert_type = self.cleaned_data.get('alert_type')

        if alert_type == 'email':
            config['email_address'] = self.cleaned_data.get('email_address')
            config['subject'] = self.cleaned_data.get('email_subject')
            config['message'] = self.cleaned_data.get('email_message')
        elif alert_type == 'telegram':
            config['chat_id'] = self.cleaned_data.get('telegram_chat_id')
            config['token'] = self.cleaned_data.get('telegram_token')
            config['message'] = self.cleaned_data.get('telegram_message')
        elif alert_type == 'webhook':
            config['url'] = self.cleaned_data.get('webhook_url')
            config['method'] = self.cleaned_data.get('webhook_method')
            
            webhook_headers = self.cleaned_data.get('webhook_headers')
            if webhook_headers:
                config['headers'] = json.loads(webhook_headers)
            
            webhook_body = self.cleaned_data.get('webhook_body')
            if webhook_body:
                config['body'] = json.loads(webhook_body)
            
            if self.cleaned_data.get('webhook_username'):
                config['username'] = self.cleaned_data.get('webhook_username')
            if self.cleaned_data.get('webhook_password'):
                config['password'] = self.cleaned_data.get('webhook_password')

        elif alert_type == 'command':
            config['command'] = self.cleaned_data.get('command_to_execute')
        
        alert.config = config
        if commit:
            alert.save()
        return alert

class MaintenanceWindowForm(forms.ModelForm):
    class Meta:
        model = MaintenanceWindow
        fields = '__all__'