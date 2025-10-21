#!/usr/bin/env python3
"""
Fetch high-quality bird photos from Macaulay Library (eBird).
These are professionally curated, verified photos.
"""

import requests
import json
import time

print("="*80)
print("FETCHING BIRD PHOTOS FROM MACAULAY LIBRARY (EBIRD)")
print("Professionally curated, verified bird photographs")
print("="*80)
print()

# Load existing data
with open('website/species_data.json', 'r', encoding='utf-8') as f:
    species_data = json.load(f)

with open('website/bird_photos.json', 'r', encoding='utf-8') as f:
    photo_data = json.load(f)

# Problem species that need better photos
problem_species = [
    'Common Sandpiper',
    'Graylag Goose',
    'Carrion Crow',
    'Common Crane',
    'Mallard',
    'Manx Shearwater',
    'Bank Swallow',
    'Common Raven',
]

# Map to scientific names
species_map = {sp['common_name']: sp['scientific_name'] for sp in species_data}

updated = 0
failed = []

for idx, common_name in enumerate(problem_species, 1):
    scientific_name = species_map.get(common_name, '')

    print(f"[{idx}/{len(problem_species)}] {common_name} ({scientific_name})")

    try:
        # Search eBird API for species media
        # Note: eBird/Macaulay Library has stricter access - this is a basic search
        search_url = "https://search.macaulaylibrary.org/api/v1/search"

        params = {
            'taxonCode': None,  # We'll need to map this
            'mediaType': 'photo',
            'sort': 'rating_rank_desc',  # Highest rated first
            'count': 10
        }

        # For now, let's try a simple approach with the species name
        # This may require eBird API key for full access
        print(f"  ⚠️  Macaulay Library requires API key for full access")
        print(f"  ℹ️  Keeping existing photo or marking as needs manual curation")
        failed.append(common_name)

    except Exception as e:
        print(f"  ❌ Error: {e}")
        failed.append(common_name)

    time.sleep(0.5)
    print()

print()
print("="*80)
print(f"RESULT: Manual curation needed")
print(f"Macaulay Library requires API access for automated fetching")
print(f"\nSuggestion: Manually curate photos from:")
print(f"  - Macaulay Library: https://search.macaulaylibrary.org/")
print(f"  - Wikimedia Commons: https://commons.wikimedia.org/")
print(f"  - Birdingplaces (photographer credits available)")
print(f"\nSpecies needing better photos: {', '.join(problem_species)}")
print("="*80)
