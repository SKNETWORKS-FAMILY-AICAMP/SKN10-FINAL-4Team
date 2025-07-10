import yt_dlp
import os
import sys
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
import requests
import json
import subprocess
import webrtcvad
import struct
import wave
import librosa
from scipy.spatial.distance import cdist

def extract_transcript(youtube_url):
    """
    유튜브 자막 추출
    """
    print("유튜브 자막 추출 중...")
    
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['ko', 'en'],  # 언어
        'skip_download': True, 
        'quiet': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 정보 가져오기
            info = ydl.extract_info(youtube_url, download=False)
            
            subtitles = info.get('subtitles', {})
            auto_subs = info.get('automatic_captions', {})
            
            # Combine manual and automatic subtitles
            all_subs = {}
            for lang in ['ko', 'en']:
                if lang in subtitles:
                    all_subs[lang] = subtitles[lang]
                elif lang in auto_subs:
                    all_subs[lang] = auto_subs[lang]
            
            if not all_subs:
                print("자막을 찾을 수 없습니다.")
                return None
            
            best_lang = None
            if 'ko' in all_subs:
                best_lang = 'ko'
            elif 'en' in all_subs:
                best_lang = 'en'
            else:
                best_lang = list(all_subs.keys())[0]
            
            print(f"사용 가능한 자막 언어: {list(all_subs.keys())}")
            print(f"선택된 언어: {best_lang}")
            
            # 자막 다운로드
            sub_url = all_subs[best_lang][0]['url']
            subtitle_response = requests.get(sub_url)
            subtitle_response.raise_for_status()
            
            # 자막 파싱 (JSON 형식으로 가정)
            subtitle_data = subtitle_response.json()
            
            # 타임스탬프가 있는 이벤트 추출
            events = subtitle_data.get('events', [])
            transcript = []
            
            for event in events:
                if 'segs' in event:
                    start_time = event.get('tStartMs', 0) / 1000.0  # Convert to seconds
                    end_time = start_time + (event.get('dDurationMs', 0) / 1000.0)
                    
                    # Combine all text segments
                    text = ''
                    for seg in event['segs']:
                        text += seg.get('utf8', '')
                    
                    if text.strip():  # Only add non-empty segments
                        transcript.append({
                            'start': start_time,
                            'end': end_time,
                            'text': text.strip()
                        })
            
            print(f"자막 추출 완료: {len(transcript)}개 세그먼트")
            
            # Print first few segments as preview
            if transcript:
                print("\n자막 미리보기:")
                for i, segment in enumerate(transcript[:3]):
                    print(f"{segment['start']:.1f}s - {segment['end']:.1f}s: {segment['text']}")
                if len(transcript) > 3:
                    print("...")
            
            return transcript
            
    except Exception as e:
        print(f"자막 추출 중 오류 발생: {str(e)}")
        return None

def create_full_text(transcript):
    """
    json 말고 텍스트 
    """
    if not transcript:
        return ""
    
    full_text = " ".join([segment['text'] for segment in transcript])
    
    full_text = " ".join(full_text.split())  # Remove extra whitespace
    
    print(f"추론용 텍스트 생성 완료: {len(full_text)}자")
    print(f"텍스트 미리보기: {full_text[:100]}...")
    
    return full_text

def limit_text_for_2min(text, max_chars=800):
    """
    Limit text to approximately 2 minutes of speech.
    Average speaking rate is about 150-160 words per minute.
    For Korean, approximately 400-500 characters per minute.
    
    Args:
        text: Full text to limit
        max_chars: Maximum characters (approximately 2 minutes)
    
    Returns:
        str: Limited text for 2-minute generation
    """
    if len(text) <= max_chars:
        return text
    
    # Truncate to max_chars and try to end at a sentence boundary
    truncated = text[:max_chars]
    
    # Try to find a good sentence ending
    sentence_endings = ['.', '!', '?', '。', '！', '？']
    last_sentence_end = -1
    
    for ending in sentence_endings:
        pos = truncated.rfind(ending)
        if pos > last_sentence_end:
            last_sentence_end = pos
    
    if last_sentence_end > max_chars * 0.7:  # If we found a sentence end in the last 30%
        limited_text = truncated[:last_sentence_end + 1]
    else:
        # If no good sentence ending, just truncate
        limited_text = truncated
    
    print(f"텍스트 2분 제한 적용: {len(text)}자 -> {len(limited_text)}자")
    print(f"제한된 텍스트 미리보기: {limited_text[:100]}...")
    
    return limited_text

