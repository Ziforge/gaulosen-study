#!/usr/bin/env python3
"""
Fetch bird photos from birdingplaces.eu Gaulosen page.
These photos are already labeled with the correct bird species names.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin

print("="*80)
print("FETCHING BIRD PHOTOS FROM BIRDINGPLACES.EU")
print("Source: https://www.birdingplaces.eu/en/birdingplaces/norway/gaulosen-naturreservat")
print("="*80)
print()

# Fetch the page
url = "https://www.birdingplaces.eu/en/birdingplaces/norway/gaulosen-naturreservat"
print(f"Fetching page: {url}")

try:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    print(f"✓ Page fetched successfully ({len(response.content)} bytes)")
except Exception as e:
    print(f"❌ Error fetching page: {e}")
    exit(1)

# Parse HTML
soup = BeautifulSoup(response.content, 'html.parser')
print("✓ HTML parsed")
print()

# Load our species list
with open('website/species_data.json', 'r', encoding='utf-8') as f:
    our_species = json.load(f)

our_species_names = {sp['common_name'].lower() for sp in our_species}
our_species_scientific = {sp['scientific_name'].lower() for sp in our_species}

print(f"Looking for photos for {len(our_species)} detected species...")
print()

# Find all bird links/images on the page
bird_photos = {}

# Look for bird species containers
# The page structure has bird names and associated images
bird_elements = soup.find_all(['a', 'div'], class_=re.compile(r'bird|species', re.I))

print(f"Found {len(bird_elements)} potential bird elements")

# Also look for all images with bird-related paths
all_images = soup.find_all('img')
print(f"Found {len(all_images)} total images")
print()

# Parse the page more carefully for bird species with photos
for img in all_images:
    src = img.get('src', '')
    alt = img.get('alt', '')
    title = img.get('title', '')

    # Skip if no meaningful image source
    if not src or 'square' not in src.lower():
        continue

    # Get the full URL
    full_url = urljoin(url, src)

    # Try to find the bird name from alt text, title, or nearby text
    bird_name = alt or title

    # Also check parent elements for bird name
    parent = img.parent
    if parent:
        parent_text = parent.get_text(strip=True)
        if parent_text and len(parent_text) < 100:  # Reasonable length for bird name
            bird_name = parent_text

    if bird_name:
        print(f"Found image: {bird_name[:50]}")
        print(f"  URL: {full_url}")

        # Try to match to our species
        bird_name_lower = bird_name.lower()

        # Direct match attempt
        matched = False
        for sp in our_species:
            common_lower = sp['common_name'].lower()
            scientific_lower = sp['scientific_name'].lower()

            # Check if our species name appears in the found text
            if common_lower in bird_name_lower or scientific_lower in bird_name_lower:
                print(f"  ✓ MATCH: {sp['common_name']}")

                if sp['common_name'] not in bird_photos:
                    bird_photos[sp['common_name']] = {
                        'image_url': full_url.replace('/squares/', '/large/'),  # Get large version
                        'source': 'BirdingPlaces.eu',
                        'source_url': url,
                        'license': 'Various (see source)',
                        'species_name': sp['common_name'],
                        'scientific_name': sp['scientific_name']
                    }
                matched = True
                break

        if not matched:
            print(f"  ⚠️  No match in our species list")
        print()

print()
print("="*80)
print("RESULTS")
print("="*80)
print()
print(f"✓ Found photos for {len(bird_photos)} species")
print()

if bird_photos:
    print("MATCHED SPECIES:")
    for name in sorted(bird_photos.keys()):
        print(f"  • {name}")
    print()

    # Save results
    output_file = 'website/bird_photos_birdingplaces.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(bird_photos, f, indent=2, ensure_ascii=False)

    print(f"Saved to: {output_file}")
else:
    print("⚠️  No photos matched our species list")
    print()
    print("This might be because:")
    print("  1. The page structure is different than expected")
    print("  2. The bird names don't exactly match our species names")
    print("  3. The page uses JavaScript to load content dynamically")
    print()
    print("Let me try a different approach...")

print("="*80)
