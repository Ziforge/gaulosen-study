#!/usr/bin/env python3
"""
Generate Spectrograms for Best Detections (Highest Confidence per Species)
Creates detailed spectrogram images for the top detections
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import soundfile as sf
import os
from pathlib import Path

print("=" * 80)
print("🌟 GENERATING SPECTROGRAMS FOR BEST DETECTIONS")
print("=" * 80)
print()

# Configuration
AUDIO_DIR = "/Users/georgeredpath/Dev/Gaulossen-recordings/audio_files"
ALL_DETECTIONS = "results/all_detections_with_weather.csv"
OUTPUT_DIR = "results/spectrograms_best"
SAMPLE_RATE = 22050
N_FFT = 2048
HOP_LENGTH = 512

# Number of best detections per species
TOP_N_PER_SPECIES = 3  # Top 3 highest confidence per species

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("📊 Configuration:")
print(f"   Audio directory: {AUDIO_DIR}")
print(f"   All detections CSV: {ALL_DETECTIONS}")
print(f"   Output directory: {OUTPUT_DIR}")
print(f"   Top detections per species: {TOP_N_PER_SPECIES}")
print()

# Load all detections
print("📥 Loading all detections with weather...")
df = pd.read_csv(ALL_DETECTIONS)
print(f"   Total detections: {len(df):,}")
print(f"   Unique species: {df['common_name'].nunique()}")
print()

# Get top N detections per species (highest confidence)
print("🔍 Selecting best detections per species...")
best_detections = df.groupby('common_name').apply(
    lambda x: x.nlargest(TOP_N_PER_SPECIES, 'confidence')
).reset_index(drop=True)

print(f"   Selected {len(best_detections)} best detections across {best_detections['common_name'].nunique()} species")
print()

# Also get top 50 overall highest confidence
print("🏆 Adding top 50 highest confidence overall...")
top_overall = df.nlargest(50, 'confidence')
combined = pd.concat([best_detections, top_overall]).drop_duplicates()
print(f"   Total detections to process: {len(combined)}")
print()

# Group by audio file
combined_grouped = combined.groupby('filename')

print("🎵 Generating spectrograms...")
print("-" * 80)

spectrogram_count = 0
species_processed = set()

for audio_filename, detections in combined_grouped:
    # Find audio file in subdirectories
    audio_path = None
    for date_dir in os.listdir(AUDIO_DIR):
        potential_path = os.path.join(AUDIO_DIR, date_dir, audio_filename)
        if os.path.exists(potential_path):
            audio_path = potential_path
            break

    if not audio_path:
        print(f"   ⚠️  Audio file not found: {audio_filename}")
        continue

    print(f"\n   📄 Processing: {audio_filename}")
    print(f"      Detections in this file: {len(detections)}")
    print(f"      Loading audio...")

    try:
        # Load entire audio file
        y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)
        duration = len(y) / sr
        print(f"      Audio loaded: {duration/3600:.2f} hours")

        # Process each detection
        for idx, row in detections.iterrows():
            start_time = row['start_s']
            end_time = row['end_s']
            species = row['common_name']
            confidence = row['confidence']
            weather = row.get('weather_summary', 'N/A')

            species_processed.add(species)

            # Add 1 second context
            context_start = max(0, start_time - 1.0)
            context_end = min(duration, end_time + 1.0)

            # Extract segment
            start_sample = int(context_start * sr)
            end_sample = int(context_end * sr)
            segment = y[start_sample:end_sample]

            if len(segment) == 0:
                continue

            # Generate spectrogram
            fig, axes = plt.subplots(2, 1, figsize=(14, 9))

            # Top panel: Waveform
            ax1 = axes[0]
            times = np.linspace(context_start, context_end, len(segment))
            ax1.plot(times, segment, linewidth=0.5, color='steelblue', alpha=0.8)
            ax1.axvline(x=start_time, color='red', linestyle='--', linewidth=2, label='Detection')
            ax1.axvline(x=end_time, color='red', linestyle='--', linewidth=2)
            ax1.fill_between([start_time, end_time], ax1.get_ylim()[0], ax1.get_ylim()[1],
                           alpha=0.2, color='red')
            ax1.set_xlabel('Time (s)', fontsize=11)
            ax1.set_ylabel('Amplitude', fontsize=11)
            ax1.set_title(f'Waveform - {species} (Confidence: {confidence:.3f})',
                         fontsize=13, fontweight='bold')
            ax1.legend(loc='upper right', fontsize=10)
            ax1.grid(True, alpha=0.3)

            # Bottom panel: Spectrogram
            ax2 = axes[1]
            D = librosa.amplitude_to_db(
                np.abs(librosa.stft(segment, n_fft=N_FFT, hop_length=HOP_LENGTH)),
                ref=np.max
            )

            img = librosa.display.specshow(
                D,
                sr=sr,
                hop_length=HOP_LENGTH,
                x_axis='time',
                y_axis='hz',
                ax=ax2,
                cmap='magma'
            )

            # Mark detection boundaries
            detection_start_frame = int((start_time - context_start) * sr / HOP_LENGTH)
            detection_end_frame = int((end_time - context_start) * sr / HOP_LENGTH)

            ax2.axvline(x=detection_start_frame * HOP_LENGTH / sr, color='cyan',
                       linestyle='--', linewidth=2, alpha=0.8, label='Detection window')
            ax2.axvline(x=detection_end_frame * HOP_LENGTH / sr, color='cyan',
                       linestyle='--', linewidth=2, alpha=0.8)

            # Typical bird frequency range
            ax2.axhline(y=1000, color='yellow', linestyle=':', linewidth=1, alpha=0.4)
            ax2.axhline(y=8000, color='yellow', linestyle=':', linewidth=1, alpha=0.4)

            ax2.set_xlabel('Time (s)', fontsize=11)
            ax2.set_ylabel('Frequency (Hz)', fontsize=11)
            ax2.set_title(f'Spectrogram - {species}', fontsize=13, fontweight='bold')
            ax2.set_ylim([0, 12000])
            ax2.legend(loc='upper right', fontsize=9)

            # Colorbar
            cbar = fig.colorbar(img, ax=ax2, format='%+2.0f dB')
            cbar.set_label('Amplitude (dB)', fontsize=10)

            # Enhanced metadata
            metadata_text = (
                f"📁 File: {row['file_stem']}\n"
                f"📅 Date: {row['recording_date']}\n"
                f"⏰ Time: {row['absolute_timestamp']}\n"
                f"🌦️  Weather: {weather}\n"
                f"🔊 Confidence: {confidence:.3f}\n"
                f"⏱️  Duration: {end_time - start_time:.2f}s\n"
                f"🎵 Freq: {row.get('Low Freq (Hz)', 'N/A')} - {row.get('High Freq (Hz)', 'N/A')} Hz"
            )

            fig.text(0.02, 0.98, metadata_text, transform=fig.transFigure,
                    fontsize=9, verticalalignment='top', family='monospace',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

            plt.tight_layout(rect=[0, 0, 1, 0.96])

            # Save spectrogram
            safe_species = species.replace(' ', '_').replace('/', '-')
            conf_str = f"{confidence:.3f}".replace('.', '')
            output_filename = f"{row['file_stem']}_{safe_species}_{int(start_time)}s_conf{conf_str}.png"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            spectrogram_count += 1
            print(f"      ✅ {safe_species} ({confidence:.3f}) at {start_time:.1f}s")

    except Exception as e:
        print(f"      ❌ Error: {e}")
        continue

print()
print("=" * 80)
print("✅ BEST DETECTIONS SPECTROGRAM GENERATION COMPLETE")
print("=" * 80)
print()

print(f"📊 Summary:")
print(f"   Total spectrograms generated: {spectrogram_count}")
print(f"   Unique species: {len(species_processed)}")
print(f"   Output directory: {OUTPUT_DIR}")
print()

print(f"🏆 Top species processed:")
for species in sorted(species_processed)[:20]:
    print(f"   - {species}")
if len(species_processed) > 20:
    print(f"   ... and {len(species_processed) - 20} more")
print()

print(f"🎯 To review:")
print(f"   open {OUTPUT_DIR}")
print()
