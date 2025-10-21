#!/usr/bin/env python3
"""
Generate side-by-side comparisons of processed vs unprocessed spectrograms
for key species to demonstrate audio enhancement pipeline effectiveness.
"""

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import glob
from scipy.signal import wiener

# Key species for comparison (showing enhancement benefits)
key_species = [
    ("Graylag_Goose", 2871),
    ("Great_Snipe", 189),
    ("Hooded_Crow", 87),
    ("Common_Crane", 70)
]

audio_dir = '../results/audio_clips/'

def apply_wiener_filter(y, sr, mysize=1024):
    """Apply Wiener filtering to reduce noise"""
    # Work with STFT
    D = librosa.stft(y, n_fft=2048, hop_length=512)
    magnitude = np.abs(D)
    phase = np.angle(D)

    # Apply Wiener filter to each frequency bin
    filtered_magnitude = np.zeros_like(magnitude)
    for i in range(magnitude.shape[0]):
        filtered_magnitude[i, :] = wiener(magnitude[i, :], mysize=min(mysize, len(magnitude[i, :])))

    # Reconstruct
    D_filtered = filtered_magnitude * np.exp(1j * phase)
    y_filtered = librosa.istft(D_filtered, hop_length=512)

    return y_filtered

def apply_hpss(y):
    """Apply Harmonic-Percussive Source Separation"""
    # Separate harmonic (bird calls) from percussive (rain noise)
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    return y_harmonic

for species_name, count in key_species:
    pattern = f"{audio_dir}*{species_name}*.wav"
    files = glob.glob(pattern)

    if not files:
        print(f"No files found for {species_name}")
        continue

    # Use first audio file
    audio_file = sorted(files)[0]
    print(f"Processing {species_name}: {audio_file}")

    # Load audio
    y_raw, sr = librosa.load(audio_file, sr=None)

    # Limit to 4 seconds for visualization
    max_samples = min(len(y_raw), sr * 4)
    y_raw = y_raw[:max_samples]

    # Apply processing pipeline
    y_wiener = apply_wiener_filter(y_raw, sr)
    y_processed = apply_hpss(y_wiener)

    # Create side-by-side comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    species_display = species_name.replace('_', ' ')

    # LEFT: Unprocessed spectrogram
    D_raw = librosa.amplitude_to_db(np.abs(librosa.stft(y_raw)), ref=np.max)
    img1 = librosa.display.specshow(D_raw, y_axis='linear', x_axis='time',
                                     sr=sr, ax=axes[0], cmap='viridis')
    axes[0].set_title(f'{species_display} - UNPROCESSED (Raw)',
                      fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Time (s)', fontsize=12)
    axes[0].set_ylabel('Frequency (Hz)', fontsize=12)
    axes[0].set_ylim(0, 8000)
    fig.colorbar(img1, ax=axes[0], format='%+2.0f dB')

    # RIGHT: Processed spectrogram (Wiener + HPSS)
    D_processed = librosa.amplitude_to_db(np.abs(librosa.stft(y_processed)), ref=np.max)
    img2 = librosa.display.specshow(D_processed, y_axis='linear', x_axis='time',
                                     sr=sr, ax=axes[1], cmap='viridis')
    axes[1].set_title(f'{species_display} - PROCESSED (Wiener + HPSS)',
                      fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Time (s)', fontsize=12)
    axes[1].set_ylabel('Frequency (Hz)', fontsize=12)
    axes[1].set_ylim(0, 8000)
    fig.colorbar(img2, ax=axes[1], format='%+2.0f dB')

    # Overall title
    fig.suptitle(f'{species_display} (n={count}): Audio Enhancement Pipeline Comparison',
                 fontsize=16, fontweight='bold', y=1.02)

    # Save
    output_name = f'figures/comparison_{species_name.lower()}.png'
    plt.tight_layout()
    plt.savefig(output_name, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_name}")

print("\nAll processed vs unprocessed comparisons generated!")
