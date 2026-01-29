from django.contrib import admin
from django.urls import path, include
from blood_request.views import home_view, staff_dashboard, update_task_status, manager_dashboard, campaign_list  # Import dashboard views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("portal/", staff_dashboard, name="staff_dashboard"),
    path("portal/manager/", manager_dashboard, name="manager_dashboard"), # New Team View
    path("portal/task/<int:pk>/update/", update_task_status, name="update_task_status"),
    path("campaigns/", campaign_list, name="campaign_list"),
    path("blood-request/", include("blood_request.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

