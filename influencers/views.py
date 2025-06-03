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

# API Keys .env에서 가져오기
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

#클라이언트 생성
client = openai.OpenAI(api_key=OPENAI_API_KEY)
elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)

#인플루언서 채팅 페이지 렌더링
def influencer_chat(request, pk):
    influencer = get_object_or_404(Influencer, pk=pk)
    return render(request, 'influencers/chat.html', {'influencer': influencer})

#유저 잇풋 openai에 전달
def send_message(request, id):
    if request.method == 'POST':
        message = request.POST.get('message')
        print(f"[BACKEND] Received message for influencer {id}: {message}")
        try:

            #인플루언서 모델 가져오기
            influencer = get_object_or_404(Influencer, pk=id)
            #json으로 받은 메시지를 openai에 전달
            response = send_message_to_gpt(message, influencer.response_model_id, influencer.response_system_prompt)
            print(f"Answer: {response}")

            answer = send_message_to_gpt(response, influencer.speech_style_model_id, influencer.speech_style_system_prompt)
            print(f"Answer: {answer}")

            audio_url = generate_tts_audio(influencer, answer)
            print(f"[BACKEND] Audio URL: {audio_url}")
        
        except Exception as e:
            answer = f"API error: {str(e)}"
            audio_url = None
            print(f"Error: {str(e)}")  # Log the error

        #json으로 프론트엔드에 전달
        return JsonResponse({
            'status': 'success', 
            'received': message, 
            'answer': answer, 
            'audio_url': audio_url
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def send_message_to_gpt(message, model_id, system_prompt):
    print(f"[BACKEND] Getting answer from GPT using OpenAI")
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content


def generate_tts_audio(influencer, answer):
    if not influencer.voiceid:
        raise Exception("Influencer does not have a voiceid set for ElevenLabs.")
    response_gen = elevenlabs.text_to_speech.convert(
        voice_id=influencer.voiceid,
        output_format="mp3_22050_32",
        text=answer,
        model_id="eleven_turbo_v2_5",

        #이 변수도 모델에 정의해야할듯 ㅠ
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.75,
            style=0.1,
            use_speaker_boost=True,
            speed=1.0,
        ),
    )
    audio_content = b""
    for chunk in response_gen:
        audio_content += chunk
    if not audio_content:
        raise Exception("No audio content received from ElevenLabs API")
    audio_dir = os.path.join(settings.MEDIA_ROOT, 'influencers', str(influencer.id), 'tts_audio')
    os.makedirs(audio_dir, exist_ok=True)
    audio_filename = f"tts_{str(abs(hash(answer)))[:8]}.mp3"
    audio_path = os.path.join(audio_dir, audio_filename)
    with open(audio_path, "wb") as f:
        f.write(audio_content)
    audio_url = f"/media/influencers/{influencer.id}/tts_audio/{audio_filename}"
    return audio_url