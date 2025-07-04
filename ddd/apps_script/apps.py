from django.apps import AppConfig


class AppsScriptConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps_script'
    
    def ready(self):
        from .cron import updater
        updater.start()