def create_elevenlabs_voice(audio_file, voice_name, api_key):
    """Create Elevenlabs voice model from audio file"""
    url = "https://api.elevenlabs.io/v1/voices/add"
    
    if not os.path.exists(audio_file):
        print(f"오디오 파일 찾을 수 없음: {audio_file}")
        return None
        
    print(f"오디오 파일 사용: {os.path.abspath(audio_file)}")
    
    headers = {
        "xi-api-key": api_key
    }
    
    files = {
        "files": (os.path.basename(audio_file), open(audio_file, "rb"), "audio/mpeg")
    }
    
    data = {
        "name": voice_name,
        "remove_background_noise": "true"
    }
    
    try:
        print("Elevenlabs 모델 생성 중...")
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        
        result = response.json()
        print(f"음성 모델 생성 완료")
        print(f"보이스 ID: {result['voice_id']}")
        print(f"검증 필요: {result['requires_verification']}")
        return result['voice_id']
        
    except requests.exceptions.RequestException as e:
        print(f"일레븐랩스 업로드 오류: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"응답: {e.response.text}")
        return None
    finally:
        files["files"][1].close()

def apply_vad(audio_data, sample_rate, aggressiveness=3, frame_duration=30):
    """
    음성 활동 감지(VAD) 처리
    """
    print("음성 활동 감지(VAD) 처리 중...")
    
    # Initialize VAD
    vad = webrtcvad.Vad(aggressiveness)
    
    # Convert to 16-bit PCM
    audio_int16 = (audio_data * 32767).astype(np.int16)
    
    # Calculate frame size
    frame_size = int(sample_rate * frame_duration / 1000)
    
    # Split audio into frames
    frames = []
    for i in range(0, len(audio_int16), frame_size):
        frame = audio_int16[i:i + frame_size]
        if len(frame) == frame_size:  # Only process complete frames
            frames.append(frame)
    
    # Process frames with VAD
    speech_frames = []
    for frame in frames:
        # Convert frame to bytes
        frame_bytes = frame.tobytes()
        try:
            # Check if frame contains speech
            is_speech = vad.is_speech(frame_bytes, sample_rate)
            if is_speech:
                speech_frames.append(frame)
        except Exception as e:
            print(f"VAD 처리 중 오류 발생: {str(e)}")
            continue
    
    if not speech_frames:
        print("경고: VAD가 음성을 감지하지 못했습니다. 원본 오디오를 사용합니다.")
        return audio_data
    
    # Merge speech frames
    speech_audio = np.concatenate(speech_frames)
    
    # Convert back to float
    speech_audio = speech_audio.astype(np.float32) / 32767.0
    
    # Calculate duration of removed segments
    original_duration = len(audio_data) / sample_rate
    new_duration = len(speech_audio) / sample_rate
    removed_duration = original_duration - new_duration
    
    print(f"VAD 처리 완료:")
    print(f"- 제거된 무음 구간: {removed_duration:.1f}초")
    print(f"- 남은 음성 구간: {new_duration:.1f}초")
    
    return speech_audio

def normalize_audio(audio_data, sample_rate, target_rms=-20, target_peak=-3):
    """Normalize audio volume (-23dB to -18dB RMS, -3dB peak)"""
    # Initialize loudness meter
    meter = pyln.Meter(sample_rate)
    # Calculate current loudness
    current_loudness = meter.integrated_loudness(audio_data)
    # Calculate peak level
    current_peak = np.max(np.abs(audio_data))
    current_peak_db = 20 * np.log10(current_peak)
    # Calculate required gain for RMS normalization
    rms_gain = target_rms - current_loudness
    # Calculate required gain for peak normalization
    peak_gain = target_peak - current_peak_db
    # Use smaller gain to prevent clipping
    gain = min(rms_gain, peak_gain)
    # Apply gain
    normalized_audio = audio_data * (10 ** (gain / 20))
    print(f"음량 정규화 (RMS: {target_rms}dB, 피크: {target_peak}dB) 전처리 완료")
    return normalized_audio

def convert_to_mp3(input_file, output_file, bitrate="128k"):
    """Convert WAV to MP3 using ffmpeg"""
    try:
        command = [
            "ffmpeg", "-y",  # -y to overwrite output file if it exists
            "-i", input_file,
            "-codec:a", "libmp3lame",
            "-b:a", bitrate,
            output_file
        ]
        subprocess.run(command, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"MP3 변환 오류: {str(e)}")
        return False

def process_audio(input_file, transcript=None, output_file="processed_audio.mp3", target_duration=120):
    """Process audio for Elevenlabs IVC requirements"""
    print("메인 오디오 전처리 시작...")
    
    # Verify input file exists
    if not os.path.exists(input_file):
        print(f"오디오 파일 찾을 수 없음: {input_file}")
        return None
    
    print(f"오디오 파일 처리 중: {os.path.abspath(input_file)}")
    
    # Load audio file
    audio_data, sample_rate = sf.read(input_file)
    
    # Convert stereo to mono if needed
    if len(audio_data.shape) > 1:
        print("스테레오 -> 모노로 변환 중...")
        audio_data = np.mean(audio_data, axis=1)
    
    # Trim to 2 minutes if longer
    max_samples = target_duration * sample_rate
    if len(audio_data) > max_samples:
        print(f"오디오 최대 2분으로 자름")
        audio_data = audio_data[:max_samples]
    
    # Apply VAD
    audio_data = apply_vad(audio_data, sample_rate)
    
    # Normalize volume
    normalized_audio = normalize_audio(audio_data, sample_rate)
    
    # Save as temporary WAV file
    temp_wav = "temp_processed.wav"
    sf.write(temp_wav, normalized_audio, sample_rate)
    
    # Convert WAV to MP3
    print("MP3로 변환 중...")
    output_path = os.path.abspath(output_file)
    if not convert_to_mp3(temp_wav, output_path, "128k"):
        return None
    
    # Remove temporary file
    os.remove(temp_wav)
    
    # Check file size
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    if file_size_mb > 11:
        print(f"경고: 파일 크기가 11MB를 초과합니다 ({file_size_mb:.2f}MB)")
        # Try with lower bitrate if file is too large
        print("더 낮은 비트레이트로 다시 시도 중...")
        if not convert_to_mp3(temp_wav, output_path, "96k"):
            return None
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"새 파일 크기: {file_size_mb:.2f}MB")
    
    print(f"처리된 오디오 저장 완료: {output_path}")
    print(f"파일 크기: {file_size_mb:.2f}MB")
    print(f"비트레이트: 128kbps")
    
    return output_path

