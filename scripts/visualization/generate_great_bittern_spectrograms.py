#!/usr/bin/env python3
"""
Generate Raven Pro-style spectrograms for ALL Great Bittern audio clips.
This creates high-quality visualizations for manual verification.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import librosa
import librosa.display
from scipy import signal
import warnings
warnings.filterwarnings('ignore')

# Paths
AUDIO_DIR = Path("results/audio_clips_enhanced")
OUTPUT_DIR = Path("results/spectrograms_great_bittern")
OUTPUT_DIR.mkdir(exist_ok=True)

# Raven Pro-style settings
SAMPLE_RATE = 44100
N_FFT = 2048
HOP_LENGTH = 512
FREQ_MAX = 12000  # Hz

def create_raven_style_spectrogram(audio_path, output_path):
    """Create Raven Pro-style spectrogram"""

    # Load audio
    y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)

    # Apply pre-emphasis to boost high frequencies (like Raven Pro)
    y = librosa.effects.preemphasis(y, coef=0.97)

    # Compute spectrogram
    D = librosa.stft(y, n_fft=N_FFT, hop_length=HOP_LENGTH, window='hamming')
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

    # Create figure with Raven Pro styling
    fig, ax = plt.subplots(figsize=(14, 6), facecolor='black')

    # Plot spectrogram with hot colormap (Raven Pro default)
    img = librosa.display.specshow(
        S_db,
        sr=sr,
        hop_length=HOP_LENGTH,
        x_axis='time',
        y_axis='hz',
        cmap='hot',
        ax=ax,
        vmin=-80,
        vmax=0
    )

    # Set frequency range
    ax.set_ylim([0, FREQ_MAX])

    # Styling to match Raven Pro
    ax.set_facecolor('black')
    ax.set_xlabel('Time (s)', color='white', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency (Hz)', color='white', fontsize=12, fontweight='bold')
    ax.tick_params(colors='white', labelsize=10)

    # Add filename as title
    filename = audio_path.stem
    ax.set_title(f'{filename}', color='white', fontsize=14, fontweight='bold', pad=15)

    # Add colorbar
    cbar = plt.colorbar(img, ax=ax, format='%+2.0f dB')
    cbar.ax.tick_params(colors='white', labelsize=10)
    cbar.set_label('Amplitude (dB)', color='white', fontsize=11, fontweight='bold')

    # Grid
    ax.grid(True, color='gray', alpha=0.3, linestyle='-', linewidth=0.5)

    # Tight layout
    plt.tight_layout()

    # Save with high DPI
    plt.savefig(output_path, dpi=150, facecolor='black', edgecolor='none', bbox_inches='tight')
    plt.close()


def main():
    """Generate spectrograms for all Great Bittern audio files"""

    print("=" * 80)
    print("GREAT BITTERN SPECTROGRAM GENERATION")
    print("=" * 80)
    print()

    # Find all Great Bittern audio files
    audio_files = sorted(AUDIO_DIR.glob("*Great_Bittern*.wav"))

    print(f"Found {len(audio_files)} Great Bittern audio files")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    # Generate spectrograms
    for i, audio_path in enumerate(audio_files, 1):
        output_path = OUTPUT_DIR / f"{audio_path.stem}.png"

        if output_path.exists():
            print(f"[{i:3d}/{len(audio_files)}] SKIP {audio_path.name} (exists)")
        else:
            print(f"[{i:3d}/{len(audio_files)}] Creating spectrogram: {audio_path.name}")
            try:
                create_raven_style_spectrogram(audio_path, output_path)
                print(f"              → Saved: {output_path.name}")
            except Exception as e:
                print(f"              ✗ ERROR: {e}")

        if i % 10 == 0:
            print()

    print()
    print("=" * 80)
    print(f"COMPLETE: {len(list(OUTPUT_DIR.glob('*.png')))} spectrograms generated")
    print("=" * 80)


if __name__ == "__main__":
    main()
