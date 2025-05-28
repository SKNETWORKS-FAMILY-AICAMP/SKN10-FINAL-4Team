from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Influencer
import json
import openai
import os
import requests
from django.conf import settings
from dotenv import load_dotenv
from django.conf import settings
import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from influencers.models import Influencer

load_dotenv()  # take environment variables from .env.

# API Keys
# 854aeb8ff1235662fb24541664f10311
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

elevenlabs = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

def influencer_chat(request, pk):
    influencer = get_object_or_404(Influencer, pk=pk)
    return render(request, 'influencers/chat.html', {'influencer': influencer})

def send_message(request, id):
    if request.method == 'POST':
        message = request.POST.get('message')
        print(f"[BACKEND] Received message for influencer {id}: {message}")
        try:
            influencer = get_object_or_404(Influencer, pk=id)
            # 1. Get answer from GPT using OpenAI
            print(f"[BACKEND] Getting answer from GPT using OpenAI")
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "너는 침착맨이야. 침착맨의 어투와 말투로 대답해줘. 장난스럽게."},
                    {"role": "user", "content": message}
                ]
            )
            answer = response.choices[0].message.content

            print(f"Answer: {answer}")

            # 2. Generate TTS audio from answer using ElevenLabs
            if not influencer.voiceid:
                raise Exception("Influencer does not have a voiceid set for ElevenLabs.")

            response_gen = elevenlabs.text_to_speech.convert(
                voice_id=influencer.voiceid,
                output_format="mp3_22050_32",
                text=answer,
                model_id="eleven_turbo_v2_5",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True,
                    speed=1.0,
                ),
            )

            # Collect the audio content from the generator
            audio_content = b""
            for chunk in response_gen:
                audio_content += chunk

            if not audio_content:
                raise Exception("No audio content received from ElevenLabs API")

            # Save the audio file
            audio_dir = os.path.join(settings.MEDIA_ROOT, 'influencers', str(id), 'tts_audio')
            os.makedirs(audio_dir, exist_ok=True)
            audio_filename = f"tts_{str(abs(hash(answer)))[:8]}.mp3"
            audio_path = os.path.join(audio_dir, audio_filename)

            with open(audio_path, "wb") as f:
                f.write(audio_content)

            # 4. Return the answer and audio file URL
            audio_url = f"/media/influencers/{id}/tts_audio/{audio_filename}"
            print(f"[BACKEND] Audio URL: {audio_url}")
        except Exception as e:
            answer = f"API error: {str(e)}"
            audio_url = None
            print(f"Error: {str(e)}")  # Log the error

        return JsonResponse({
            'status': 'success', 
            'received': message, 
            'answer': answer, 
            'audio_url': audio_url
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)