def download_audio(youtube_url, output_file="raw_audio.wav"):
    """Download audio from YouTube video"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'force_generic_extractor': False
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("비디오 정보 추출 중...")
            ydl.download([youtube_url])
            
        if os.path.exists("temp_audio.wav"):
            output_path = os.path.abspath(output_file)
            os.rename("temp_audio.wav", output_path)
            print(f"오디오 다운로드 완료: {output_path}")
            return output_path
        else:
            print("오디오 파일 생성 실패")
            return None
            
    except yt_dlp.utils.DownloadError as e:
        print(f"다운로드 오류: {str(e)}")
        return None
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return None

def calculate_mcd(original_audio_path, generated_audio_path, sample_rate=22050):
    """
    Calculate Mel-Cepstral Distortion (MCD) between original and generated audio.
    
    Args:
        original_audio_path: Path to original audio file
        generated_audio_path: Path to generated audio file
        sample_rate: Sample rate for processing
    
    Returns:
        float: MCD score (lower is better)
    """
    try:
        print(f"MCD 계산 중...")
        print(f"원본: {original_audio_path}")
        print(f"생성: {generated_audio_path}")
        
        # Load audio files
        original_audio, _ = librosa.load(original_audio_path, sr=sample_rate)
        generated_audio, _ = librosa.load(generated_audio_path, sr=sample_rate)
        
        # Ensure both audios have the same length (use the shorter one)
        min_length = min(len(original_audio), len(generated_audio))
        original_audio = original_audio[:min_length]
        generated_audio = generated_audio[:min_length]
        
        # Extract mel-cepstral coefficients
        original_mel = librosa.feature.melspectrogram(y=original_audio, sr=sample_rate)
        generated_mel = librosa.feature.melspectrogram(y=generated_audio, sr=sample_rate)
        
        # Convert to log scale
        original_log_mel = np.log(original_mel + 1e-8)
        generated_log_mel = np.log(generated_mel + 1e-8)
        
        # Calculate MCD
        mcd = np.mean(np.sqrt(2 * np.sum((original_log_mel - generated_log_mel) ** 2, axis=0)))
        
        print(f"MCD 계산 완료: {mcd:.4f}")
        return mcd
        
    except Exception as e:
        print(f"MCD 계산 중 오류 발생: {str(e)}")
        return float('inf')

def evaluate_model_performance(original_audio_path, generated_audio_path, voice_name):
    """
    Evaluate model performance using MCD.
    
    Args:
        original_audio_path: Path to original processed audio
        generated_audio_path: Path to generated audio
        voice_name: Name of the voice model
    
    Returns:
        dict: Performance metrics
    """
    print(f"\n{'='*50}")
    print(f"모델 성능 평가: {voice_name}")
    print(f"{'='*50}")
    
    if not os.path.exists(original_audio_path):
        print(f"❌ 원본 오디오 파일을 찾을 수 없음: {original_audio_path}")
        return None
    
    if not os.path.exists(generated_audio_path):
        print(f"❌ 생성된 오디오 파일을 찾을 수 없음: {generated_audio_path}")
        return None
    
    # Calculate MCD
    mcd_score = calculate_mcd(original_audio_path, generated_audio_path)
    
    # Get file sizes for additional metrics
    original_size = os.path.getsize(original_audio_path) / (1024 * 1024)  # MB
    generated_size = os.path.getsize(generated_audio_path) / (1024 * 1024)  # MB
    
    # Calculate duration
    original_duration = librosa.get_duration(path=original_audio_path)
    generated_duration = librosa.get_duration(path=generated_audio_path)
    
    performance_metrics = {
        'voice_name': voice_name,
        'original_audio_path': original_audio_path,
        'generated_audio_path': generated_audio_path,
        'mcd_score': mcd_score,
        'original_size_mb': original_size,
        'generated_size_mb': generated_size,
        'original_duration': original_duration,
        'generated_duration': generated_duration,
        'duration_difference': abs(original_duration - generated_duration),
        'size_ratio': generated_size / original_size if original_size > 0 else 0
    }
    
    print(f"성능 지표:")
    print(f"  - MCD 점수: {mcd_score:.4f}")
    print(f"  - 원본 크기: {original_size:.2f}MB")
    print(f"  - 생성 크기: {generated_size:.2f}MB")
    print(f"  - 원본 길이: {original_duration:.2f}초")
    print(f"  - 생성 길이: {generated_duration:.2f}초")
    print(f"  - 길이 차이: {abs(original_duration - generated_duration):.2f}초")
    
    return performance_metrics

def cleanup_generated_files(results, keep_best_only=False):
    """
    Clean up generated audio files after MCD evaluation.
    
    Args:
        results: List of results from voice creation and evaluation
        keep_best_only: If True, keep only the best model's files
    """
    print("생성된 파일 정리 중...")
    
    files_to_remove = []
    
    for result in results:
        if result['status'] == 'success':
            # Remove generated audio files
            if result['generated_audio_path'] and os.path.exists(result['generated_audio_path']):
                files_to_remove.append(result['generated_audio_path'])
            
            # Remove processed audio files (original training audio)
            processed_audio = f"processed_audio_{result['voice_name']}.mp3"
            if os.path.exists(processed_audio):
                files_to_remove.append(processed_audio)
    
    # If keeping best only, identify the best model
    if keep_best_only and results:
        valid_results = [r for r in results if r['status'] == 'success' and r['performance_metrics']]
        if valid_results:
            best_result = min(valid_results, key=lambda x: x['performance_metrics']['mcd_score'])
            
            # Remove best model's files from cleanup list
            if best_result['generated_audio_path'] in files_to_remove:
                files_to_remove.remove(best_result['generated_audio_path'])
            
            processed_audio = f"processed_audio_{best_result['voice_name']}.mp3"
            if processed_audio in files_to_remove:
                files_to_remove.remove(processed_audio)
            
            print(f"최고 모델 파일 보존: {best_result['voice_name']}")
    
    # Remove files
    for file_path in files_to_remove:
        try:
            os.remove(file_path)
            print(f"삭제됨: {file_path}")
        except Exception as e:
            print(f"파일 삭제 실패: {file_path} - {str(e)}")
    
    print(f"파일 정리 완료: {len(files_to_remove)}개 파일 삭제됨")

def find_best_model(performance_results):
    """
    Find the best model based on MCD scores.
    
    Args:
        performance_results: List of performance metrics dictionaries
    
    Returns:
        dict: Best model information with voice_id
    """
    if not performance_results:
        print("❌ 평가할 모델이 없습니다.")
        return None
    
    # Filter out failed evaluations
    valid_results = [r for r in performance_results if r is not None and r['mcd_score'] != float('inf')]
    
    if not valid_results:
        print("❌ 유효한 MCD 점수가 없습니다.")
        return None
    
    # Sort by MCD score (lower is better)
    sorted_results = sorted(valid_results, key=lambda x: x['mcd_score'])
    
    best_model = sorted_results[0]
    
    print(f"\n{'='*60}")
    print("모델 선정 완료")
    print(f"{'='*60}")
    print(f"최고 모델: {best_model['voice_name']}")
    print(f"Voice ID: {best_model['voice_id']}")
    print(f"MCD 점수: {best_model['mcd_score']:.4f}")
    print(f"원본 오디오: {best_model['original_audio_path']}")
    print(f"생성된 오디오: {best_model['generated_audio_path']}")
    
    print(f"\n전체 모델 순위 (MCD 기준):")
    for i, result in enumerate(sorted_results, 1):
        print(f"{i}. {result['voice_name']} (ID: {result['voice_id']}): {result['mcd_score']:.4f}")
    
    print(f"{'='*60}")
    
    return best_model

def generate_audio_with_elevenlabs(voice_id, text, api_key, output_file="generated_audio.mp3"):
    """
    Generate audio using Elevenlabs voice model with given text.
    
    Args:
        voice_id: Elevenlabs voice ID
        text: Text to synthesize
        api_key: Elevenlabs API key
        output_file: Output MP3 file name
    
    Returns:
        str: Path to generated audio file if successful, None otherwise
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Limit text to 2 minutes
    limited_text = limit_text_for_2min(text)
    
    data = {
        "text": limited_text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        print(f"Elevenlabs 음성 추론 중... (Voice ID: {voice_id})")
        print(f"텍스트: {limited_text[:100]}...")
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        # Save the audio
        output_path = os.path.abspath(output_file)
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        # Get file size
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        
        print(f"음성 합성 완료: {output_path}")
        print(f"파일 크기: {file_size_mb:.2f}MB")
        
        return output_path
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Elevenlabs 음성 합성 오류: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"응답: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ 음성 합성 중 오류 발생: {str(e)}")
        return None

