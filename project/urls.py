from django.contrib import admin
from django.urls import path, include
from blood_request.views import home_view, staff_dashboard, update_task_status, manager_dashboard, campaign_list, project_list, project_detail, report_list, blogs_page, resources_page, profile_edit, export_donors_csv, export_requests_csv
from blood_request import views
from blood_request import workspace_views # NEW

from django.conf import settings
from django.shortcuts import render
from django.conf.urls.static import static

urlpatterns = [
    path("admin/portal/manager/", manager_dashboard, name="manager_dashboard"), # New Team View
    path("admin/portal/users/", views.user_list, name="user_list"),
    path("admin/portal/users/add/", views.user_add, name="user_add"),
    path("admin/portal/users/<int:pk>/", views.user_edit_portal, name="user_edit_portal"),
    path("admin/portal/teams/", views.team_list, name="team_list"),
    path("admin/portal/teams/create/", views.team_create, name="team_create"),
    path("admin/portal/teams/<int:pk>/", views.team_detail, name="team_detail"),
    path("admin/portal/teams/<int:pk>/add-member/", views.team_add_member, name="team_add_member"),
    path("admin/portal/teams/<int:team_pk>/remove-member/<int:user_pk>/", views.team_remove_member, name="team_remove_member"),
    path("admin/portal/notes/create/", views.shared_note_create, name="shared_note_create"),
    path("admin/portal/notes/<int:pk>/", views.shared_note_detail, name="shared_note_detail"),
    path("admin/portal/task/<int:pk>/update/", update_task_status, name="update_task_status"),
    path("admin/portal/", staff_dashboard, name="staff_dashboard"),
    path("admin/portal/profile/", profile_edit, name="profile_edit"),
    path("admin/export/donors/", views.export_donors_csv, name="export_donors_csv"),
    path("admin/export/requests/", views.export_requests_csv, name="export_requests_csv"),
    path("api/calendar/events/", views.calendar_events_api, name="calendar_events_api"),

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
    path('workplace-living/', views.workplace_living, name='workplace_living'),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
     path('volunteering/', views.volunteering, name='volunteering'),
    
    # Workspace URLs
    path('workspaces/', workspace_views.workspace_list, name='workspace_list'),
    path('workspaces/create/', workspace_views.workspace_create, name='workspace_create'),
    path('w/<slug:slug>/', workspace_views.workspace_detail, name='workspace_detail'),
    path('w/<slug:slug>/invite/', workspace_views.workspace_invite, name='workspace_invite'),
    
    path('shared-notes/', views.shared_note_list, name='shared_note_list'),
    path('shared-notes/create/', views.shared_note_create, name='shared_note_create'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('blogs/create/', views.blog_create, name='blog_create'),

      path('admin/', admin.site.urls),

    path('', include('blood_request.urls')),

    path('news-clippings/', views.news_clippings, name='news_clippings'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

