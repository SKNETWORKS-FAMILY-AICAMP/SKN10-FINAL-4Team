from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('', views.chatbot_view, name='chatbot'),
] 