def create_voice_and_evaluate(youtube_url, voice_name, api_key):
    """
    Create voice model, generate audio, and evaluate performance.
    Returns voice_id, generated audio path, and performance metrics.
    """
    print(f"\n{'='*60}")
    print(f"개별 Voice 모델 생성 및 성능 평가: {voice_name}")
    print(f"{'='*60}")
    
    # Extract transcript
    transcript = extract_transcript(youtube_url)
    if not transcript:
        print("❌ 자막을 찾을 수 없어 처리를 건너뜁니다.")
        return None, None, None
    
    # Create full text
    full_text = create_full_text(transcript)
    if not full_text:
        print("❌ 텍스트를 생성할 수 없어 처리를 건너뜁니다.")
        return None, None, None
    
    # Download audio
    raw_audio = download_audio(youtube_url)
    if not raw_audio:
        return None, None, None
    
    # Process audio with voice-specific filename
    processed_audio = f"processed_audio_{voice_name}.mp3"
    processed_audio = process_audio(raw_audio, transcript, processed_audio)
    if not processed_audio:
        return None, None, None
    
    # Create voice model
    voice_id = create_elevenlabs_voice(processed_audio, voice_name, api_key)
    if not voice_id:
        return None, None, None
    
    # Generate audio using the model
    generated_audio_path = generate_audio_with_elevenlabs(
        voice_id=voice_id,
        text=full_text,
        api_key=api_key,
        output_file=f"generated_{voice_name}.mp3"
    )
    
    # Evaluate performance
    performance_metrics = None
    if generated_audio_path:
        performance_metrics = evaluate_model_performance(
            processed_audio, generated_audio_path, voice_name
        )
        # Add voice_id to performance metrics
        if performance_metrics:
            performance_metrics['voice_id'] = voice_id
    
    # Cleanup
    if os.path.exists(raw_audio):
        os.remove(raw_audio)
    
    return voice_id, generated_audio_path, performance_metrics

