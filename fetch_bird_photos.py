#!/usr/bin/env python3
"""
Fetch bird photos from Wikimedia Commons with proper attribution.
Creates a JSON file mapping species to photo URLs with full academic citations.
"""

import requests
import json
import pandas as pd
from pathlib import Path
import time

print("="*80)
print("FETCHING BIRD PHOTOS FROM WIKIMEDIA COMMONS")
print("="*80)
print()

# Load verified species
verified_species = pd.read_csv('results/verified_species_list.csv')
species_data = json.load(open('website/species_data.json', 'r', encoding='utf-8'))

# Create mapping of common name to scientific name
name_map = {sp['common_name']: sp['scientific_name'] for sp in species_data}

photo_data = {}
failed = []

for idx, (_, row) in enumerate(verified_species.iterrows()):
    common_name = row['species']
    scientific_name = name_map.get(common_name, '')

    print(f"[{idx+1}/82] {common_name} ({scientific_name})")

    # Search Wikimedia Commons for the species
    search_url = "https://commons.wikimedia.org/w/api.php"

    params = {
        'action': 'query',
        'format': 'json',
        'generator': 'search',
        'gsrsearch': f'{scientific_name} bird',
        'gsrlimit': 5,
        'prop': 'imageinfo',
        'iiprop': 'url|extmetadata|size',
        'iiurlwidth': 800
    }

    try:
        response = requests.get(search_url, params=params, timeout=10)
        data = response.json()

        if 'query' in data and 'pages' in data['query']:
            # Get the first suitable image
            for page_id, page in data['query']['pages'].items():
                if 'imageinfo' in page:
                    img_info = page['imageinfo'][0]

                    # Check if it's a photo (not a drawing/map)
                    if 'extmetadata' in img_info:
                        metadata = img_info['extmetadata']

                        # Get image URL
                        image_url = img_info.get('thumburl', img_info.get('url', ''))

                        # Get attribution info
                        artist = metadata.get('Artist', {}).get('value', 'Unknown')
                        license_name = metadata.get('LicenseShortName', {}).get('value', 'Unknown')
                        license_url = metadata.get('LicenseUrl', {}).get('value', '')

                        # Clean HTML from artist field
                        if '<' in artist:
                            import re
                            artist = re.sub('<[^<]+?>', '', artist).strip()

                        photo_data[common_name] = {
                            'image_url': image_url,
                            'artist': artist,
                            'license': license_name,
                            'license_url': license_url,
                            'source': f"Wikimedia Commons",
                            'scientific_name': scientific_name,
                            'citation': f"{artist}. {scientific_name}. Wikimedia Commons. {license_name}. {license_url or 'https://commons.wikimedia.org'}"
                        }

                        print(f"  ✓ Found image")
                        print(f"    Artist: {artist[:60]}...")
                        print(f"    License: {license_name}")
                        break
            else:
                print(f"  ⚠️  No suitable image found")
                failed.append(common_name)
        else:
            print(f"  ⚠️  No results")
            failed.append(common_name)

    except Exception as e:
        print(f"  ❌ Error: {e}")
        failed.append(common_name)

    # Rate limiting
    time.sleep(0.5)
    print()

# Save photo data
output_file = Path('website/bird_photos.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(photo_data, f, indent=2, ensure_ascii=False)

print()
print("="*80)
print(f"COMPLETE")
print(f"Found photos: {len(photo_data)}/82")
print(f"Failed: {len(failed)}")
if failed:
    print(f"Failed species: {', '.join(failed[:5])}{'...' if len(failed) > 5 else ''}")
print(f"Output: {output_file}")
print("="*80)
