from django.urls import path
from .views import chatbot_page

urlpatterns = [
    path("chat/", chatbot_page, name="chatbot"),
]
