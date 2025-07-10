from elevenlabs import stream
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import os

# Initialize ElevenLabs client
elevenlabs = ElevenLabs(
    api_key='',
)

# Create output directory if it doesn't exist
output_dir = "itsub_benchmark"
os.makedirs(output_dir, exist_ok=True)

# List of diverse sentences with varying emotions
sentences = [
  {
    "text": "와! 정말 대박이다! 이건 꼭 해봐야 해!",
    "filename": "excited.mp3"
  },
  {
    "text": "죄송합니다. 제가 실수했네요. 다시 한번 기회를 주시겠어요?",
    "filename": "apologetic.mp3"
  },
  {
    "text": "이건 정말 중요한 문제예요. 신중하게 생각해봐야 할 것 같아요.",
    "filename": "serious.mp3"
  },
  {
    "text": "하하하! 너무 웃겨서 어쩔 줄 모르겠어요!",
    "filename": "laughing.mp3"
  },
  {
    "text": "정말 힘들었어요... 하지만 이겨냈어요.",
    "filename": "emotional.mp3"
  },
  {
    "text": "이건 정말 놀라운 발견이에요. 여러분도 한번 확인해보세요.",
    "filename": "surprised.mp3"
  },
  {
    "text": "음... 이건 좀 생각해봐야 할 것 같아요.",
    "filename": "thoughtful.mp3"
  },
  {
    "text": "제발 도와주세요! 정말 급한 상황이에요!",
    "filename": "urgent.mp3"
  },
  {
    "text": "휴... 드디어 끝났네요. 정말 힘들었어요.",
    "filename": "relieved.mp3"
  },
  {
    "text": "와우! 이건 정말 멋진 기회예요!",
    "filename": "enthusiastic.mp3"
  },
  {
    "text": "이건 믿을 수 없는 일이에요! (11)",
    "filename": "excited_11.mp3"
  },
  {
    "text": "정말 죄송해요. 실수였어요. (12)",
    "filename": "apologetic_12.mp3"
  },
  {
    "text": "심각하게 받아들여야 할 문제네요. (13)",
    "filename": "serious_13.mp3"
  },
  {
    "text": "너무 재밌어서 배꼽이 빠질 뻔했어요! (14)",
    "filename": "laughing_14.mp3"
  },
  {
    "text": "감정이 북받쳐 올라요. (15)",
    "filename": "emotional_15.mp3"
  },
  {
    "text": "상상도 못한 일이에요! (16)",
    "filename": "surprised_16.mp3"
  },
  {
    "text": "좀 더 생각해볼게요. (17)",
    "filename": "thoughtful_17.mp3"
  },
  {
    "text": "지금 당장 도와주세요! (18)",
    "filename": "urgent_18.mp3"
  },
  {
    "text": "이제 끝났다는 게 믿기지 않아요. (19)",
    "filename": "relieved_19.mp3"
  },
  {
    "text": "이건 평생 한 번뿐인 기회예요! (20)",
    "filename": "enthusiastic_20.mp3"
  },
  {
    "text": "이건 믿을 수 없는 일이에요! (21)",
    "filename": "excited_21.mp3"
  },
  {
    "text": "정말 죄송해요. 실수였어요. (22)",
    "filename": "apologetic_22.mp3"
  },
  {
    "text": "심각하게 받아들여야 할 문제네요. (23)",
    "filename": "serious_23.mp3"
  },
  {
    "text": "너무 재밌어서 배꼽이 빠질 뻔했어요! (24)",
    "filename": "laughing_24.mp3"
  },
  {
    "text": "감정이 북받쳐 올라요. (25)",
    "filename": "emotional_25.mp3"
  },
  {
    "text": "상상도 못한 일이에요! (26)",
    "filename": "surprised_26.mp3"
  },
  {
    "text": "좀 더 생각해볼게요. (27)",
    "filename": "thoughtful_27.mp3"
  },
  {
    "text": "지금 당장 도와주세요! (28)",
    "filename": "urgent_28.mp3"
  },
  {
    "text": "이제 끝났다는 게 믿기지 않아요. (29)",
    "filename": "relieved_29.mp3"
  },
  {
    "text": "이건 평생 한 번뿐인 기회예요! (30)",
    "filename": "enthusiastic_30.mp3"
  },
  {
    "text": "이건 믿을 수 없는 일이에요! (31)",
    "filename": "excited_31.mp3"
  },
  {
    "text": "정말 죄송해요. 실수였어요. (32)",
    "filename": "apologetic_32.mp3"
  },
  {
    "text": "심각하게 받아들여야 할 문제네요. (33)",
    "filename": "serious_33.mp3"
  },
  {
    "text": "너무 재밌어서 배꼽이 빠질 뻔했어요! (34)",
    "filename": "laughing_34.mp3"
  },
  {
    "text": "감정이 북받쳐 올라요. (35)",
    "filename": "emotional_35.mp3"
  },
  {
    "text": "상상도 못한 일이에요! (36)",
    "filename": "surprised_36.mp3"
  },
  {
    "text": "좀 더 생각해볼게요. (37)",
    "filename": "thoughtful_37.mp3"
  },
  {
    "text": "지금 당장 도와주세요! (38)",
    "filename": "urgent_38.mp3"
  },
  {
    "text": "이제 끝났다는 게 믿기지 않아요. (39)",
    "filename": "relieved_39.mp3"
  },
  {
    "text": "이건 평생 한 번뿐인 기회예요! (40)",
    "filename": "enthusiastic_40.mp3"
  },
  {
    "text": "이건 믿을 수 없는 일이에요! (41)",
    "filename": "excited_41.mp3"
  },
  {
    "text": "정말 죄송해요. 실수였어요. (42)",
    "filename": "apologetic_42.mp3"
  },
  {
    "text": "심각하게 받아들여야 할 문제네요. (43)",
    "filename": "serious_43.mp3"
  },
  {
    "text": "너무 재밌어서 배꼽이 빠질 뻔했어요! (44)",
    "filename": "laughing_44.mp3"
  },
  {
    "text": "감정이 북받쳐 올라요. (45)",
    "filename": "emotional_45.mp3"
  },
  {
    "text": "상상도 못한 일이에요! (46)",
    "filename": "surprised_46.mp3"
  },
  {
    "text": "좀 더 생각해볼게요. (47)",
    "filename": "thoughtful_47.mp3"
  },
  {
    "text": "지금 당장 도와주세요! (48)",
    "filename": "urgent_48.mp3"
  },
  {
    "text": "이제 끝났다는 게 믿기지 않아요. (49)",
    "filename": "relieved_49.mp3"
  },
  {
    "text": "이건 평생 한 번뿐인 기회예요! (50)",
    "filename": "enthusiastic_50.mp3"
  },
  {
    "text": "이건 믿을 수 없는 일이에요! (51)",
    "filename": "excited_51.mp3"
  },
  {
    "text": "정말 죄송해요. 실수였어요. (52)",
    "filename": "apologetic_52.mp3"
  },
  {
    "text": "심각하게 받아들여야 할 문제네요. (53)",
    "filename": "serious_53.mp3"
  },
  {
    "text": "너무 재밌어서 배꼽이 빠질 뻔했어요! (54)",
    "filename": "laughing_54.mp3"
  },
  {
    "text": "감정이 북받쳐 올라요. (55)",
    "filename": "emotional_55.mp3"
  },
  {
    "text": "상상도 못한 일이에요! (56)",
    "filename": "surprised_56.mp3"
  },
  {
    "text": "좀 더 생각해볼게요. (57)",
    "filename": "thoughtful_57.mp3"
  },
  {
    "text": "지금 당장 도와주세요! (58)",
    "filename": "urgent_58.mp3"
  },
  {
    "text": "이제 끝났다는 게 믿기지 않아요. (59)",
    "filename": "relieved_59.mp3"
  },
  {
    "text": "이건 평생 한 번뿐인 기회예요! (60)",
    "filename": "enthusiastic_60.mp3"
  },
  {
    "text": "이건 믿을 수 없는 일이에요! (61)",
    "filename": "excited_61.mp3"
  },
  {
    "text": "정말 죄송해요. 실수였어요. (62)",
    "filename": "apologetic_62.mp3"
  },
  {
    "text": "심각하게 받아들여야 할 문제네요. (63)",
    "filename": "serious_63.mp3"
  },
  {
    "text": "너무 재밌어서 배꼽이 빠질 뻔했어요! (64)",
    "filename": "laughing_64.mp3"
  },
  {
    "text": "감정이 북받쳐 올라요. (65)",
    "filename": "emotional_65.mp3"
  },
  {
    "text": "상상도 못한 일이에요! (66)",
    "filename": "surprised_66.mp3"
  },
  {
    "text": "좀 더 생각해볼게요. (67)",
    "filename": "thoughtful_67.mp3"
  },
  {
    "text": "지금 당장 도와주세요! (68)",
    "filename": "urgent_68.mp3"
  },
  {
    "text": "이제 끝났다는 게 믿기지 않아요. (69)",
    "filename": "relieved_69.mp3"
  },
  {
    "text": "이건 평생 한 번뿐인 기회예요! (70)",
    "filename": "enthusiastic_70.mp3"
  },
  {
    "text": "이건 믿을 수 없는 일이에요! (71)",
    "filename": "excited_71.mp3"
  },
  {
    "text": "정말 죄송해요. 실수였어요. (72)",
    "filename": "apologetic_72.mp3"
  },
  {
    "text": "심각하게 받아들여야 할 문제네요. (73)",
    "filename": "serious_73.mp3"
  },
  {
    "text": "너무 재밌어서 배꼽이 빠질 뻔했어요! (74)",
    "filename": "laughing_74.mp3"
  },
  {
    "text": "감정이 북받쳐 올라요. (75)",
    "filename": "emotional_75.mp3"
  },
  {
    "text": "상상도 못한 일이에요! (76)",
    "filename": "surprised_76.mp3"
  },
  {
    "text": "좀 더 생각해볼게요. (77)",
    "filename": "thoughtful_77.mp3"
  },
  {
    "text": "지금 당장 도와주세요! (78)",
    "filename": "urgent_78.mp3"
  },
  {
    "text": "이제 끝났다는 게 믿기지 않아요. (79)",
    "filename": "relieved_79.mp3"
  },
  {
    "text": "이건 평생 한 번뿐인 기회예요! (80)",
    "filename": "enthusiastic_80.mp3"
  },
  {
    "text": "이건 믿을 수 없는 일이에요! (81)",
    "filename": "excited_81.mp3"
  },
  {
    "text": "정말 죄송해요. 실수였어요. (82)",
    "filename": "apologetic_82.mp3"
  },
  {
    "text": "심각하게 받아들여야 할 문제네요. (83)",
    "filename": "serious_83.mp3"
  },
  {
    "text": "너무 재밌어서 배꼽이 빠질 뻔했어요! (84)",
    "filename": "laughing_84.mp3"
  },
  {
    "text": "감정이 북받쳐 올라요. (85)",
    "filename": "emotional_85.mp3"
  },
  {
    "text": "상상도 못한 일이에요! (86)",
    "filename": "surprised_86.mp3"
  },
  {
    "text": "좀 더 생각해볼게요. (87)",
    "filename": "thoughtful_87.mp3"
  },
  {
    "text": "지금 당장 도와주세요! (88)",
    "filename": "urgent_88.mp3"
  },
  {
    "text": "이제 끝났다는 게 믿기지 않아요. (89)",
    "filename": "relieved_89.mp3"
  },
  {
    "text": "이건 평생 한 번뿐인 기회예요! (90)",
    "filename": "enthusiastic_90.mp3"
  },
  {
    "text": "이건 믿을 수 없는 일이에요! (91)",
    "filename": "excited_91.mp3"
  },
  {
    "text": "정말 죄송해요. 실수였어요. (92)",
    "filename": "apologetic_92.mp3"
  },
  {
    "text": "심각하게 받아들여야 할 문제네요. (93)",
    "filename": "serious_93.mp3"
  },
  {
    "text": "너무 재밌어서 배꼽이 빠질 뻔했어요! (94)",
    "filename": "laughing_94.mp3"
  },
  {
    "text": "감정이 북받쳐 올라요. (95)",
    "filename": "emotional_95.mp3"
  },
  {
    "text": "상상도 못한 일이에요! (96)",
    "filename": "surprised_96.mp3"
  },
  {
    "text": "좀 더 생각해볼게요. (97)",
    "filename": "thoughtful_97.mp3"
  },
  {
    "text": "지금 당장 도와주세요! (98)",
    "filename": "urgent_98.mp3"
  },
  {
    "text": "이제 끝났다는 게 믿기지 않아요. (99)",
    "filename": "relieved_99.mp3"
  },
  {
    "text": "이건 평생 한 번뿐인 기회예요! (100)",
    "filename": "enthusiastic_100.mp3"
  }
]

# Generate and save audio for each sentence
for sentence in sentences:
    print(f"Generating audio for: {sentence['text']}")
    
    try:
        # Generate audio
        audio = elevenlabs.text_to_speech.convert(
            text=sentence["text"],
            voice_id="plOtwiwqx7nYT1lHEYwM",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        
        # Save the audio file
        output_path = os.path.join(output_dir, sentence["filename"])
        
        # Convert generator to bytes and save
        audio_bytes = b"".join(chunk for chunk in audio)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        
        print(f"Successfully saved to: {output_path}")
        
    except Exception as e:
        print(f"Error generating audio for '{sentence['text']}': {str(e)}")

print("\nAll audio files have been generated and saved in the 'final_processed' directory.")