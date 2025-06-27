from django.urls import path
from .views import influencer_chat, send_message, create_influencer
from . import views


urlpatterns = [
    path('chat/<int:pk>/', influencer_chat, name='influencer_chat'),
    path('chat/<int:id>/send/', send_message, name='send_message'),
    path('create/', views.create_influencer, name='create_influencer'),
    path('rate/<int:influencer_id>/', views.rate_influencer, name='rate_influencer'),
    path('rate/<int:influencer_id>/stats/', views.influencer_rating_stats, name='influencer_rating_stats'),
    path('admin-stats/', views.admin_stats, name='admin_stats'),

    # or, if using slug: path('chat/<slug:slug>/', influencer_chat, name='influencer_chat'),
]