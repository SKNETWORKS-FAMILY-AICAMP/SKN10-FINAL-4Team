from django.urls import path
from .views import influencer_chat, send_message

urlpatterns = [
    path('chat/<int:pk>/', influencer_chat, name='influencer_chat'),
    path('chat/<int:id>/send/', send_message, name='send_message'),
    # or, if using slug: path('chat/<slug:slug>/', influencer_chat, name='influencer_chat'),
]