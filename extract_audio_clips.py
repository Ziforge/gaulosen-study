#!/usr/bin/env python3
"""
Extract Audio Clips for Detections
Creates individual WAV files for web playback
"""

import pandas as pd
import soundfile as sf
import librosa
import os
from pathlib import Path

print("=" * 80)
print("🎵 EXTRACTING AUDIO CLIPS FOR WEB PLAYBACK")
print("=" * 80)
print()

# Configuration
AUDIO_DIR = "/Users/georgeredpath/Dev/Gaulossen-recordings/audio_files"
ALL_DETECTIONS = "results/all_detections_with_weather.csv"
OUTPUT_DIR = "results/audio_clips"
SAMPLE_RATE = 22050  # Standard web audio rate

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("📊 Configuration:")
print(f"   Audio directory: {AUDIO_DIR}")
print(f"   All detections CSV: {ALL_DETECTIONS}")
print(f"   Output directory: {OUTPUT_DIR}")
print(f"   Sample rate: {SAMPLE_RATE} Hz")
print()

# Load all detections
print("📥 Loading all detections with weather...")
df = pd.read_csv(ALL_DETECTIONS)
print(f"   Total detections: {len(df):,}")
print()

# Get best detections (top 3 per species + top 50 overall + all high priority)
print("🔍 Selecting detections for audio extraction...")

# High priority detections (confidence < 0.50)
high_priority = df[df['confidence'] < 0.50]
print(f"   High priority: {len(high_priority)}")

# Top 3 per species
best_per_species = df.groupby('common_name').apply(
    lambda x: x.nlargest(3, 'confidence')
).reset_index(drop=True)
print(f"   Best per species: {len(best_per_species)}")

# Top 50 overall
top_overall = df.nlargest(50, 'confidence')
print(f"   Top 50 overall: {len(top_overall)}")

# Combine and remove duplicates
combined = pd.concat([high_priority, best_per_species, top_overall]).drop_duplicates()
print(f"   Total unique detections to extract: {len(combined)}")
print()

# Group by audio file to minimize loading
combined_grouped = combined.groupby('filename')

print("🎵 Extracting audio clips...")
print("-" * 80)

clip_count = 0
audio_cache = {}  # Cache loaded audio to avoid reloading

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

            # Add 0.5 second padding for context
            context_start = max(0, start_time - 0.5)
            context_end = min(duration, end_time + 0.5)

            # Extract segment
            start_sample = int(context_start * sr)
            end_sample = int(context_end * sr)
            segment = y[start_sample:end_sample]

            if len(segment) == 0:
                continue

            # Create output filename
            safe_species = species.replace(' ', '_').replace('/', '-')
            conf_str = f"{confidence:.3f}".replace('.', '')
            output_filename = f"{row['file_stem']}_{safe_species}_{int(start_time)}s_conf{conf_str}.wav"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            # Save audio clip
            sf.write(output_path, segment, SAMPLE_RATE)

            clip_count += 1
            print(f"      ✅ {safe_species} ({confidence:.3f}) → {output_filename}")

    except Exception as e:
        print(f"      ❌ Error: {e}")
        continue

print()
print("=" * 80)
print("✅ AUDIO CLIP EXTRACTION COMPLETE")
print("=" * 80)
print()

print(f"📊 Summary:")
print(f"   Total audio clips extracted: {clip_count}")
print(f"   Output directory: {OUTPUT_DIR}")
print(f"   Format: WAV, {SAMPLE_RATE} Hz")
print()

print(f"📁 Sample files created:")
for filename in sorted(os.listdir(OUTPUT_DIR))[:10]:
    if filename.endswith('.wav'):
        size_kb = os.path.getsize(os.path.join(OUTPUT_DIR, filename)) / 1024
        print(f"   - {filename} ({size_kb:.1f} KB)")
if clip_count > 10:
    print(f"   ... and {clip_count - 10} more")
print()

print(f"🎯 These clips are ready for web playback!")
print()
