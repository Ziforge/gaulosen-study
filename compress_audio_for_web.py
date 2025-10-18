#!/usr/bin/env python3
"""Compress audio files for GitHub Pages deployment."""

import json
import subprocess
from pathlib import Path

# Read species files to get list of audio files needed
with open('species_files.json', 'r') as f:
    species_files = json.load(f)

# Create output directory
output_dir = Path('results/audio_clips_enhanced')
output_dir.mkdir(parents=True, exist_ok=True)

# Compress each audio file
total = len(species_files)
for i, (species, files) in enumerate(species_files.items(), 1):
    if 'audio' not in files:
        continue

    audio_path = Path(files['audio'])
    if not audio_path.exists():
        print(f"[{i}/{total}] SKIP: {species} - file not found: {audio_path}")
        continue

    # Use ffmpeg to compress: mono, 22050 Hz, 64kbps MP3
    output_path = audio_path.with_suffix('.mp3')

    if output_path.exists():
        print(f"[{i}/{total}] EXISTS: {species}")
        continue

    print(f"[{i}/{total}] Compressing: {species}")

    cmd = [
        'ffmpeg', '-i', str(audio_path),
        '-ac', '1',  # mono
        '-ar', '22050',  # 22.05 kHz
        '-b:a', '64k',  # 64 kbps
        '-y',  # overwrite
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[:200]}")
    else:
        # Get file sizes
        original_size = audio_path.stat().st_size / (1024 * 1024)  # MB
        compressed_size = output_path.stat().st_size / (1024 * 1024)  # MB
        ratio = (compressed_size / original_size) * 100
        print(f"  {original_size:.2f}MB -> {compressed_size:.2f}MB ({ratio:.1f}%)")

print("\nDone! Updating species_files.json to use MP3 files...")

# Update species_files.json to point to MP3 files
for species, files in species_files.items():
    if 'audio' in files:
        files['audio'] = files['audio'].replace('.wav', '.mp3')

with open('species_files.json', 'w') as f:
    json.dump(species_files, f, indent=2)

print("Updated species_files.json")
