from .ivc_prepare import create_voice_from_youtube
from .system_prompt import generator_feature_system_prompt, generator_speech_system_prompt
from .generate_sft_data import generate_sft_data_from_example_video
from .generate_speech_model_id import fine_tune_from_data
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

client = OpenAI()

def generate_voiceid(youtube_url, influencer_name):
    # Your logic to generate a voice ID from YouTube
    voice_id = create_voice_from_youtube(
        youtube_url=youtube_url, # 유튜브 오디오 URL    
        voice_name=influencer_name, # 음성 모델 이름
        api_key=ELEVENLABS_API_KEY # Elevenlabs API 키
    )
    
    if voice_id:
        print(f"파이프라인 완료")
        print(f"Voice ID: {voice_id}")
        print("--------------------------------")
    else:
        print("파이프라인 실패")
        print("--------------------------------")
    
    # return voice_id
    return voice_id

def generate_speech_model_id(youtube_url, name):
    # Your logic to generate a model ID
    train_data = generate_sft_data_from_example_video(youtube_url, name, TAVILY_API_KEY, client)

    speech_model_id = fine_tune_from_data(train_data, name)
    return speech_model_id

def generate_prompts(youtube_url, name):
    # Your logic to generate prompts
    feature_system_prompt = generator_feature_system_prompt(youtube_url, name, TAVILY_API_KEY, client)

    speech_system_prompt = generator_speech_system_prompt(youtube_url, name, TAVILY_API_KEY, client)
    return feature_system_prompt, speech_system_prompt