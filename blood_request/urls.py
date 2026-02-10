from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('api/register/', views.register_donor, name='register_donor'),
    path('api/search/', views.search_donors, name='search_donors'),
    path('api/notes/', views.personal_notes_api, name='personal_notes_api'),
    path('projects/', views.projects_page, name='projects'),

    path('reports/', views.report_list, name='report_list'),
    path('blogs/<int:id>/', views.blog_detail, name='blog_detail'),
    path('donor/<int:pk>/', views.donor_detail, name='donor_detail'),


    path(
    'career-and-fellowship/',
    views.career_fellowship,
    name='career_fellowship'
),


    path('locations/', views.locations, name='locations'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/create/', views.appointment_create, name='appointment_create'),
]
