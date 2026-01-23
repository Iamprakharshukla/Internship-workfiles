from django.urls import path
from .views import chat_view

urlpatterns = [
    path('ask/', chat_view, name='chat_ask'),
]
