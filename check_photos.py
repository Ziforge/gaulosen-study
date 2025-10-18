#!/usr/bin/env python3
import json

data = json.load(open('website/bird_photos.json'))
print(f'Total species with photos: {len(data)}')
print('\n=== Checking User-Mentioned Species ===')

for sp in ['Graylag Goose', 'Common Sandpiper', 'Eurasian Magpie', 'Yellowhammer', 'Hooded Crow', 'Rook', 'Carrion Crow', 'Mallard']:
    print(f'\n{sp}:')
    info = data.get(sp, {})
    if info:
        print(f'  Photographer: {info.get("photographer", "N/A")}')
        print(f'  Date: {info.get("observation_date", "N/A")}')
        print(f'  License: {info.get("license", "N/A")}')
        print(f'  URL: {info.get("observation_url", "N/A")}')
    else:
        print('  NOT FOUND')
