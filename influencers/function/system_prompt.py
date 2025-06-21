from yt_dlp import YoutubeDL
import requests
import re

# 이모지 제거 함수
def remove_emojis(text):
    emoji_pattern = re.compile("[\U00010000-\U0010FFFF]+", flags=re.UNICODE)
    return emoji_pattern.sub("", text)

# 🔍 인플루언서 배경 정보 검색 (web 용)
def search_influencer_background(name: str, TAVILY_API_KEY: str) -> str:
    tavily_url = "https://api.tavily.com/search"
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    data = {
        "query": f"{name} 인플루언서 특징 및 활동 분야",
        "search_depth": "basic",
        "include_answer": True,
        "include_raw_content": False
    }

    response = requests.post(tavily_url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json().get("answer", "검색된 정보 없음")
    else:
        return "Tavily 검색 실패"

# 🎞️ 유튜브 영상 메타데이터 추출
def extract_video_info(video_url: str):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'forcejson': True
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return {
            "title": info.get("title", "제목 없음"),
            "uploader": info.get("uploader", "알 수 없음"),
            "description": info.get("description", "설명 없음")
        }

# 📋 관점 적용 LLM용 system prompt 생성 (web 용)
def build_prompt_generalized(name: str, channel: str, video_title: str, video_description: str, background_info: str) -> str:
    if name.lower() not in channel.lower():
        channel_note = (
            f"⚠️ 참고: 이 영상은 '{name}'의 공식 채널이 아닐 수 있습니다. "
            f"클립 영상일 가능성을 염두에 두고, 아래 정보들을 기반으로 일반적인 활동 특징을 추론해 주세요.\n\n"
        )
    else:
        channel_note = ""

    return (
        f"'{name}'이라는 인플루언서의 관점을 따르는 LLM용 시스템 프롬프트를 작성해주세요.\n\n"
        f"{channel_note}"
        f"이 인플루언서는 유튜브 채널 '{channel}'에서 활동합니다.\n\n"
        f"아래 영상은 이 인플루언서의 대표 콘텐츠 중 하나입니다:\n"
        f"- 영상 제목: {video_title}\n"
        f"- 영상 설명: {video_description[:400]}...\n\n"
        f"또한, 웹 검색 결과에 따르면 이 인플루언서는 다음과 같은 특징을 가지고 있습니다:\n"
        f"{background_info}\n\n"
        f"이 정보들을 단서로 삼아, 이 인플루언서가 일반적으로 어떤 주제와 관점을 가지고 활동하는지를 추론해 주세요.\n"
        f"해당 인플루언서를 GPT가 이미 알고 있다고 가정하고, 내장된 배경지식도 함께 활용해서 system prompt를 생성해 주세요.\n\n"
        f"⚠️ 아래 조건을 충실히 반영해주세요:\n"
        f"- 이 인플루언서가 주로 다루는 콘텐츠 주제와 중요하게 여기는 관점 또는 평가 기준을 반영해서 응답하도록 유도하세요.\n"
        f"- 응답은 정보 중심적이고 객관적이어야 하며,\n"
        f"  문장마다 줄바꿈(개행)을 해서 각각의 정보가 분리되어 보이도록 작성하세요.\n"
        f"- 반드시 2~3문장으로 간결하게 요약될 수 있도록 유도해야 합니다.\n"
        f"- “감탄사, 말투, 구어체 표현은 절대 포함하지 말고 응답하세요.”라는 내용을 반드시 포함시키세요.\n"
        f"- 프롬프트는 반드시 “당신은 OO입니다.”로 시작해주세요.\n\n"
        f"이제 '{name}'에 대해 생성해 주세요:"
    )

def generator_feature_system_prompt(video_url: str, influencer_name: str, TAVILY_API_KEY: str, client) -> str:
    video_info = extract_video_info(video_url)
    background = search_influencer_background(influencer_name, TAVILY_API_KEY)
    prompt_web = build_prompt_generalized(
        influencer_name, video_info["uploader"], video_info["title"], video_info["description"], background
    )
    feature_system_prompt = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "너는 AI 프롬프트 엔지니어야."},
            {"role": "user", "content": prompt_web}
        ]
    ).choices[0].message.content.strip()

    return feature_system_prompt

# 📌 말투 적용 LLM용 시스템 프롬프트 생성 (말투 반영 용)
def generator_speech_system_prompt(video_url: str, influencer_name: str, TAVILY_API_KEY: str, client) -> str:
    video_info = extract_video_info(video_url)
    background_info = search_influencer_background(influencer_name, TAVILY_API_KEY)

    context = (
        f"[인플루언서 이름]: {influencer_name}\n"
        f"[채널명]: {video_info['uploader']}\n"
        f"[영상 제목]: {video_info['title']}\n"
        f"[영상 설명]: {video_info['description'][:300]}...\n"
        f"[Tavily 기반 배경 정보]: {background_info}\n\n"
        f"위 정보를 바탕으로 {influencer_name}의 말투 특징을 bullet 형식으로 설명해주세요.\n"
        f"- 어투, 말버릇, 표현 스타일 중심\n"
        f"- 이모티콘은 절대 사용하지 마세요\n"
        f"- 최대한 자연스럽고 구체적인 예시도 포함해주세요."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 유튜버 말투 분석 전문가입니다."},
            {"role": "user", "content": context}
        ],
        temperature=0.5,
        max_tokens=600
    )

    style_description = remove_emojis(response.choices[0].message.content.strip())
    print(style_description)

    return (
        f"당신은 인플루언서 {influencer_name}의 말투로 바꿔주는 말투 변환기입니다.\n"
        f"질문에 대해 답변을 하지 않고, 내용 그대로를 말투로 변환해주세요.\n"
        f"{influencer_name} 특유의 말투 스타일을 자연스럽게 반영해 주세요.\n\n"
        f"{influencer_name} 말투의 특징은 다음과 같습니다:\n"
        f"{style_description}\n\n"
        f"단, 말이 어색하거나 과장되지 않도록 자연스럽게 말투를 적용하세요."
    )