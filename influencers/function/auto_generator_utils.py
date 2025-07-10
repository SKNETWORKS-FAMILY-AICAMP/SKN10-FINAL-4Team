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

def generate_voice_names(person_name, url_count):
    """
    Automatically generate voice names based on person name and URL count.
    
    Args:
        person_name: Name of the person
        url_count: Number of YouTube URLs
    
    Returns:
        list: Generated voice names
    """
    voice_names = []
    for i in range(url_count):
        voice_names.append(f"{person_name}_voice_{i+1}")
    return voice_names

def run_ivc_pipeline_with_evaluation():
    """
    Run IVC pipeline with voice model creation and MCD evaluation.
    This function creates voice models from multiple YouTube URLs and evaluates their performance.
    """
    print("🎤 IVC Pipeline - Voice Model Creation and MCD Evaluation")
    print("=" * 60)
    
    # Validate configuration
    if not API_KEY or API_KEY == "your_elevenlabs_api_key_here":
        print("❌ API_KEY를 설정해주세요.")
        print("ivc_pipeline.py 파일에서 API_KEY 변수를 수정하세요.")
        return
    
    if len(YOUTUBE_URLS) == 0:
        print("❌ 오류: YOUTUBE_URLS가 비어있습니다.")
        return
    
    # Auto-generate voice names
    voice_names = generate_voice_names(PERSON_NAME, len(YOUTUBE_URLS))
    
    print(f"설정된 YouTube URL들:")
    for i, (url, name) in enumerate(zip(YOUTUBE_URLS, voice_names), 1):
        print(f"{i}. {name}: {url}")
    
    print(f"\n🔄 {len(YOUTUBE_URLS)}개 모델 생성 및 성능 평가 시작...")
    print("MCD (Mel-Cepstral Distortion) 점수로 모델 성능을 평가합니다.")
    print("   (낮은 점수가 더 좋은 성능을 의미합니다)")
    
    # Run batch processing and evaluation
    results, best_model = create_multiple_voices_and_evaluate(
        YOUTUBE_URLS, voice_names, API_KEY
    )
    
    if results:
        successful = [r for r in results if r['status'] == 'success']
        print(f"\n성공: {len(successful)}/{len(results)}개")
        
        if best_model:
  
            print(f"\n{'='*60}")
            print("MCD 평가 완료!")
            print("=" * 60)
            
            # Return the best model ID for further use
            return best_model['voice_id']
    
    print(f"\n{'='*60}")
    print("MCD 평가 완료!")
    print("=" * 60)
    return None

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