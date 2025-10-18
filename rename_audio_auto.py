#!/usr/bin/env python3
"""
Rename audio files to human-readable format (automatic):
From: 245AAA0563ED3DA7_20251013_113753_Spotted_Crake_15s_conf0.87.wav
To:   2025-10-13_11h37m_Spotted_Crake_15s_conf087.wav
"""

import pandas as pd
from pathlib import Path
import re

print("=" * 80)
print("RENAMING AUDIO FILES TO HUMAN-READABLE FORMAT")
print("=" * 80)
print()

# Get audio directory
audio_dir = Path('results/audio_clips_enhanced')
if not audio_dir.exists():
    print(f"❌ Audio directory not found: {audio_dir}")
    exit(1)

# Create mapping of old to new names
rename_map = {}

for audio_file in audio_dir.glob('*.wav'):
    # Parse filename
    # Format: 245AAA0563ED3DA7_20251013_113753_Spotted_Crake_15s_conf0.87.wav
    parts = audio_file.stem.split('_')

    if len(parts) < 5:
        continue

    # Extract components
    file_id = parts[0]  # 245AAA0563ED3DA7
    date = parts[1]      # 20251013
    time = parts[2]      # 113753

    # Find species name (everything between time and "Xs")
    species_parts = []
    for i in range(3, len(parts)):
        if re.match(r'\d+s$', parts[i]):  # Found timestamp like "15s"
            break
        species_parts.append(parts[i])

    species = '_'.join(species_parts)

    # Find timestamp and confidence
    timestamp = None
    confidence = None
    for part in parts:
        if re.match(r'\d+s$', part):
            timestamp = part
        elif part.startswith('conf'):
            confidence = part.replace('conf', '').replace('.', '')

    if not timestamp or not confidence:
        continue

    # Format new name
    # 2025-10-13_11h37m_Spotted_Crake_15s_conf087.wav
    year = date[:4]
    month = date[4:6]
    day = date[6:8]
    hour = time[:2]
    minute = time[2:4]

    new_name = f"{year}-{month}-{day}_{hour}h{minute}m_{species}_{timestamp}_conf{confidence}.wav"

    rename_map[audio_file] = audio_dir / new_name

print(f"Found {len(rename_map)} audio files to rename")
print()
print("Example renamings (first 10):")
print("-" * 80)
for i, (old, new) in enumerate(list(rename_map.items())[:10]):
    print(f"{old.name}")
    print(f"  → {new.name}")
    print()

# Perform renames
print("Renaming files...")
print("-" * 80)

success_count = 0
error_count = 0

for old_path, new_path in rename_map.items():
    try:
        old_path.rename(new_path)
        success_count += 1
        if success_count <= 20:  # Show first 20
            print(f"✓ {new_path.name}")
    except Exception as e:
        print(f"✗ Failed: {old_path.name} - {e}")
        error_count += 1

print()
if success_count > 20:
    print(f"... and {success_count - 20} more files")
print()

print("=" * 80)
print(f"✅ Renamed {success_count} files")
if error_count > 0:
    print(f"❌ Failed: {error_count} files")
print("=" * 80)
print()

# Show sample of new filenames
print("Sample of new filenames (sorted by species):")
print("-" * 80)
new_files = sorted(audio_dir.glob('*.wav'))
species_samples = {}
for audio_file in new_files:
    # Extract species from filename
    parts = audio_file.stem.split('_')
    if len(parts) >= 4:
        species = '_'.join(parts[2:-2])  # Between date/time and timestamp/conf
        if species not in species_samples:
            species_samples[species] = []
        if len(species_samples[species]) < 2:  # 2 examples per species
            species_samples[species].append(audio_file.name)

for species, files in sorted(species_samples.items())[:10]:
    print(f"\n{species}:")
    for filename in files:
        print(f"  {filename}")

print()
print(f"\nTotal files: {len(new_files)}")
print()
