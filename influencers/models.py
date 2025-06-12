from django.db import models
from django.utils.text import slugify

# Create your models here.

class Influencer(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    total_chat_received = models.IntegerField(default=0)
    thumbs_up = models.IntegerField(default=0)
    price_per_chat = models.IntegerField(default=0)
    image = models.ImageField(upload_to='influencers/', null=True, blank=True)
    voiceid = models.CharField(max_length=100, null=True, blank=True, help_text="ElevenLabs Voice ID")
    feature_model_id = models.CharField(max_length=100, null=True, blank=True, help_text="Apply Featrue OpenAI Model ID")
    feature_system_prompt = models.TextField(null=True, blank=True, help_text="System Prompt")
    speech_model_id = models.CharField(max_length=100, null=True, blank=True, help_text="Reflect Speech OpenAI Model ID")
    speech_system_prompt = models.TextField(null=True, blank=True, help_text="Relfect Speech System Prompt")

    def __str__(self):
        return self.name

