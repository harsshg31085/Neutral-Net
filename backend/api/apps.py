from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    detector = None

    def ready(self):
        from .utils.bias_detector import BiasDetector

        if ApiConfig.detector is None:
            ApiConfig.detector = BiasDetector()