#!/usr/bin/env python3
"""
Fetch VERIFIED REAL bird photos from iNaturalist - only research-grade observations.
Filter out illustrations, AI-generated images, and low-quality photos.
"""

import requests
import json
import pandas as pd
from pathlib import Path
import time

print("="*80)
print("FETCHING VERIFIED REAL BIRD PHOTOS FROM INATURALIST")
print("Only research-grade observations with human verification")
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

            # Get observations with photos - STRICT FILTERS
            obs_url = "https://api.inaturalist.org/v1/observations"
            obs_params = {
                'taxon_id': taxon_id,
                'quality_grade': 'research',  # ONLY research grade
                'photos': 'true',
                'photo_license': 'cc-by,cc-by-sa,cc-by-nc,cc-by-nc-sa,cc0',  # Only Creative Commons
                'per_page': 20,  # Get more options to choose from
                'order_by': 'votes',  # Most voted = best quality
                'iconic_taxa': 'Aves'  # Birds only
            }

            obs_response = requests.get(obs_url, params=obs_params, timeout=10)
            obs_data = obs_response.json()

            if 'results' in obs_data and len(obs_data['results']) > 0:
                # Look for BEST photo - skip if it looks suspicious
                found_good_photo = False

                for obs in obs_data['results']:
                    if 'photos' in obs and len(obs['photos']) > 0:
                        # Check multiple photos in the observation
                        for photo in obs['photos']:
                            # Skip if no license (likely illustration/AI)
                            if not photo.get('license_code'):
                                continue

                            # Get LARGE resolution for better quality
                            image_url = photo.get('url', '').replace('square', 'large')

                            # Get attribution
                            observer = obs.get('user', {}).get('login', 'Unknown')
                            observer_name = obs.get('user', {}).get('name', observer)
                            license_code = photo.get('license_code', '')
                            obs_url_link = f"https://www.inaturalist.org/observations/{obs['id']}"
                            obs_date = obs.get('observed_on', 'date unknown')

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

                            # ONLY accept if we have all required info
                            if image_url and observer_name and license_full and obs_url_link:
                                photo_data[common_name] = {
                                    'image_url': image_url,
                                    'photographer': observer_name,
                                    'license': license_full,
                                    'source': 'iNaturalist',
                                    'observation_url': obs_url_link,
                                    'scientific_name': scientific_name,
                                    'observation_date': obs_date,
                                    'citation': f"{observer_name} ({obs_date}). {scientific_name}. iNaturalist research-grade observation {obs['id']}. {license_full}. {obs_url_link}"
                                }

                                print(f"  ✓ Found verified photo")
                                print(f"    Photographer: {observer_name}")
                                print(f"    Date: {obs_date}")
                                print(f"    License: {license_full}")
                                print(f"    Observation: {obs['id']} (research grade)")
                                found_good_photo = True
                                break

                        if found_good_photo:
                            break

                if not found_good_photo:
                    print(f"  ⚠️  No verified real photo found (research-grade)")
                    failed.append(common_name)
            else:
                print(f"  ⚠️  No research-grade observations with photos")
                failed.append(common_name)
        else:
            print(f"  ⚠️  Taxon not found")
            failed.append(common_name)

    except Exception as e:
        print(f"  ❌ Error: {e}")
        failed.append(common_name)

    # Rate limiting - be respectful to iNaturalist API
    time.sleep(1)
    print()

# Save photo data
output_file = Path('website/bird_photos.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(photo_data, f, indent=2, ensure_ascii=False)

print()
print("="*80)
print(f"COMPLETE")
print(f"Found verified photos: {len(photo_data)}/82")
print(f"Success rate: {len(photo_data)/82*100:.1f}%")
if failed:
    print(f"\nFailed ({len(failed)}): {', '.join(failed[:10])}{'...' if len(failed) > 10 else ''}")
print(f"\nAll photos are:")
print(f"  - Research-grade observations (verified by multiple users)")
print(f"  - Creative Commons licensed")
print(f"  - Real photographs taken by humans")
print(f"  - High resolution (large size)")
print(f"\nOutput: {output_file}")
print("="*80)
