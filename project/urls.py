from django.contrib import admin
from django.urls import path, include
from blood_request.views import home_view, staff_dashboard, update_task_status, manager_dashboard, campaign_list, project_list, project_detail, report_list, blogs_page, resources_page, profile_edit

from django.conf import settings
from django.shortcuts import render
from django.conf.urls.static import static

urlpatterns = [
    path("admin/portal/manager/", manager_dashboard, name="manager_dashboard"), # New Team View
    path("admin/portal/task/<int:pk>/update/", update_task_status, name="update_task_status"),
    path("admin/portal/", staff_dashboard, name="staff_dashboard"),
    path("admin/portal/profile/", profile_edit, name="profile_edit"),

    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("campaigns/", campaign_list, name="campaign_list"),
    path("projects/", project_list, name="project_list"),
    path("projects/<slug:slug>/", project_detail, name="project_detail"),
    path("blogs/", blogs_page, name="blogs"),
    path("resources/", resources_page, name="resources"),
    path("reports/", report_list, name="report_list"),
    path("blood-request/", include("blood_request.urls")),
    path('', include('blood_request.urls')),
    
    path("ckeditor5/", include('django_ckeditor_5.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

