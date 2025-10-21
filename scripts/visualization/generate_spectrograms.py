#!/usr/bin/env python3
"""
Generate Individual Spectrograms for High-Priority Detections
Creates detailed spectrogram images for manual review
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
print("🎵 GENERATING INDIVIDUAL SPECTROGRAMS FOR HIGH-PRIORITY DETECTIONS")
print("=" * 80)
print()

# Configuration
AUDIO_DIR = "/Users/georgeredpath/Dev/Gaulosen-recordings/audio_files"
HP_CSV = "results/python_raven_automated/high_priority_enhanced.csv"
OUTPUT_DIR = "results/spectrograms_high_priority"
SAMPLE_RATE = 22050  # Downsample for faster processing
N_FFT = 2048
HOP_LENGTH = 512

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("📊 Configuration:")
print(f"   Audio directory: {AUDIO_DIR}")
print(f"   High priority CSV: {HP_CSV}")
print(f"   Output directory: {OUTPUT_DIR}")
print(f"   Sample rate: {SAMPLE_RATE} Hz")
print()

# Load high priority detections
print("📥 Loading high priority detections...")
df = pd.read_csv(HP_CSV)
print(f"   Found {len(df)} detections to process\n")

# Group by audio file
df_grouped = df.groupby('Begin File')

print("🎵 Generating spectrograms...")
print("-" * 80)

spectrogram_count = 0

for audio_file, detections in df_grouped:
    # Try to find audio file in subdirectories
    audio_path = None

    # Try direct path first
    direct_path = os.path.join(AUDIO_DIR, audio_file)
    if os.path.exists(direct_path):
        audio_path = direct_path
    else:
        # Search in date subdirectories
        for date_dir in os.listdir(AUDIO_DIR):
            potential_path = os.path.join(AUDIO_DIR, date_dir, audio_file)
            if os.path.exists(potential_path):
                audio_path = potential_path
                break

    if not audio_path:
        print(f"   ⚠️  Audio file not found: {audio_file}")
        continue

    print(f"\n   📄 Processing: {audio_file}")
    print(f"      Loading audio... (may take a minute for large files)")

    try:
        # Load entire audio file
        y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)
        duration = len(y) / sr
        print(f"      Audio loaded: {duration/3600:.2f} hours, {sr} Hz")

        # Process each detection
        for idx, row in detections.iterrows():
            start_time = row['Begin Time (s)']
            end_time = row['End Time (s)']
            species = row['Common Name']
            confidence = row['Confidence']

            # Add 1 second before and after for context
            context_start = max(0, start_time - 1.0)
            context_end = min(duration, end_time + 1.0)

            # Extract segment
            start_sample = int(context_start * sr)
            end_sample = int(context_end * sr)
            segment = y[start_sample:end_sample]

            if len(segment) == 0:
                print(f"      ⚠️  Empty segment for {species} at {start_time:.1f}s")
                continue

            # Generate spectrogram
            fig, axes = plt.subplots(2, 1, figsize=(12, 8))

            # Top panel: Waveform
            ax1 = axes[0]
            times = np.linspace(context_start, context_end, len(segment))
            ax1.plot(times, segment, linewidth=0.5, color='steelblue')
            ax1.axvline(x=start_time, color='red', linestyle='--', label='Detection start')
            ax1.axvline(x=end_time, color='red', linestyle='--', label='Detection end')
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Amplitude')
            ax1.set_title(f'Waveform - {species} (Confidence: {confidence:.3f})')
            ax1.legend(loc='upper right')
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
                cmap='viridis'
            )

            # Adjust x-axis to show actual time
            num_frames = D.shape[1]
            time_labels = np.linspace(context_start, context_end, num_frames)

            # Mark detection boundaries
            detection_start_frame = int((start_time - context_start) * sr / HOP_LENGTH)
            detection_end_frame = int((end_time - context_start) * sr / HOP_LENGTH)

            ax2.axvline(x=detection_start_frame * HOP_LENGTH / sr, color='red',
                       linestyle='--', linewidth=2, alpha=0.7)
            ax2.axvline(x=detection_end_frame * HOP_LENGTH / sr, color='red',
                       linestyle='--', linewidth=2, alpha=0.7)

            # Mark BirdNET frequency range
            ax2.axhline(y=500, color='yellow', linestyle=':', linewidth=1, alpha=0.5, label='BirdNET range')
            ax2.axhline(y=10000, color='yellow', linestyle=':', linewidth=1, alpha=0.5)

            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Frequency (Hz)')
            ax2.set_title(f'Spectrogram - {species}')
            ax2.set_ylim([0, 12000])  # Focus on bird frequency range

            # Add colorbar
            cbar = fig.colorbar(img, ax=ax2, format='%+2.0f dB')
            cbar.set_label('Amplitude (dB)')

            # Add metadata
            metadata_text = (
                f"File: {audio_file}\n"
                f"Time: {start_time:.2f} - {end_time:.2f}s\n"
                f"Duration: {end_time - start_time:.2f}s\n"
                f"Confidence: {confidence:.3f}\n"
                f"Low Freq: {row['Low Freq (Hz)']:.0f} Hz\n"
                f"High Freq: {row['High Freq (Hz)']:.0f} Hz\n"
                f"Bandwidth: {row['bandwidth']:.0f} Hz"
            )

            fig.text(0.02, 0.98, metadata_text, transform=fig.transFigure,
                    fontsize=9, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

            plt.tight_layout(rect=[0, 0, 1, 0.96])

            # Save spectrogram
            safe_species = species.replace(' ', '_').replace('/', '-')
            output_filename = f"{Path(audio_file).stem}_{safe_species}_{start_time:.0f}s.png"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            spectrogram_count += 1
            print(f"      ✅ {safe_species} at {start_time:.1f}s → {output_filename}")

    except Exception as e:
        print(f"      ❌ Error processing {audio_file}: {e}")
        continue

print()
print("=" * 80)
print("✅ SPECTROGRAM GENERATION COMPLETE")
print("=" * 80)
print()

print(f"📊 Summary:")
print(f"   Total spectrograms generated: {spectrogram_count}")
print(f"   Output directory: {OUTPUT_DIR}")
print()

print(f"📁 Files created:")
for filename in sorted(os.listdir(OUTPUT_DIR))[:10]:
    if filename.endswith('.png'):
        print(f"   - {filename}")
if spectrogram_count > 10:
    print(f"   ... and {spectrogram_count - 10} more")
print()

print(f"🔍 Each spectrogram includes:")
print(f"   - Waveform (top panel)")
print(f"   - Spectrogram (bottom panel)")
print(f"   - Detection boundaries (red dashed lines)")
print(f"   - BirdNET frequency range (yellow dotted lines)")
print(f"   - Metadata (species, confidence, timing)")
print()

print(f"🎯 To review:")
print(f"   open {OUTPUT_DIR}")
print()
