from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('api/register/', views.register_donor, name='register_donor'),
    path('api/search/', views.search_donors, name='search_donors'),
    path('blogs/', views.blogs_page, name='blogs'),
    path('projects/', views.projects_page, name='projects'),
]
