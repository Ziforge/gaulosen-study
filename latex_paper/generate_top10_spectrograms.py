#!/usr/bin/env python3
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import glob

# Top 10 species based on detection counts
top_species = [
    ("Graylag_Goose", 2871),
    ("Pink-footed_Goose", 189),
    ("Great_Snipe", 189),
    ("Hooded_Crow", 87),
    ("Carrion_Crow", 84),
    ("Greater_White-fronted_Goose", 71),
    ("Common_Crane", 70),
    ("Eurasian_Woodcock", 57),
    ("Canada_Goose", 47),
    ("Rook", 45)
]

audio_dir = '../results/audio_clips/'

for species_name, count in top_species:
    # Find audio files for this species
    pattern = f"{audio_dir}*{species_name}*.wav"
    files = glob.glob(pattern)

    if not files:
        print(f"No files found for {species_name}")
        continue

    # Use the first file (or highest confidence if sorting)
    audio_file = sorted(files)[0]
    print(f"Processing {species_name}: {audio_file}")

    try:
        # Load audio
        y, sr = librosa.load(audio_file, sr=None)

        # Create figure
        fig, ax = plt.subplots(figsize=(8, 4))

        # Generate spectrogram
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        img = librosa.display.specshow(D, y_axis='linear', x_axis='time', sr=sr, ax=ax, cmap='viridis')

        # Formatting
        species_display = species_name.replace('_', ' ')
        ax.set_title(f'{species_display} (n={count})', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time (s)', fontsize=12)
        ax.set_ylabel('Frequency (Hz)', fontsize=12)
        ax.set_ylim(0, 8000)  # Focus on bird vocalization range

        # Add colorbar
        fig.colorbar(img, ax=ax, format='%+2.0f dB')

        # Save
        output_name = f'figures/spectrogram_{species_name.lower()}.png'
        plt.tight_layout()
        plt.savefig(output_name, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  → Saved: {output_name}")

    except Exception as e:
        print(f"  ERROR: {e}")

print("\nAll spectrograms generated!")
