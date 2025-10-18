#!/usr/bin/env python3
"""
Map spectrogram and audio files to each species for the gallery.
"""

import pandas as pd
from pathlib import Path
import json

print("="*80)
print("GENERATING SPECIES FILE MAPPINGS")
print("="*80)
print()

# Get list of all spectrograms and audio files
spec_dir = Path('results/spectrograms_best')
audio_dir = Path('results/audio_clips_enhanced')

spectrograms = list(spec_dir.glob('*.png'))
audio_files = list(audio_dir.glob('*.wav'))

print(f"Found {len(spectrograms)} spectrograms")
print(f"Found {len(audio_files)} audio files")
print()

# Load verified species
verified_species = pd.read_csv('results/verified_species_list.csv')

# Create mapping
species_files = {}

for _, row in verified_species.iterrows():
    species = row['species']

    # Normalize species name for filename matching
    # Try both with and without apostrophe
    species_normalized = species.replace(' ', '_').replace('-', '-')
    species_no_apostrophe = species_normalized.replace("'", "")

    # Find matching spectrogram
    spec_match = None
    for spec in spectrograms:
        if species_normalized in spec.name or species_no_apostrophe in spec.name:
            spec_match = f"results/spectrograms_best/{spec.name}"
            break

    # Find matching audio
    audio_match = None
    for audio in audio_files:
        if species_normalized in audio.name or species_no_apostrophe in audio.name:
            audio_match = f"results/audio_clips_enhanced/{audio.name}"
            break

    if spec_match or audio_match:
        species_files[species] = {
            'spectrogram': spec_match,
            'audio': audio_match
        }
        print(f"✓ {species}")
        if spec_match:
            print(f"  Spectrogram: {Path(spec_match).name}")
        if audio_match:
            print(f"  Audio: {Path(audio_match).name}")
    else:
        print(f"⚠️  {species} - No files found")

# Save mapping
output_file = Path('website/species_files.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(species_files, f, indent=2, ensure_ascii=False)

print()
print("="*80)
print(f"COMPLETE - Mapped {len(species_files)} species to files")
print(f"Output: {output_file}")
print("="*80)
