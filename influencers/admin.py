from django.contrib import admin
from .models import Influencer, InfluencerRating, ConversationStat

@admin.register(Influencer)
class InfluencerAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

admin.site.register(InfluencerRating)
admin.site.register(ConversationStat)

