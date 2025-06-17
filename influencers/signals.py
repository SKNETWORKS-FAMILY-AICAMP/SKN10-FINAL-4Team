from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Influencer

@receiver(post_save, sender=Influencer)
def initialize_auto_influencer(sender, instance, created, **kwargs):
    # Only run for new objects created in auto mode and with empty fields

    print(f"Initializing auto influencer: {instance.id}")
    if created and instance.created_mode == 'auto':
        updated = False

        # Example: Use YouTube URL to generate other fields
        if instance.youtube_url:
            # Call your custom logic here, e.g.:
            from .youtube_utils import generate_voiceid, generate_feature_model_id, generate_prompts

            if not instance.voiceid:
                instance.voiceid = generate_voiceid(instance.youtube_url)
                updated = True
            if not instance.feature_model_id:
                instance.feature_model_id = generate_feature_model_id(instance.youtube_url)
                updated = True
            if not instance.feature_system_prompt:
                instance.feature_system_prompt = generate_prompts(instance.youtube_url, prompt_type='feature')
                updated = True
            if not instance.speech_model_id:
                instance.speech_model_id = generate_feature_model_id(instance.youtube_url, speech=True)
                updated = True
            if not instance.speech_system_prompt:
                instance.speech_system_prompt = generate_prompts(instance.youtube_url, prompt_type='speech')
                updated = True

        if updated:
            instance.save()