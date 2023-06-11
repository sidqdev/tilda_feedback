from django.urls import path
from .views import *
from .bot_handler import start_bot

start_bot()

urlpatterns = [
    path("create_feedback/", create_feedback),    
    path('get_feedbacks', get_feedbacks),
]
