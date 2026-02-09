from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('api/register/', views.register_donor, name='register_donor'),
    path('api/search/', views.search_donors, name='search_donors'),
    path('projects/', views.projects_page, name='projects'),
    path('reports/', views.report_list, name='report_list'),
    path('blogs/<int:id>/', views.blog_detail, name='blog_detail'),
    path('donor/<int:pk>/', views.donor_detail, name='donor_detail'),

    ]
