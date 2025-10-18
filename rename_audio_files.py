#!/usr/bin/env python3
"""
Rename audio files to human-readable format:
From: 245AAA0563ED3DA7_20251013_113753_Spotted_Crake_15s_conf0.87.wav
To:   2025-10-13_11h37m_Spotted_Crake_15s_conf087.wav
"""

import pandas as pd
from pathlib import Path
import shutil
import re

print("=" * 80)
print("RENAMING AUDIO FILES TO HUMAN-READABLE FORMAT")
print("=" * 80)
print()

# Load metadata
df = pd.read_csv('results/all_detections_with_weather.csv')

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

# Show examples
print(f"Found {len(rename_map)} audio files to rename")
print()
print("Example renamings:")
print("-" * 80)
for i, (old, new) in enumerate(list(rename_map.items())[:5]):
    print(f"OLD: {old.name}")
    print(f"NEW: {new.name}")
    print()

# Ask for confirmation
response = input("Proceed with renaming? (yes/no): ")
if response.lower() != 'yes':
    print("❌ Aborted")
    exit(0)

# Perform renames
print()
print("Renaming files...")
print("-" * 80)

success_count = 0
error_count = 0

for old_path, new_path in rename_map.items():
    try:
        old_path.rename(new_path)
        success_count += 1
        if success_count <= 10:  # Show first 10
            print(f"✓ {new_path.name}")
    except Exception as e:
        print(f"✗ Failed: {old_path.name} - {e}")
        error_count += 1

print()
print("=" * 80)
print(f"✅ Renamed {success_count} files")
if error_count > 0:
    print(f"❌ Failed: {error_count} files")
print("=" * 80)
print()

# Update the website tables with new filenames
print("Updating website tables with new filenames...")

website_tables = Path('results/WEBSITE_BEHAVIORAL_FINDINGS_TABLES.md')
if website_tables.exists():
    content = website_tables.read_text()

    # Replace old format with new format
    # 245AAA0563ED3DA7_20251013_113753.WAV -> 2025-10-13_11h37m
    for old_path, new_path in list(rename_map.items())[:10]:
        old_basename = old_path.stem.split('_')
        if len(old_basename) >= 3:
            old_prefix = f"{old_basename[0]}_{old_basename[1]}_{old_basename[2]}"
            new_prefix = new_path.stem.rsplit('_', 3)[0]  # Everything before _species_time_conf
            content = content.replace(old_prefix, new_prefix)

    # Write updated content
    website_tables.write_text(content)
    print("✅ Updated website tables")

print()
print("Example new filenames:")
print("-" * 80)
for audio_file in sorted(audio_dir.glob('*.wav'))[:10]:
    print(f"  {audio_file.name}")
print()
