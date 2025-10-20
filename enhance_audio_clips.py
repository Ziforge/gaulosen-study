#!/usr/bin/env python3
"""
Enhance Audio Clips for Better Audibility
Applies normalization, amplification, and spectral enhancement
"""

import pandas as pd
import soundfile as sf
import librosa
import numpy as np
import os
from pathlib import Path
from scipy import signal

print("=" * 80)
print("🔊 ENHANCING AUDIO CLIPS FOR BETTER AUDIBILITY")
print("=" * 80)
print()

# Configuration
AUDIO_DIR = "/Users/georgeredpath/Dev/Gaulosen-recordings/audio_files"
ALL_DETECTIONS = "results/all_detections_with_weather.csv"
OUTPUT_DIR = "results/audio_clips_enhanced"
SAMPLE_RATE = 22050

# Enhancement parameters
NORMALIZE = True              # Normalize to max amplitude
AMPLIFICATION_DB = 20         # Amplify by 20 dB (10x amplitude)
HIGH_PASS_FREQ = 500          # Remove low frequency rumble
LOW_PASS_FREQ = 12000         # Focus on bird frequency range
COMPRESSION_RATIO = 3.0       # Dynamic range compression
NOISE_GATE_THRESHOLD = 0.02   # Silence very quiet parts

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("📊 Enhancement Configuration:")
print(f"   Input directory: {AUDIO_DIR}")
print(f"   Output directory: {OUTPUT_DIR}")
print(f"   Sample rate: {SAMPLE_RATE} Hz")
print(f"   Amplification: +{AMPLIFICATION_DB} dB")
print(f"   High-pass filter: {HIGH_PASS_FREQ} Hz (removes rumble)")
print(f"   Low-pass filter: {LOW_PASS_FREQ} Hz (focus on birds)")
print(f"   Compression ratio: {COMPRESSION_RATIO}:1")
print()

def enhance_audio(audio_segment, sr):
    """Apply audio enhancements"""

    # 1. High-pass filter to remove low-frequency rumble
    sos_high = signal.butter(4, HIGH_PASS_FREQ, 'highpass', fs=sr, output='sos')
    audio_segment = signal.sosfilt(sos_high, audio_segment)

    # 2. Low-pass filter to focus on bird frequency range
    sos_low = signal.butter(4, LOW_PASS_FREQ, 'lowpass', fs=sr, output='sos')
    audio_segment = signal.sosfilt(sos_low, audio_segment)

    # 3. Normalize to prevent clipping
    if NORMALIZE and np.max(np.abs(audio_segment)) > 0:
        audio_segment = audio_segment / np.max(np.abs(audio_segment))

    # 4. Apply noise gate (silence very quiet parts)
    audio_segment[np.abs(audio_segment) < NOISE_GATE_THRESHOLD] = 0

    # 5. Dynamic range compression (make quiet sounds louder)
    threshold = 0.3
    mask = np.abs(audio_segment) > threshold
    compressed = audio_segment.copy()
    compressed[mask] = np.sign(audio_segment[mask]) * (
        threshold + (np.abs(audio_segment[mask]) - threshold) / COMPRESSION_RATIO
    )
    compressed[~mask] = audio_segment[~mask] * (1.5)  # Boost quiet parts

    # 6. Apply amplification
    amplification_factor = 10 ** (AMPLIFICATION_DB / 20)
    compressed = compressed * amplification_factor

    # 7. Final normalization to prevent clipping
    if np.max(np.abs(compressed)) > 1.0:
        compressed = compressed / np.max(np.abs(compressed)) * 0.95

    return compressed

# Load all detections
print("📥 Loading all detections...")
df = pd.read_csv(ALL_DETECTIONS)
print(f"   Total detections: {len(df):,}")
print()

# Get best detections (same as before)
print("🔍 Selecting detections for audio enhancement...")
high_priority = df[df['confidence'] < 0.50]
best_per_species = df.groupby('common_name').apply(
    lambda x: x.nlargest(3, 'confidence')
).reset_index(drop=True)
top_overall = df.nlargest(50, 'confidence')
combined = pd.concat([high_priority, best_per_species, top_overall]).drop_duplicates()
print(f"   Total detections to enhance: {len(combined)}")
print()

# Group by audio file
combined_grouped = combined.groupby('filename')

print("🔊 Enhancing audio clips...")
print("-" * 80)

clip_count = 0
enhanced_count = 0

for audio_filename, detections in combined_grouped:
    # Find audio file
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

    try:
        # Load entire audio file
        print(f"      Loading audio...")
        y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)
        duration = len(y) / sr
        print(f"      Audio loaded: {duration/3600:.2f} hours")

        # Process each detection
        for idx, row in detections.iterrows():
            start_time = row['start_s']
            end_time = row['end_s']
            species = row['common_name']
            confidence = row['confidence']

            # Add 0.5 second padding
            context_start = max(0, start_time - 0.5)
            context_end = min(duration, end_time + 0.5)

            # Extract segment
            start_sample = int(context_start * sr)
            end_sample = int(context_end * sr)
            segment = y[start_sample:end_sample]

            if len(segment) == 0:
                continue

            # ENHANCE THE AUDIO
            enhanced_segment = enhance_audio(segment, sr)

            # Create output filename
            safe_species = species.replace(' ', '_').replace('/', '-')
            conf_str = f"{confidence:.3f}".replace('.', '')
            output_filename = f"{row['file_stem']}_{safe_species}_{int(start_time)}s_conf{conf_str}.wav"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            # Save enhanced audio clip
            sf.write(output_path, enhanced_segment, SAMPLE_RATE)

            clip_count += 1
            enhanced_count += 1

            # Show progress for first few
            if clip_count <= 5 or clip_count % 20 == 0:
                print(f"      ✅ {safe_species} ({confidence:.3f}) → ENHANCED")

    except Exception as e:
        print(f"      ❌ Error: {e}")
        continue

print()
print("=" * 80)
print("✅ AUDIO ENHANCEMENT COMPLETE")
print("=" * 80)
print()

print(f"📊 Summary:")
print(f"   Total clips enhanced: {enhanced_count}")
print(f"   Output directory: {OUTPUT_DIR}")
print(f"   Enhancements applied:")
print(f"      • High-pass filter at {HIGH_PASS_FREQ} Hz (removes rumble)")
print(f"      • Low-pass filter at {LOW_PASS_FREQ} Hz (focuses on birds)")
print(f"      • Dynamic range compression ({COMPRESSION_RATIO}:1)")
print(f"      • Amplification: +{AMPLIFICATION_DB} dB")
print(f"      • Normalization and noise gating")
print()

print(f"📁 Sample enhanced files:")
for filename in sorted(os.listdir(OUTPUT_DIR))[:10]:
    if filename.endswith('.wav'):
        size_kb = os.path.getsize(os.path.join(OUTPUT_DIR, filename)) / 1024
        print(f"   - {filename} ({size_kb:.1f} KB)")
if enhanced_count > 10:
    print(f"   ... and {enhanced_count - 10} more")
print()

print(f"🎯 Enhanced audio is MUCH louder and clearer!")
print(f"   Bird calls should now be easily audible")
print()
