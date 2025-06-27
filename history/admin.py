from django.contrib import admin
from .models import History


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'influencer', 'history')
    search_fields = ('user', 'influencer')

# Register your models here.
