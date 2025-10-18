#!/usr/bin/env python3
"""
Fetch high-quality bird photos from Wikimedia Commons.
Wikimedia has curated, verified photos with proper quality control.
"""

import requests
import json
import time

print("="*80)
print("FETCHING BIRD PHOTOS FROM WIKIMEDIA COMMONS")
print("High-quality, curated photos with proper licensing")
print("="*80)
print()

# Load existing data
with open('website/bird_photos.json', 'r', encoding='utf-8') as f:
    photo_data = json.load(f)

# Species to re-fetch - focus on problematic ones
species_to_refetch = {
    'Common Sandpiper': 'Actitis hypoleucos',
    'Graylag Goose': 'Anser anser',
    'Carrion Crow': 'Corvus corone',
    'Common Crane': 'Grus grus',
    'Mallard': 'Anas platyrhynchos',
    'Manx Shearwater': 'Puffinus puffinus',
    'Bank Swallow': 'Riparia riparia',
    'Common Raven': 'Corvus corax',
}

updated = 0
failed = []

for idx, (common_name, scientific_name) in enumerate(species_to_refetch.items(), 1):
    print(f"[{idx}/{len(species_to_refetch)}] {common_name} ({scientific_name})")

    try:
        # Search Wikimedia Commons for the species
        search_url = "https://commons.wikimedia.org/w/api.php"
        params = {
            'action': 'query',
            'format': 'json',
            'generator': 'search',
            'gsrsearch': f'{scientific_name} filetype:bitmap',
            'gsrlimit': 20,
            'prop': 'imageinfo',
            'iiprop': 'url|extmetadata|size',
            'iiurlwidth': 800
        }

        response = requests.get(search_url, params=params, timeout=15)
        data = response.json()

        if 'query' in data and 'pages' in data['query']:
            pages = data['query']['pages']

            best_photo = None
            best_score = 0

            for page_id, page in pages.items():
                if 'imageinfo' not in page:
                    continue

                imageinfo = page['imageinfo'][0]

                # Skip if too small
                if imageinfo.get('width', 0) < 400 or imageinfo.get('height', 0) < 300:
                    continue

                # Get metadata
                extmetadata = imageinfo.get('extmetadata', {})

                # Check license
                license_info = extmetadata.get('LicenseShortName', {}).get('value', '')
                if not license_info or 'cc' not in license_info.lower():
                    continue

                # Get attribution
                artist = extmetadata.get('Artist', {}).get('value', 'Unknown')
                credit = extmetadata.get('Credit', {}).get('value', '')

                # Clean up HTML from artist field
                if artist:
                    import re
                    artist = re.sub('<[^<]+?>', '', artist).strip()
                    if not artist or len(artist) > 100:
                        artist = 'Unknown'

                # Score based on image quality indicators
                score = 0
                score += imageinfo.get('width', 0) / 100  # Higher resolution = better
                score += imageinfo.get('height', 0) / 100

                # Prefer certain licenses
                if 'cc-0' in license_info.lower() or 'public domain' in license_info.lower():
                    score += 20
                elif 'cc-by' in license_info.lower() and 'sa' in license_info.lower():
                    score += 15
                elif 'cc-by' in license_info.lower():
                    score += 10

                if score > best_score:
                    image_url = imageinfo.get('thumburl', imageinfo.get('url', ''))
                    page_url = imageinfo.get('descriptionurl', '')

                    if image_url and page_url:
                        best_photo = {
                            'image_url': image_url,
                            'photographer': artist,
                            'license': license_info,
                            'source': 'Wikimedia Commons',
                            'observation_url': page_url,
                            'scientific_name': scientific_name,
                            'observation_date': 'via Wikimedia',
                            'citation': f"{artist}. {scientific_name}. Wikimedia Commons. {license_info}. {page_url}"
                        }
                        best_score = score

            if best_photo:
                photo_data[common_name] = best_photo
                print(f"  ✓ Found photo")
                print(f"    Photographer: {best_photo['photographer']}")
                print(f"    License: {best_photo['license']}")
                print(f"    Score: {best_score:.1f}")
                updated += 1
            else:
                print(f"  ⚠️  No suitable photo found")
                failed.append(common_name)
        else:
            print(f"  ⚠️  No results from Wikimedia")
            failed.append(common_name)

    except Exception as e:
        print(f"  ❌ Error: {e}")
        failed.append(common_name)

    time.sleep(1)
    print()

# Save updated data
with open('website/bird_photos.json', 'w', encoding='utf-8') as f:
    json.dump(photo_data, f, indent=2, ensure_ascii=False)

print()
print("="*80)
print(f"COMPLETE")
print(f"Updated photos: {updated}/{len(species_to_refetch)}")
if failed:
    print(f"\nFailed ({len(failed)}): {', '.join(failed)}")
print(f"\nOutput: website/bird_photos.json")
print("="*80)
