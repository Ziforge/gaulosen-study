#!/usr/bin/env python3
"""
Fetch bird photos from iNaturalist with proper academic citations.
iNaturalist has excellent CC-licensed photos with full attribution.
"""

import requests
import json
import pandas as pd
from pathlib import Path
import time

print("="*80)
print("FETCHING BIRD PHOTOS FROM INATURALIST")
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

    # Search iNaturalist for the species
    search_url = "https://api.inaturalist.org/v1/taxa"

    params = {
        'q': scientific_name,
        'rank': 'species',
        'per_page': 1
    }

    try:
        # Get taxon ID
        response = requests.get(search_url, params=params, timeout=10)
        data = response.json()

        if 'results' in data and len(data['results']) > 0:
            taxon = data['results'][0]
            taxon_id = taxon['id']

            # Get observations with photos
            obs_url = "https://api.inaturalist.org/v1/observations"
            obs_params = {
                'taxon_id': taxon_id,
                'quality_grade': 'research',  # Only research-grade observations
                'photos': 'true',
                'per_page': 5,
                'order_by': 'votes'  # Most voted first
            }

            obs_response = requests.get(obs_url, params=obs_params, timeout=10)
            obs_data = obs_response.json()

            if 'results' in obs_data and len(obs_data['results']) > 0:
                # Get first observation with photo
                for obs in obs_data['results']:
                    if 'photos' in obs and len(obs['photos']) > 0:
                        photo = obs['photos'][0]

                        # Get medium resolution image
                        image_url = photo.get('url', '').replace('square', 'medium')

                        # Get attribution
                        observer = obs.get('user', {}).get('login', 'Unknown')
                        observer_name = obs.get('user', {}).get('name', observer)
                        license_code = photo.get('license_code', 'All Rights Reserved')
                        obs_url_link = f"https://www.inaturalist.org/observations/{obs['id']}"

                        # Map license code to full name
                        license_map = {
                            'cc0': 'CC0 (Public Domain)',
                            'cc-by': 'CC BY 4.0',
                            'cc-by-nc': 'CC BY-NC 4.0',
                            'cc-by-sa': 'CC BY-SA 4.0',
                            'cc-by-nd': 'CC BY-ND 4.0',
                            'cc-by-nc-sa': 'CC BY-NC-SA 4.0',
                            'cc-by-nc-nd': 'CC BY-NC-ND 4.0'
                        }
                        license_full = license_map.get(license_code, license_code)

                        photo_data[common_name] = {
                            'image_url': image_url,
                            'photographer': observer_name,
                            'license': license_full,
                            'source': 'iNaturalist',
                            'observation_url': obs_url_link,
                            'scientific_name': scientific_name,
                            'citation': f"{observer_name} ({obs.get('observed_on', 'n.d.')}). {scientific_name}. iNaturalist observation {obs['id']}. {license_full}. {obs_url_link}"
                        }

                        print(f"  ✓ Found photo")
                        print(f"    Photographer: {observer_name}")
                        print(f"    License: {license_full}")
                        break
                else:
                    print(f"  ⚠️  No suitable photo found")
                    failed.append(common_name)
            else:
                print(f"  ⚠️  No observations with photos")
                failed.append(common_name)
        else:
            print(f"  ⚠️  Taxon not found")
            failed.append(common_name)

    except Exception as e:
        print(f"  ❌ Error: {e}")
        failed.append(common_name)

    # Rate limiting - be nice to iNaturalist API
    time.sleep(1)
    print()

# Save photo data
output_file = Path('website/bird_photos.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(photo_data, f, indent=2, ensure_ascii=False)

print()
print("="*80)
print(f"COMPLETE")
print(f"Found photos: {len(photo_data)}/82")
print(f"Success rate: {len(photo_data)/82*100:.1f}%")
if failed:
    print(f"Failed ({len(failed)}): {', '.join(failed[:5])}{'...' if len(failed) > 5 else ''}")
print(f"Output: {output_file}")
print("="*80)
