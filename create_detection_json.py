#!/usr/bin/env python3
"""
Create JSON file for web viewer
Simplifies data loading in browser
"""

import pandas as pd
import json

print("Creating detection JSON for web viewer...")

# Load CSV
df = pd.read_csv('results/all_detections_with_weather.csv')

# Convert to list of dicts
detections = []
for _, row in df.iterrows():
    detection = {
        'species': row['common_name'],
        'confidence': float(row['confidence']),
        'time': str(row['absolute_timestamp']),
        'file': row['file_stem'],
        'weather': row['weather_summary'],
        'start_s': float(row['start_s']),
        'end_s': float(row['end_s']),
        'suspicious': float(row['confidence']) < 0.50
    }
    detections.append(detection)

# Save as JSON
with open('results/detections.json', 'w') as f:
    json.dump(detections, f, indent=2)

print(f"✅ Created results/detections.json with {len(detections)} detections")

# Also create a smaller file with just best detections for faster loading
high_priority = df[df['confidence'] < 0.50]
best_per_species = df.groupby('common_name').apply(
    lambda x: x.nlargest(3, 'confidence')
).reset_index(drop=True)
top_overall = df.nlargest(50, 'confidence')
combined = pd.concat([high_priority, best_per_species, top_overall]).drop_duplicates()

best_detections = []
for _, row in combined.iterrows():
    detection = {
        'species': row['common_name'],
        'confidence': float(row['confidence']),
        'time': str(row['absolute_timestamp']),
        'file': row['file_stem'],
        'weather': row['weather_summary'],
        'start_s': float(row['start_s']),
        'end_s': float(row['end_s']),
        'suspicious': float(row['confidence']) < 0.50
    }
    best_detections.append(detection)

with open('results/detections_best.json', 'w') as f:
    json.dump(best_detections, f, indent=2)

print(f"✅ Created results/detections_best.json with {len(best_detections)} detections")
