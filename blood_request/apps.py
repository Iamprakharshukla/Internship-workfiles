from django.apps import AppConfig


class BloodRequestConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "blood_request"

    def ready(self):
        import blood_request.signals
