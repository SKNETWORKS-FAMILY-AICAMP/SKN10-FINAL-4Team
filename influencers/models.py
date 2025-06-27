from django.db import models
from django.utils.text import slugify
from django.conf import settings

# Create your models here.

class Influencer(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    # total_chat_received = models.IntegerField(default=0, blank=True, null=True)
    # thumbs_up = models.IntegerField(default=0, blank=True, null=True)
    # price_per_chat = models.IntegerField(default=0, blank=True, null=True)
    image = models.ImageField(upload_to='influencers/', null=True, blank=True)
    voiceid = models.CharField(max_length=100, null=True, blank=True, help_text="ElevenLabs Voice ID")
    feature_model_id = models.CharField(max_length=100, null=True, blank=True, help_text="Apply Feature OpenAI Model ID")
    feature_system_prompt = models.TextField(null=True, blank=True, help_text="System Prompt")
    speech_model_id = models.CharField(max_length=100, null=True, blank=True, help_text="Reflect Speech OpenAI Model ID")
    speech_system_prompt = models.TextField(null=True, blank=True, help_text="Reflect Speech System Prompt")
    created_mode = models.CharField(max_length=15, choices=[('finetune', 'Finetune'), ('non-finetune', 'Non-Finetune')], default='non-finetune')

    def is_ready(self):
        # List all fields that must be filled for production
        required_fields = [
            self.name,
            self.voiceid,
            self.feature_model_id,
            self.feature_system_prompt,
            self.speech_model_id,
            self.speech_system_prompt,
        ]
        # All must be non-empty/non-null
        return all(required_fields)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        return self.ratings.aggregate(models.Avg('stars'))['stars__avg'] or 0

    @property
    def rating_count(self):
        return self.ratings.count()

class InfluencerRating(models.Model):
    influencer = models.ForeignKey('Influencer', on_delete=models.CASCADE, related_name='ratings')
    stars = models.PositiveSmallIntegerField()  # 1 to 5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.influencer.name} - {self.stars} stars"

class ConversationStat(models.Model):
    influencer = models.ForeignKey('Influencer', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    user_message = models.TextField()
    ai_answer = models.TextField()
    word_count = models.PositiveIntegerField()
    response_time = models.FloatField(help_text="Seconds")
    tokens_used = models.PositiveIntegerField(default=0)
    tts_credits_used = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.influencer.name} ({self.created_at:%Y-%m-%d %H:%M:%S}) - {self.word_count} words, {self.response_time:.2f}s"
    