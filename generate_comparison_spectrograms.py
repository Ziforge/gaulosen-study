#!/usr/bin/env python3
"""
Generate comparison spectrograms for audio enhancement pipeline.
Finds pairs of unprocessed/enhanced audio and creates side-by-side visualizations.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from pathlib import Path

# Paths
AUDIO_UNPROCESSED = Path("/Users/georgeredpath/Dev/mcp-pipeline/shared/gaulossen/results/audio_clips")
AUDIO_ENHANCED = Path("/Users/georgeredpath/Dev/mcp-pipeline/shared/gaulossen/results/audio_clips_enhanced")
OUTPUT_DIR = Path("/Users/georgeredpath/Dev/mcp-pipeline/shared/gaulossen/gaulosen_study/export/figures")

# Spectrogram parameters (Raven Pro conventions)
FFT_SIZE = 2048
HOP_LENGTH = 512
SR = 48000  # AudioMoth sampling rate

def load_audio(filepath):
    """Load audio file and return waveform."""
    y, sr = librosa.load(filepath, sr=SR)
    return y, sr

def create_spectrogram(y, sr, ax, title):
    """Create spectrogram on given axes."""
    # Compute STFT
    D = librosa.stft(y, n_fft=FFT_SIZE, hop_length=HOP_LENGTH)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

    # Plot
    img = librosa.display.specshow(
        S_db,
        sr=sr,
        hop_length=HOP_LENGTH,
        x_axis='time',
        y_axis='hz',
        ax=ax,
        cmap='viridis',
        vmin=-80,
        vmax=0
    )
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency (Hz)', fontsize=10)
    ax.set_xlabel('Time (s)', fontsize=10)
    ax.set_ylim(0, 8000)  # Focus on bird vocalization range

    return img

def create_comparison(species, filename_base, detection_count):
    """Create side-by-side comparison for a species."""
    # Find matching files
    unprocessed_wav = AUDIO_UNPROCESSED / f"{filename_base}.wav"
    enhanced_wav = AUDIO_ENHANCED / f"{filename_base}.wav"

    if not unprocessed_wav.exists() or not enhanced_wav.exists():
        print(f"Missing files for {species}: {filename_base}")
        return False

    # Load audio
    y_raw, sr_raw = load_audio(unprocessed_wav)
    y_enhanced, sr_enhanced = load_audio(enhanced_wav)

    # Ensure same length
    min_len = min(len(y_raw), len(y_enhanced))
    y_raw = y_raw[:min_len]
    y_enhanced = y_enhanced[:min_len]

    # Create figure
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f'{species} (n={detection_count}): Audio Enhancement Pipeline Comparison',
                 fontsize=14, fontweight='bold')

    # Left: Unprocessed
    img1 = create_spectrogram(y_raw, sr_raw, axes[0], f'{species} - UNPROCESSED (Raw)')

    # Right: Enhanced
    img2 = create_spectrogram(y_enhanced, sr_enhanced, axes[1], f'{species} - PROCESSED (Wiener + HPSS)')

    # Add colorbars
    cbar1 = plt.colorbar(img1, ax=axes[0], format='%+2.0f dB')
    cbar2 = plt.colorbar(img2, ax=axes[1], format='%+2.0f dB')

    plt.tight_layout()

    # Save
    output_file = OUTPUT_DIR / f"comparison_{species.lower().replace(' ', '_').replace('-', '_')}.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"✓ Created: {output_file.name}")
    return True

def main():
    """Generate comparison spectrograms for key species."""

    # Target species with high-confidence detections
    # Format: (species_name, filename_base, detection_count)
    species_list = [
        ("Graylag Goose", "2025-10-13_11h37m_Graylag_Goose_17643s_conf0991", 2871),
        ("Great Snipe", "2025-10-13_11h37m_Great_Snipe_31848s_conf0957", 189),
        ("Common Crane", "2025-10-13_11h37m_Common_Crane_13119s_conf0653", 70),
        ("Pink-footed Goose", "2025-10-13_11h37m_Pink-footed_Goose_11715s_conf0785", 189),
        ("Hooded Crow", "2025-10-13_11h37m_Hooded_Crow_3852s_conf0740", 87),
        ("Yellowhammer", "2025-10-13_11h37m_Yellowhammer_13440s_conf0831", 51),
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating comparison spectrograms...")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    success_count = 0
    for species, filename_base, count in species_list:
        if create_comparison(species, filename_base, count):
            success_count += 1

    print()
    print(f"Generated {success_count}/{len(species_list)} comparison spectrograms")

if __name__ == "__main__":
    main()
