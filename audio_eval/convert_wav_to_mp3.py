from pydub import AudioSegment
import os

input_dir = "supertones"
output_dir = "supertones_mp3"
os.makedirs(output_dir, exist_ok=True)

for fname in os.listdir(input_dir):
    if fname.endswith(".wav"):
        wav_path = os.path.join(input_dir, fname)
        mp3_name = os.path.splitext(fname)[0] + ".mp3"
        mp3_path = os.path.join(output_dir, mp3_name)
        audio = AudioSegment.from_wav(wav_path)
        audio.export(mp3_path, format="mp3")
        print(f"Converted: {wav_path} -> {mp3_path}")

print("All conversions complete.") 