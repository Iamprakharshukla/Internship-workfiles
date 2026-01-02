from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("blood_request.urls")),
]

# AUTOMATICALLY APPLY MIGRATIONS FOR IN-MEMORY DATABASE
# This workaround ensures tables exist when using :memory: to avoid locking issues.
from django.conf import settings
from django.core.management import call_command
import sys

# We check for 'runserver' to ensure we only run this when the server starts,
# and we catch all errors to prevent crashes if it runs multiple times.
if settings.DEBUG and settings.DATABASES['default']['NAME'] == ':memory:' and 'runserver' in sys.argv:
    try:
        call_command('migrate', interactive=False)
    except Exception:
        pass
