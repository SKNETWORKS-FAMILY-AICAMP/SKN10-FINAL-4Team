from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import Influencer, InfluencerRating, ConversationStat
from .forms import InfluencerForm
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
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from history.models import History
from users.models import User
import time
from django.db.models import Sum, Avg, Count
from datetime import datetime, timedelta
from django.utils import timezone

load_dotenv()  # take environment variables from .env.

# API Keys .env에서 가져오기
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

#클라이언트 생성
client = openai.OpenAI(api_key=OPENAI_API_KEY)
elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)

User = get_user_model()

#인플루언서 채팅 페이지 렌더링
def influencer_chat(request, pk):
    influencer = get_object_or_404(Influencer, pk=pk)
    return render(request, 'influencers/chat.html', {'influencer': influencer})

#유저 잇풋 openai에 전달
@csrf_exempt
def send_message(request, id):
    if request.method == 'POST':
        start_time = time.time()
        message = request.POST.get('message')
        user = request.user
        print(f"[BACKEND] Received message for influencer {id}: {message}")
        tokens_used = 0
        tts_credits_used = 0
        try:
            influencer = get_object_or_404(Influencer, pk=id)
            print(influencer)
            if request.user.is_authenticated and isinstance(request.user, User):
                history_obj, _ = History.objects.get_or_create(
                    user=user,
                    influencer=influencer,
                    defaults={'history': []}
                )
                chat_history = history_obj.history
            else:
                chat_history = []
            response, tokens_used = send_message_to_gpt(message, influencer.feature_model_id, influencer.feature_system_prompt, chat_history)
            print(f"Answer: {response}")
            answer, tokens_used2 = send_message_to_gpt(response, influencer.speech_model_id, influencer.speech_system_prompt)
            print(f"Answer: {answer}")
            tokens_used += tokens_used2
            audio_url = generate_tts_audio(influencer, answer)
            print(f"[BACKEND] Audio URL: {audio_url}")
            tts_credits_used = len(answer)
            history_obj.history.extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": answer}
            ])
            history_obj.save()
        except Exception as e:
            answer = f"API error: {str(e)}"
            audio_url = None
            print(f"Error: {str(e)}")
        end_time = time.time()
        elapsed = end_time - start_time
        word_count = len(answer.split()) if answer else 0
        ConversationStat.objects.create(
            influencer=influencer,
            user=user if user.is_authenticated else None,
            user_message=message,
            ai_answer=answer,
            word_count=word_count,
            response_time=elapsed,
            tokens_used=tokens_used,
            tts_credits_used=tts_credits_used
        )
        return JsonResponse({
            'status': 'success',
            'received': message,
            'answer': answer,
            'audio_url': audio_url,
            'response_time': elapsed,
            'word_count': word_count,
            'tokens_used': tokens_used,
            'tts_credits_used': tts_credits_used
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)


def send_message_to_gpt(message, model_id, system_prompt, chat_history=None):
    print(f"[BACKEND] Getting answer from GPT using OpenAI")
    if chat_history:
        messages = [{"role": "system", "content": system_prompt}] + chat_history + [{"role": "user", "content": message}]
        response = client.chat.completions.create(
            model=model_id,
            messages=messages
        )
        answer = response.choices[0].message.content
        tokens = getattr(response, 'usage', None)
        if tokens:
            total_tokens = tokens.total_tokens
        else:
            total_tokens = 0
        return answer, total_tokens
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    )
    answer = response.choices[0].message.content
    tokens = getattr(response, 'usage', None)
    if tokens:
        total_tokens = tokens.total_tokens
    else:
        total_tokens = 0
    return answer, total_tokens


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



@csrf_exempt
def create_influencer(request):
    if request.method == 'POST':
        mode = request.POST.get('mode', 'manual')
        form = InfluencerForm(request.POST, request.FILES)
        if form.is_valid():
            influencer = form.save(commit=False)
            influencer.created_mode = mode
            influencer.save()
            return redirect('landingpage')  # or wherever you want to go
    else:
        form = InfluencerForm()
    return render(request, 'influencers/create_influencer.html', {'form': form})

