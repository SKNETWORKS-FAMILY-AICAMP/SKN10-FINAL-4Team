from django.contrib import admin
from .models import Influencer

@admin.register(Influencer)
class InfluencerAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'total_chat_received', 'thumbs_up', 'price_per_chat')
    search_fields = ('name', 'description')
