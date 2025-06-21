from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL
import re
import requests
from urllib.parse import urlparse, parse_qs

def remove_emojis(text):
    try:
        emoji_pattern = re.compile("[\U00010000-\U0010FFFF]+", flags=re.UNICODE)
        return emoji_pattern.sub("", text)
    except re.error:
        fallback = re.compile("[\u2600-\u26FF\u2700-\u27BF]+", flags=re.UNICODE)
        return fallback.sub("", text)

def extract_video_id(url):
    query = parse_qs(urlparse(url).query)
    return query.get("v", [""])[0]

def get_influencer_tone(influencer_name, TAVILY_API_KEY, client):
    query = f"{influencer_name} 말투 스타일 특징"
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    res = requests.post("https://api.tavily.com/search", json={"query": query}, headers=headers)
    passages = res.json().get("results", [])
    source_info = "\n".join(p.get("content", "") for p in passages[:2])

    prompt = (
        f"다음 정보를 바탕으로 '{influencer_name}'의 말투 특징을 요약해 주세요.\n"
        f"- 핵심 어투, 말버릇, 표현 방식 중심\n"
        f"- 이모티콘은 절대 사용하지 마세요\n\n"
        f"{source_info}"
    )

    response = client(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "인플루언서 말투를 요약하는 전문가입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
    )
    return remove_emojis(response.choices[0].message.content.strip())

def get_transcript(video_id):
    for lang in ["ko", "a.ko", "en", "a.en"]:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
            return " ".join([item['text'] for item in transcript])
        except:
            continue
    print(f"⚠️ 자막 추출 실패: {video_id}")
    return ""

def refine_sentences_with_gpt(transcript_text, client):
    prompt = (
        "다음 텍스트는 유튜브 자막입니다. 문장 단위로 자연스럽게 정제해 주세요.\n"
        "- 한 문장씩 줄바꿈\n- 비문 제거\n- 반복 제거\n- 자연스러운 구어체 표현\n- 이모티콘은 절대 사용하지 마세요\n\n"
        f"{transcript_text}"
    )
    response = client(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "자막을 정제하는 AI입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
    )
    cleaned = response.choices[0].message.content.strip().split("\n")
    return [remove_emojis(s.strip()) for s in cleaned if len(s.strip()) > 5]

def refine_sentences_safely(transcript_text, client, max_chunk_chars=1500):
    chunks = [transcript_text[i:i + max_chunk_chars] for i in range(0, len(transcript_text), max_chunk_chars)]
    results = []
    for idx, chunk in enumerate(chunks):
        print(f"문장 정제 중... (chunk {idx + 1}/{len(chunks)})")
        try:
            refined = refine_sentences_with_gpt(chunk, client)
            results.extend(refined)
        except Exception as e:
            print(f"⚠️ 정제 실패 (chunk {idx + 1}): {e}")
            continue
    return results

def generate_styled_response(influencer_name, style_description, text_sample, client):
    prompt = (
        f"아래 텍스트를 참고해 '{influencer_name}'의 말투로 응답을 만들어 주세요.\n"
        f"말투 특징:\n{style_description}\n\n텍스트:\n{text_sample}\n\n→ 스타일 응답:"
    )
    response = client(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "인플루언서 말투를 재현하는 AI입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
    )
    return remove_emojis(response.choices[0].message.content.strip())

def generate_user_question(assistant_response, client):
    prompt = (
        f"다음은 AI의 답변입니다. 이 답변에 어울리는 자연스럽고 짧은 질문을 하나 만들어 주세요.\n"
        f"- 구체적으로 시작\n- 일상적 말투\n- 이모티콘 금지\n\nAssistant: \"{assistant_response}\"\nUser:"
    )
    response = client(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "user 질문을 생성하는 AI입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
    )
    return remove_emojis(response.choices[0].message.content.strip())

def generate_sft_dataset(influencer_name, video_urls, TAVILY_API_KEY, client, limit=420):
    print("말투 특징 수집 중...")
    style_desc = get_influencer_tone(influencer_name, TAVILY_API_KEY, client)

    data_pairs = []
    for url in video_urls:
        video_id = extract_video_id(url)
        if not video_id:
            continue

        print(f"자막 추출 중: {video_id}")
        transcript = get_transcript(video_id)
        if not transcript:
            continue

        print("문장 정제 중...")
        refined = refine_sentences_safely(transcript, client)
        refined = [s for s in refined if len(s) < 300]
        for s in refined:
            try:
                print(f"스타일 응답 생성 중... 문장 길이: {len(s)}")
                a = generate_styled_response(influencer_name, style_desc, s, client)
                print("질문 생성 중...")
                u = generate_user_question(a, client)
                data_pairs.append({
                    "messages": [
                        {"role": "user", "content": u},
                        {"role": "assistant", "content": a}
                    ]
                })
                if len(data_pairs) >= limit:
                    print("목표 도달! 중단.")
                    return data_pairs
                print(f"현재 데이터 수: {len(data_pairs)}")
            except Exception as e:
                print(f"⚠️ 실패: {e}")
        if len(data_pairs) >= limit:
            break
    return data_pairs

def get_channel_url_from_video(video_url):
    ydl_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info.get("channel_url")

def get_video_ids_from_channel(channel_url, max_videos=20):
    if "/videos" not in channel_url:
        channel_url += "/videos"
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'no_warnings': True,
        'dump_single_json': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        data = ydl.extract_info(channel_url, download=False)
        if "entries" in data:
            return [entry['id'] for entry in data['entries'][:max_videos] if 'id' in entry]
        return []

def generate_sft_data_from_example_video(example_video_url, influencer_name, TAVILY_API_KEY, client, max_videos=5):
    print(f"채널 추출 중...")
    channel_url = get_channel_url_from_video(example_video_url)
    print(f"채널 URL: {channel_url}")
    print(f"영상 ID 추출 중...")
    video_ids = get_video_ids_from_channel(channel_url, max_videos=max_videos)
    full_video_urls = [f"https://www.youtube.com/watch?v={vid}" for vid in video_ids]
    print(f"총 {len(full_video_urls)}개 영상 확보됨")

    return generate_sft_dataset(influencer_name, full_video_urls, TAVILY_API_KEY, client)