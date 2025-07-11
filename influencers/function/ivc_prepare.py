import yt_dlp
import os
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
import requests
import subprocess
import webrtcvad

# 일레븐랩스 모델 생성
def create_elevenlabs_voice(audio_file, voice_name, api_key):
    url = "https://api.elevenlabs.io/v1/voices/add"
    
    # 파일 존재하는지 확인
    if not os.path.exists(audio_file):
        print(f"정제된 오디오 파일 찾을 수 없음: {audio_file}")
        return None
        
    print(f"정제된 오디오 파일 사용: {os.path.abspath(audio_file)}")
    
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
        print("Elevenlabs IVC 모델 생성 중...")
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        
        result = response.json()
        print(f"IVC 음성 모델 생성 완료")
        # print(f"보이스 ID: {result['voice_id']}")
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
    Apply Voice Activity Detection to remove non-speech segments.
    
    Args:
        audio_data: numpy array of audio data
        sample_rate: sample rate of the audio
        aggressiveness: VAD aggressiveness (0-3)
        frame_duration: frame duration in ms (10, 20, or 30)
    
    Returns:
        numpy array containing only speech segments
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

# 음량 정규화 (-23dB, -3dB)
def normalize_audio(audio_data, sample_rate, target_rms=-20, target_peak=-3):
    # 음량 미터 초기화
    meter = pyln.Meter(sample_rate)
    # 현재 음량 계산
    current_loudness = meter.integrated_loudness(audio_data)
    # 피크 레벨 계산
    current_peak = np.max(np.abs(audio_data))
    current_peak_db = 20 * np.log10(current_peak)
    # RMS 정규화를 위한 필요한 게인 계산
    rms_gain = target_rms - current_loudness
    # 피크 정규화를 위한 필요한 게인 계산
    peak_gain = target_peak - current_peak_db
    # 클리핑을 방지하기 위해 작은 게인 사용
    gain = min(rms_gain, peak_gain)
    # 게인 적용
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

# 오디오 처리 (2분 제한)
def process_audio(input_file, output_file="processed_audio.mp3", target_duration=120):
    print("오디오 전처리 시작...")
    
    # Verify input file exists
    if not os.path.exists(input_file):
        print(f"오디오 파일 찾을 수 없음: {input_file}")
        return None
    
    print(f"오디오 파일 처리 중: {os.path.abspath(input_file)}")
    
    # 오디오 파일 로드
    audio_data, sample_rate = sf.read(input_file)
    
    # 스테레오인 경우 모노로 변환
    if len(audio_data.shape) > 1:
        print("스테레오 -> 모노로 변환 중...")
        audio_data = np.mean(audio_data, axis=1)
    
    # 2분 초과 시 2분으로 자름
    max_samples = target_duration * sample_rate
    if len(audio_data) > max_samples:
        print(f"오디오 최대 2분으로 자름")
        audio_data = audio_data[:max_samples]
    
    # VAD 적용
    audio_data = apply_vad(audio_data, sample_rate)
    
    # 음량 정규화
    normalized_audio = normalize_audio(audio_data, sample_rate)
    
    # 임시 WAV 파일로 저장
    temp_wav = "temp_processed.wav"
    sf.write(temp_wav, normalized_audio, sample_rate)
    
    # WAV를 MP3로 변환
    print("MP3로 변환 중...")
    output_path = os.path.abspath(output_file)
    if not convert_to_mp3(temp_wav, output_path, "128k"):
        return None
    
    # 임시 파일 삭제
    os.remove(temp_wav)
    
    # 파일 크기 확인
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    if file_size_mb > 11:
        print(f"경고: 파일 크기가 11MB를 초과합니다 ({file_size_mb:.2f}MB)")
        # 파일 크기가 너무 크면 더 낮은 비트레이트로 다시 시도
        print("더 낮은 비트레이트로 다시 시도 중...")
        if not convert_to_mp3(temp_wav, output_path, "96k"):
            return None
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"새 파일 크기: {file_size_mb:.2f}MB")
    
    print(f"처리된 오디오 저장 완료: {output_path}")
    print(f"파일 크기: {file_size_mb:.2f}MB")
    print(f"비트레이트: 128kbps")
    
    return output_path

# 유튜브 오디오 다운로드
def download_audio(youtube_url, output_file="raw_audio.wav"):
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
            print("유튜브 비디오 정보 추출 중...")
            ydl.download([youtube_url])
            
        if os.path.exists("temp_audio.wav"):
            output_path = os.path.abspath(output_file)
            os.rename("temp_audio.wav", output_path)
            print(f"유튜브 오디오 다운로드 완료: {output_path}")
            return output_path
        else:
            print("유튜브 오디오 다운로드 실패")
            return None
            
    except yt_dlp.utils.DownloadError as e:
        print(f"다운로드 오류: {str(e)}")
        return None
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return None

def create_voice_from_youtube(youtube_url, voice_name, api_key):
    # 유튜브 오디오에서 Elevenlabs 음성 모델 생성

    # 오디오 다운로드
    raw_audio = download_audio(youtube_url)
    if not raw_audio:
        return None
    
    # 오디오 처리
    processed_audio = process_audio(raw_audio)
    if not processed_audio:
        return None
    
    # 음성 모델 생성
    voice_id = create_elevenlabs_voice(processed_audio, voice_name, api_key)

    # 정리
    if os.path.exists(processed_audio) and os.path.exists(raw_audio):
        os.remove(processed_audio)
        os.remove(raw_audio)
    
    return voice_id