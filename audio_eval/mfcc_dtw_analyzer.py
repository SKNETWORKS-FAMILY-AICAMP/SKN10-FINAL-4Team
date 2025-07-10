import sys
import os
import numpy as np
import librosa
import matplotlib.pyplot as plt
from librosa.sequence import dtw
import seaborn as sns
from matplotlib import font_manager
import pandas as pd
from scipy import stats

# Add Korean font support
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

def load_audio(file_path):
    # Load mp3 and convert to wav-like array
    wav, sr = librosa.load(file_path, sr=None)
    # Use 16kHz for consistency
    if sr != 16000:
        wav = librosa.resample(wav, orig_sr=sr, target_sr=16000)
        sr = 16000
    # Trim leading and trailing silence
    wav, _ = librosa.effects.trim(wav)
    return wav, sr

def compute_mean_mfcc(files, n_mfcc=13):
    mfccs = []
    for file in files:
        wav, sr = load_audio(file)
        mfcc = librosa.feature.mfcc(y=wav, sr=sr, n_mfcc=n_mfcc)
        mfcc_mean = np.mean(mfcc, axis=1)
        mfccs.append(mfcc_mean)
    if mfccs:
        return np.mean(mfccs, axis=0)
    else:
        return np.zeros(n_mfcc)

def main():
    group_dirs = {
        "ElevenLabs": "ElevenLabs",
        "Supertones": "supertones",
        "Benchmark": "benchmark"
    }
    n_mfcc = 8  # To match the style in the provided image
    group_mfcc_means = {}

    for group, dir_path in group_dirs.items():
        files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith('.mp3')]
        print(f"{group}: {len(files)} files")
        group_mfcc_means[group] = compute_mean_mfcc(files, n_mfcc=n_mfcc)

    # Plotting
    x = np.arange(1, n_mfcc + 1)
    width = 0.2
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = [
        '#A020F0',  # Purple for ElevenLabs
        '#228B22',  # Green for Supertones
        '#FFD700'   # Yellow for Benchmark
    ]
    labels = list(group_dirs.keys())
    for i, group in enumerate(labels):
        ax.bar(x + (i - 1) * width, group_mfcc_means[group], width=width, label=group, color=colors[i])

    ax.set_xlabel('MFCC Coefficient')
    ax.set_ylabel('Mean Value')
    ax.set_title('Mean MFCC Vector by Group')
    ax.set_xticks(x)
    ax.set_xticklabels([f'MFCC {i}' for i in x])
    ax.legend()
    plt.tight_layout()
    plt.savefig('mean_mfcc_by_group.png', dpi=300)
    plt.close()
    print("Saved mean MFCC plot as 'mean_mfcc_by_group.png'")

if __name__ == "__main__":
    main() 