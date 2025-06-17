from django import forms
from .models import Influencer

class InfluencerForm(forms.ModelForm):
    class Meta:
        model = Influencer
        fields = [
            'name', 'youtube_url', 'image', 'description',
            'voiceid', 'feature_model_id', 'feature_system_prompt',
            'speech_model_id', 'speech_system_prompt'
        ]