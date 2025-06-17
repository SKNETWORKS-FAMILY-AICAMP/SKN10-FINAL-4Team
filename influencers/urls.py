from django.urls import path
from .views import influencer_chat, send_message, create_influencer
from . import views


urlpatterns = [
    path('chat/<int:pk>/', influencer_chat, name='influencer_chat'),
    path('chat/<int:id>/send/', send_message, name='send_message'),
    path('create/', views.create_influencer, name='create_influencer'),

    # or, if using slug: path('chat/<slug:slug>/', influencer_chat, name='influencer_chat'),
]