def create_multiple_voices_and_evaluate(youtube_urls, voice_names, api_key):
    """
    Create multiple voices, generate audio, and evaluate performance for each.
    
    Args:
        youtube_urls: list of YouTube URLs
        voice_names: list of voice names
        api_key: Elevenlabs API key
    
    Returns:
        tuple: (results, best_model) where best_model contains voice_id
    """
    if len(youtube_urls) != len(voice_names):
        print("❌ 오류: YouTube URL 수와 Voice Name 수가 일치하지 않습니다.")
        return [], None
    
    results = []
    performance_results = []
    
    for i, (youtube_url, voice_name) in enumerate(zip(youtube_urls, voice_names), 1):
        print(f"\n{'='*60}")
        print(f"처리 중: {i}/{len(youtube_urls)}")
        print(f"URL: {youtube_url}")
        print(f"Voice Name: {voice_name}")
        print(f"{'='*60}")
        
        try:
            voice_id, generated_audio_path, performance_metrics = create_voice_and_evaluate(
                youtube_url, voice_name, api_key
            )
            
            if voice_id:
                results.append({
                    'voice_id': voice_id,
                    'voice_name': voice_name,
                    'youtube_url': youtube_url,
                    'generated_audio_path': generated_audio_path,
                    'performance_metrics': performance_metrics,
                    'status': 'success',
                    'index': i
                })
                
                if performance_metrics:
                    performance_results.append(performance_metrics)
                
                print(f"성공: {voice_name} (ID: {voice_id})")
                if generated_audio_path:
                    print(f"🎵 생성된 오디오: {generated_audio_path}")
                if performance_metrics:
                    print(f"MCD 점수: {performance_metrics['mcd_score']:.4f}")
            else:
                results.append({
                    'voice_id': None,
                    'voice_name': voice_name,
                    'youtube_url': youtube_url,
                    'generated_audio_path': None,
                    'performance_metrics': None,
                    'status': 'failed',
                    'index': i
                })
                print(f"❌ 실패: {voice_name}")
                
        except Exception as e:
            results.append({
                'voice_id': None,
                'voice_name': voice_name,
                'youtube_url': youtube_url,
                'generated_audio_path': None,
                'performance_metrics': None,
                'status': 'error',
                'error': str(e),
                'index': i
            })
            print(f"❌ 오류 발생: {voice_name} - {str(e)}")
    
    # Find best model
    best_model = find_best_model(performance_results)
    
    # Clean up generated files (keep only the best model's files)
    cleanup_generated_files(results, keep_best_only=True)
    
    # Print summary
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] != 'success']
    
    print(f"\n{'='*60}")
    print("배치 처리 완료 요약:")
    print(f"총 처리: {len(results)}개")
    print(f"성공: {len(successful)}개")
    print(f"실패: {len(failed)}개")
    
    if successful:
        print("\n성공한 Voice 모델들:")
        for result in successful:
            print(f"- {result['voice_name']}: {result['voice_id']}")
            if result['performance_metrics']:
                print(f"  MCD: {result['performance_metrics']['mcd_score']:.4f}")
    
    if best_model:
        print(f"\n 최고 성능 모델: {best_model['voice_name']}")
        print(f"   Voice ID: {best_model['voice_id']}")
        print(f"   MCD 점수: {best_model['mcd_score']:.4f}")
    
    print(f"{'='*60}")
    
    return results, best_model