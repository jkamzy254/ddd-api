from django.apps import AppConfig


class SvcConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'DDD_Modules.MT.svc'
    
    def ready(self):
        from .cron import updater
        updater.start()

