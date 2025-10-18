#!/usr/bin/env python3
"""
Fetch bird photos from Pixabay - free for commercial use.
Pixabay License: Free to use, no attribution required.
"""

import requests
import json
import time
import os

# Pixabay API key - you need to get one from https://pixabay.com/api/docs/
# Sign up for free at https://pixabay.com/accounts/register/
PIXABAY_API_KEY = os.environ.get('PIXABAY_API_KEY', '')

if not PIXABAY_API_KEY:
    print("="*80)
    print("PIXABAY API KEY REQUIRED")
    print("="*80)
    print()
    print("To use Pixabay API:")
    print("1. Sign up for free at: https://pixabay.com/accounts/register/")
    print("2. Get your API key from: https://pixabay.com/api/docs/")
    print("3. Set environment variable: export PIXABAY_API_KEY='your_key_here'")
    print("4. Run this script again")
    print()
    print("="*80)
    exit(1)

print("="*80)
print("FETCHING BIRD PHOTOS FROM PIXABAY")
print("Free to use, no attribution required (Pixabay License)")
print("="*80)
print()

# Load existing data
with open('website/species_data.json', 'r', encoding='utf-8') as f:
    species_data = json.load(f)

with open('website/bird_photos.json', 'r', encoding='utf-8') as f:
    photo_data = json.load(f)

# All species
all_species = [(sp['common_name'], sp['scientific_name']) for sp in species_data]

updated = 0
failed = []

for idx, (common_name, scientific_name) in enumerate(all_species, 1):
    print(f"[{idx}/{len(all_species)}] {common_name}")

    # Try both common name and scientific name
    search_terms = [
        common_name.lower(),
        scientific_name.lower().split()[0],  # Genus
        ' '.join(scientific_name.lower().split()[:2])  # Genus + species
    ]

    best_photo = None
    best_score = 0

    for search_term in search_terms:
        try:
            url = "https://pixabay.com/api/"
            params = {
                'key': PIXABAY_API_KEY,
                'q': search_term,
                'image_type': 'photo',
                'category': 'animals',
                'min_width': 640,
                'min_height': 480,
                'safesearch': 'true',
                'per_page': 20,
                'order': 'popular'
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if 'hits' in data and len(data['hits']) > 0:
                for hit in data['hits']:
                    # Score based on quality indicators
                    score = 0
                    score += hit.get('likes', 0) / 10
                    score += hit.get('favorites', 0) / 5
                    score += hit.get('views', 0) / 1000
                    score += hit.get('imageWidth', 0) / 100
                    score += hit.get('imageHeight', 0) / 100

                    # Check if tags match our species (fuzzy matching)
                    tags = [t.lower() for t in hit.get('tags', '').split(',')]
                    species_words = set(common_name.lower().split()) | set(scientific_name.lower().split())

                    # Boost score if tags match species words
                    if any(word in ' '.join(tags) for word in species_words):
                        score += 50

                    if score > best_score:
                        best_photo = {
                            'image_url': hit.get('largeImageURL', hit.get('webformatURL', '')),
                            'photographer': hit.get('user', 'Unknown'),
                            'license': 'Pixabay License (Free for commercial use)',
                            'source': 'Pixabay',
                            'observation_url': hit.get('pageURL', ''),
                            'scientific_name': scientific_name,
                            'observation_date': 'N/A',
                            'citation': f"{hit.get('user', 'Unknown')}. {common_name}. Pixabay. Pixabay License. {hit.get('pageURL', '')}"
                        }
                        best_score = score

            time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"  ⚠️  Error searching '{search_term}': {e}")
            continue

    if best_photo and best_score > 10:  # Minimum quality threshold
        photo_data[common_name] = best_photo
        print(f"  ✓ Found photo")
        print(f"    Photographer: {best_photo['photographer']}")
        print(f"    Score: {best_score:.1f}")
        updated += 1
    else:
        print(f"  ⚠️  No suitable photo found")
        failed.append(common_name)

    time.sleep(1)  # Rate limiting
    print()

# Save updated data
with open('website/bird_photos.json', 'w', encoding='utf-8') as f:
    json.dump(photo_data, f, indent=2, ensure_ascii=False)

print()
print("="*80)
print(f"COMPLETE")
print(f"Updated photos: {updated}/{len(all_species)}")
if failed:
    print(f"\nNo photos found for ({len(failed)}): {', '.join(failed[:10])}{'...' if len(failed) > 10 else ''}")
print(f"\nAll photos from Pixabay are:")
print(f"  - Free for commercial use")
print(f"  - No attribution required (but included anyway)")
print(f"  - High quality user-submitted images")
print(f"\nOutput: website/bird_photos.json")
print("="*80)
