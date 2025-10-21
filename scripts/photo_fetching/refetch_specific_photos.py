#!/usr/bin/env python3
"""
Re-fetch specific bird photos with stricter quality criteria.
Focus on getting the most appropriate, high-quality photos.
"""

import requests
import json
import time

print("="*80)
print("RE-FETCHING SPECIFIC BIRD PHOTOS")
print("Targeting species that need better images")
print("="*80)
print()

# Load existing data
with open('website/species_data.json', 'r', encoding='utf-8') as f:
    species_data = json.load(f)

with open('website/bird_photos.json', 'r', encoding='utf-8') as f:
    photo_data = json.load(f)

# Species to re-fetch with their requirements
species_to_refetch = {
    'Graylag Goose': 'Anser anser',
    'Common Sandpiper': 'Actitis hypoleucos',
    'Hooded Crow': 'Corvus cornix',
    'Carrion Crow': 'Corvus corone',
    'Mallard': 'Anas platyrhynchos',
    'Common Crane': 'Grus grus',  # Need grey/adult plumage
    'Canada Goose': 'Branta canadensis',
    'Manx Shearwater': 'Puffinus puffinus',
    'Arctic Warbler': 'Phylloscopus borealis',
    'European Storm-Petrel': 'Hydrobates pelagicus',
    'Eurasian Eagle-Owl': 'Bubo bubo',
    'Common House-Martin': 'Delichon urbicum',
    'Bank Swallow': 'Riparia riparia',  # Try European name
}

updated = 0
still_failed = []

for idx, (common_name, scientific_name) in enumerate(species_to_refetch.items(), 1):
    print(f"[{idx}/{len(species_to_refetch)}] {common_name} ({scientific_name})")

    # For Bank Swallow, also try Sand Martin (European name)
    search_names = [scientific_name]
    if common_name == 'Bank Swallow':
        search_names.append('Riparia riparia')  # Try with different common name search

    best_photo = None
    best_score = 0

    for search_name in search_names:
        try:
            # Search iNaturalist for the species
            search_url = "https://api.inaturalist.org/v1/taxa"
            params = {
                'q': search_name,
                'rank': 'species',
                'per_page': 1
            }

            response = requests.get(search_url, params=params, timeout=10)
            data = response.json()

            if 'results' in data and len(data['results']) > 0:
                taxon = data['results'][0]
                taxon_id = taxon['id']

                # Get observations with photos - VERY STRICT FILTERS
                obs_url = "https://api.inaturalist.org/v1/observations"
                obs_params = {
                    'taxon_id': taxon_id,
                    'quality_grade': 'research',
                    'photos': 'true',
                    'photo_license': 'cc-by,cc-by-sa,cc0',  # Most permissive licenses only
                    'per_page': 50,  # Get many options
                    'order_by': 'votes',  # Most voted first
                    'iconic_taxa': 'Aves'
                }

                obs_response = requests.get(obs_url, params=obs_params, timeout=10)
                obs_data = obs_response.json()

                if 'results' in obs_data and len(obs_data['results']) > 0:
                    # Score each observation
                    for obs in obs_data['results']:
                        if 'photos' in obs and len(obs['photos']) > 0:
                            for photo in obs['photos']:
                                # Skip if no license
                                if not photo.get('license_code'):
                                    continue

                                # Calculate quality score
                                score = 0

                                # Prefer CC BY or CC0 (most open)
                                license_code = photo.get('license_code', '')
                                if license_code in ['cc0', 'cc-by']:
                                    score += 10
                                elif license_code == 'cc-by-sa':
                                    score += 5

                                # Prefer photos with more faves
                                score += obs.get('faves_count', 0)

                                # Prefer more votes
                                score += obs.get('votes_count', 0) * 2

                                # Prefer observations with descriptions
                                if obs.get('description'):
                                    score += 3

                                # Check if this is the best photo so far
                                if score > best_score:
                                    observer = obs.get('user', {}).get('login', 'Unknown')
                                    observer_name = obs.get('user', {}).get('name', observer)
                                    obs_date = obs.get('observed_on', 'date unknown')
                                    obs_url_link = f"https://www.inaturalist.org/observations/{obs['id']}"

                                    # Get LARGE resolution
                                    image_url = photo.get('url', '').replace('square', 'large')

                                    license_map = {
                                        'cc0': 'CC0 (Public Domain)',
                                        'cc-by': 'CC BY 4.0',
                                        'cc-by-sa': 'CC BY-SA 4.0',
                                    }
                                    license_full = license_map.get(license_code, license_code)

                                    # Verify all required info
                                    if image_url and observer_name and license_full and obs_url_link:
                                        best_photo = {
                                            'image_url': image_url,
                                            'photographer': observer_name,
                                            'license': license_full,
                                            'source': 'iNaturalist',
                                            'observation_url': obs_url_link,
                                            'scientific_name': scientific_name,
                                            'observation_date': obs_date,
                                            'citation': f"{observer_name} ({obs_date}). {scientific_name}. iNaturalist research-grade observation {obs['id']}. {license_full}. {obs_url_link}"
                                        }
                                        best_score = score

        except Exception as e:
            print(f"  ⚠️  Error searching: {e}")
            continue

        time.sleep(0.5)  # Brief delay between searches

    if best_photo:
        photo_data[common_name] = best_photo
        print(f"  ✓ Found better photo")
        print(f"    Photographer: {best_photo['photographer']}")
        print(f"    Date: {best_photo['observation_date']}")
        print(f"    License: {best_photo['license']}")
        print(f"    Score: {best_score}")
        updated += 1
    else:
        print(f"  ⚠️  Could not find suitable photo")
        still_failed.append(common_name)

    time.sleep(1)  # Rate limiting
    print()

# Save updated photo data
with open('website/bird_photos.json', 'w', encoding='utf-8') as f:
    json.dump(photo_data, f, indent=2, ensure_ascii=False)

print()
print("="*80)
print(f"COMPLETE")
print(f"Updated photos: {updated}/{len(species_to_refetch)}")
if still_failed:
    print(f"\nStill no photos found for ({len(still_failed)}): {', '.join(still_failed)}")
print(f"\nOutput: website/bird_photos.json")
print("="*80)
