from django.apps import AppConfig


class InfluencersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'influencers'

    def ready(self):
        import influencers.signals
