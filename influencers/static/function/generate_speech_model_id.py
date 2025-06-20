import openai
import os
import time
import json
import random
from tqdm import tqdm
from dotenv import load_dotenv
from unidecode import unidecode
import io

# ✅ .env에서 API 키 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ 메모리에서 JSONL 문자열 생성
def jsonl_from_list(data_list):
    return "\n".join(json.dumps(item, ensure_ascii=False) for item in data_list)

# ✅ 메모리 기반 파일 업로드
def upload_jsonl_from_memory(jsonl_str: str, purpose="fine-tune") -> str:
    file_like = io.BytesIO(jsonl_str.encode("utf-8"))
    res = openai.files.create(file=file_like, purpose=purpose)
    return res.id

# ✅ 파인튜닝 실행 함수
def fine_tune_from_data(data_pairs, influencer_name, model="gpt-4.1-nano-2025-04-14") -> str:
    if len(data_pairs) < 420:
        raise ValueError("❗ data_pairs가 420개 미만입니다. 최소: train 300 + val 120")

    print("🔀 데이터 셔플 및 분할 중...")
    random.shuffle(data_pairs)
    train_data = data_pairs[:300]
    val_data   = data_pairs[300:420]

    print("📤 메모리에서 파일 업로드 중...")
    train_jsonl = jsonl_from_list(train_data)
    val_jsonl   = jsonl_from_list(val_data)

    train_file_id = upload_jsonl_from_memory(train_jsonl)
    val_file_id   = upload_jsonl_from_memory(val_jsonl)

    suffix = unidecode(influencer_name.replace(" ", "_").lower()) + "-style"
    print(f"\n🚀 파인튜닝 시작... ({suffix})")
    job = openai.fine_tuning.jobs.create(
        training_file=train_file_id,
        validation_file=val_file_id,
        model=model,
        suffix=suffix
    )
    job_id = job.id
    print(f"🛠 Job ID: {job_id}")

    print("\n⏳ 학습 진행 모니터링 중...")
    with tqdm(desc="파인튜닝 진행 중", total=100, bar_format="{l_bar}{bar}| {n_fmt}%") as pbar:
        percent = 0
        last_status = None
        while True:
            status = openai.fine_tuning.jobs.retrieve(job_id).status

            if status != last_status:
                tqdm.write(f"📌 상태 변경: {status}")
                last_status = status

            if status == "succeeded":
                pbar.n = 100
                pbar.refresh()
                final_model = openai.fine_tuning.jobs.retrieve(job_id).fine_tuned_model
                print(f"\n🎉 파인튜닝 완료! 모델 ID: {final_model}")
                return final_model
            elif status == "failed":
                raise RuntimeError("❌ 파인튜닝 실패")

            if percent < 95:
                percent += 1
                pbar.update(1)
            time.sleep(60000)
