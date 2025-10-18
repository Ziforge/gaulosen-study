#!/usr/bin/env python3
"""
Rename original WAV files to include date, time, temperature, and weather
From: 245AAA0563ED3DA7_20251013_113753.WAV
To:   2025-10-13_11h37m_7-11C_Damp_foggy_low_visibility.WAV
"""

import pandas as pd
from pathlib import Path
import shutil

print("=" * 80)
print("RENAMING ORIGINAL WAV FILES WITH WEATHER METADATA")
print("=" * 80)
print()

# Load weather data
df = pd.read_csv('results/all_detections_with_weather.csv')

# Get unique files with their metadata
files_metadata = df.groupby('filename').first()[['recording_date', 'recording_start_time', 'weather_temp_c', 'weather_summary']].reset_index()

print(f"Found {len(files_metadata)} original WAV files to process")
print()

# Find original WAV files (check multiple possible locations)
original_dirs = [
    Path('.'),
    Path('audio'),
    Path('recordings'),
    Path('..'),
]

# Find where the WAV files are
wav_files = {}
for search_dir in original_dirs:
    if search_dir.exists():
        for wav_file in search_dir.glob('*.WAV'):
            wav_files[wav_file.name] = wav_file
        for wav_file in search_dir.glob('*.wav'):
            wav_files[wav_file.name.upper()] = wav_file

if not wav_files:
    print("❌ No original WAV files found in:")
    for d in original_dirs:
        print(f"   {d.absolute()}")
    print()
    print("Please specify the directory containing the original WAV files.")
    exit(1)

print(f"Found {len(wav_files)} WAV files")
print()

# Create rename mapping
rename_map = {}

for idx, row in files_metadata.iterrows():
    old_name = row['filename']

    # Check if file exists
    if old_name not in wav_files:
        print(f"⚠️  File not found: {old_name}")
        continue

    old_path = wav_files[old_name]

    date = row['recording_date']  # 2025-10-13
    time = row['recording_start_time']  # 11:37:53
    temp = row['weather_temp_c']  # 7-11
    weather = row['weather_summary']  # Damp, foggy, low visibility

    # Create short weather code
    weather_code = weather.replace(',', '').replace(' ', '_').replace('/', '-')[:40]

    # Format: 2025-10-13_11h37m_7-11C_Damp_foggy_low_visibility.WAV
    time_parts = time.split(':')
    hour = time_parts[0]
    minute = time_parts[1]

    # Clean temperature string (replace / with -)
    temp_clean = temp.replace('/', '-')

    new_name = f"{date}_{hour}h{minute}m_{temp_clean}C_{weather_code}.WAV"
    new_path = old_path.parent / new_name

    rename_map[old_path] = new_path

print("Proposed renamings:")
print("-" * 80)
for old_path, new_path in rename_map.items():
    print(f"OLD: {old_path.name}")
    print(f"NEW: {new_path.name}")
    print()

# Perform renames
print("Renaming files...")
print("-" * 80)

success_count = 0
error_count = 0

for old_path, new_path in rename_map.items():
    try:
        old_path.rename(new_path)
        print(f"✓ {new_path.name}")
        success_count += 1
    except Exception as e:
        print(f"✗ Failed: {old_path.name} - {e}")
        error_count += 1

print()
print("=" * 80)
print(f"✅ Renamed {success_count} original WAV files")
if error_count > 0:
    print(f"❌ Failed: {error_count} files")
print("=" * 80)
print()

# Show new filenames
print("New original WAV filenames:")
print("-" * 80)
parent_dir = list(rename_map.values())[0].parent if rename_map else Path('.')
for wav_file in sorted(parent_dir.glob('*.WAV')):
    print(f"  {wav_file.name}")
print()