@require_POST
def rate_influencer(request, influencer_id):
    influencer = Influencer.objects.get(pk=influencer_id)
    try:
        stars = int(request.POST.get('stars'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid star rating'}, status=400)
    if stars < 1 or stars > 5:
        return JsonResponse({'error': 'Invalid star rating'}, status=400)
    InfluencerRating.objects.create(influencer=influencer, stars=stars)
    return JsonResponse({'success': True})

def influencer_rating_stats(request, influencer_id):
    influencer = Influencer.objects.get(pk=influencer_id)
    return JsonResponse({
        'average_rating': influencer.average_rating or 0,
        'rating_count': influencer.rating_count
    })

def admin_stats(request):
    total_chats = ConversationStat.objects.count()
    total_tokens = ConversationStat.objects.aggregate(total=Sum('tokens_used'))['total'] or 0
    total_credits = ConversationStat.objects.aggregate(total=Sum('tts_credits_used'))['total'] or 0
    avg_response_time = ConversationStat.objects.aggregate(avg=Avg('response_time'))['avg'] or 0
    avg_words = ConversationStat.objects.aggregate(avg=Avg('word_count'))['avg'] or 0
    most_active_influencer = Influencer.objects.annotate(cnt=Count('conversationstat')).order_by('-cnt').first()
    most_active_user = ConversationStat.objects.values('user').annotate(cnt=Count('id')).order_by('-cnt').first()
    recent_convos = ConversationStat.objects.order_by('-created_at')[:10]
    
    # Calculate expenses in USD
    gpt_cost = total_tokens / 1000000 * 5  # $5 per 1M tokens for GPT-4o
    elevenlabs_cost = total_credits / 1000000 * 11  # $11 per 1M chars for Creator plan
    total_cost_usd = gpt_cost + elevenlabs_cost
    
    # Exchange rate (1 USD = 1,350 KRW)
    exchange_rate = 1350
    total_cost_krw = total_cost_usd * exchange_rate
    
    # Get unique users this month
    current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    unique_users_this_month = ConversationStat.objects.filter(
        created_at__gte=current_month_start,
        user__isnull=False
    ).values('user').distinct().count()
    
    # Break-even calculations
    break_even_per_user_krw = total_cost_krw / unique_users_this_month if unique_users_this_month > 0 else 0
    break_even_per_chat_krw = total_cost_krw / total_chats if total_chats > 0 else 0
    
    # Projected profit/loss scenarios
    hypothetical_price_per_user = 10000  # 5,000 KRW per user
    hypothetical_price_per_chat = 100   # 100 KRW per chat
    
    projected_profit_per_user = (hypothetical_price_per_user * unique_users_this_month) - total_cost_krw
    projected_profit_per_chat = (hypothetical_price_per_chat * total_chats) - total_cost_krw
    
    return render(request, 'influencers/admin_stats.html', {
        'total_chats': total_chats,
        'total_tokens': total_tokens,
        'total_credits': total_credits,
        'gpt_cost': gpt_cost,
        'elevenlabs_cost': elevenlabs_cost,
        'total_cost_usd': total_cost_usd,
        'total_cost_krw': total_cost_krw,
        'exchange_rate': exchange_rate,
        'unique_users_this_month': unique_users_this_month,
        'break_even_per_user_krw': break_even_per_user_krw,
        'break_even_per_chat_krw': break_even_per_chat_krw,
        'hypothetical_price_per_user': hypothetical_price_per_user,
        'hypothetical_price_per_chat': hypothetical_price_per_chat,
        'projected_profit_per_user': projected_profit_per_user,
        'projected_profit_per_chat': projected_profit_per_chat,
        'avg_response_time': avg_response_time,
        'avg_words': avg_words,
        'most_active_influencer': most_active_influencer,
        'most_active_user': most_active_user,
        'recent_convos': recent_convos,
    })