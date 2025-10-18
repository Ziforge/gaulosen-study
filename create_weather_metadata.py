#!/usr/bin/env python3
"""
Create Weather-Annotated File Metadata
Adds weather conditions to all exports and creates properly named files
"""

import pandas as pd
import os
import shutil
from pathlib import Path

print("=" * 80)
print("🌦️  CREATING WEATHER-ANNOTATED METADATA")
print("=" * 80)
print()

# Weather data for Gaulossen/Trondheim area
WEATHER_DATA = {
    '2025-10-13': {
        'morning': {
            'time': '11:37-23:59',
            'temp_c': '7-11',
            'conditions': 'Light rain, drizzle, fog',
            'wind_ms': '1.7-5.8',
            'humidity': '97-99%',
            'summary': 'Damp, foggy, low visibility'
        }
    },
    '2025-10-14': {
        'night': {
            'time': '00:00-06:00',
            'temp_c': '11',
            'conditions': 'Light rain, passing clouds',
            'wind_ms': '5.0',
            'humidity': '94-98%',
            'summary': 'Light rain overnight'
        },
        'afternoon': {
            'time': '12:25-23:59',
            'temp_c': '11',
            'conditions': 'Broken clouds, improving',
            'wind_ms': '5.0',
            'humidity': '94-98%',
            'summary': 'Clearing, drier'
        }
    },
    '2025-10-15': {
        'night': {
            'time': '00:00-12:00',
            'temp_c': '10-11',
            'conditions': 'Passing clouds, broken clouds',
            'wind_ms': '3.1-7.2',
            'humidity': '91-98%',
            'summary': 'Partly cloudy, unsettled'
        }
    }
}

# File metadata with human-readable names
FILE_METADATA = {
    '245AAA0563ED3DA7_20251013_113753': {
        'date': '2025-10-13',
        'time': '11:37:53',
        'period': 'morning',
        'duration_h': 12.37,
        'readable_name': '2025-10-13_Morning_LightRain_7-11C',
        'description': 'October 13 afternoon/evening recording - Light rain, fog, 7-11°C'
    },
    '245AAA0563ED3DA7_20251014_000000': {
        'date': '2025-10-14',
        'time': '00:00:00',
        'period': 'night',
        'duration_h': 12.42,
        'readable_name': '2025-10-14_Night_LightRain_11C',
        'description': 'October 14 night recording - Light rain, 11°C'
    },
    '245AAA0563ED3DA7_20251014_122526': {
        'date': '2025-10-14',
        'time': '12:25:26',
        'period': 'afternoon',
        'duration_h': 11.58,
        'readable_name': '2025-10-14_Afternoon_BrokenClouds_11C',
        'description': 'October 14 afternoon/evening - Clearing conditions, 11°C'
    },
    '245AAA0563ED3DA7_20251015_000000': {
        'date': '2025-10-15',
        'time': '00:00:00',
        'period': 'night',
        'duration_h': 12.42,
        'readable_name': '2025-10-15_Night_PartlyCloudy_10-11C',
        'description': 'October 15 night recording - Partly cloudy, 10-11°C'
    }
}

# Create weather-annotated metadata CSV
print("📊 Creating weather-annotated metadata...")

metadata_records = []
for file_stem, meta in FILE_METADATA.items():
    date = meta['date']
    period = meta['period']
    weather = WEATHER_DATA[date][period]

    record = {
        'original_filename': f"{file_stem}.WAV",
        'readable_name': meta['readable_name'],
        'date': date,
        'start_time': meta['time'],
        'period': period,
        'duration_hours': meta['duration_h'],
        'description': meta['description'],
        'temperature_c': weather['temp_c'],
        'conditions': weather['conditions'],
        'wind_ms': weather['wind_ms'],
        'humidity': weather['humidity'],
        'weather_summary': weather['summary']
    }
    metadata_records.append(record)

metadata_df = pd.DataFrame(metadata_records)

# Save metadata
output_path = "results/file_metadata_with_weather.csv"
metadata_df.to_csv(output_path, index=False)
print(f"   ✅ {output_path}")
print()

# Display metadata
print("📋 File Metadata with Weather Conditions:")
print("=" * 80)
for _, row in metadata_df.iterrows():
    print(f"\n{row['readable_name']}")
    print(f"   Original: {row['original_filename']}")
    print(f"   Date/Time: {row['date']} {row['start_time']} ({row['period']})")
    print(f"   Duration: {row['duration_hours']} hours")
    print(f"   Weather: {row['conditions']}")
    print(f"   Temp: {row['temperature_c']}°C | Wind: {row['wind_ms']} m/s | Humidity: {row['humidity']}")
    print(f"   Summary: {row['weather_summary']}")

print("\n")

# Add weather to all detection CSVs
print("📊 Adding weather metadata to detection files...")

df = pd.read_csv("results/all_detections.csv")

# Add weather columns
df['weather_temp_c'] = None
df['weather_conditions'] = None
df['weather_summary'] = None

for file_stem, meta in FILE_METADATA.items():
    date = meta['date']
    period = meta['period']
    weather = WEATHER_DATA[date][period]

    mask = df['file_stem'] == file_stem
    df.loc[mask, 'weather_temp_c'] = weather['temp_c']
    df.loc[mask, 'weather_conditions'] = weather['conditions']
    df.loc[mask, 'weather_summary'] = weather['summary']
    df.loc[mask, 'readable_filename'] = meta['readable_name']

# Save updated detections
output_path = "results/all_detections_with_weather.csv"
df.to_csv(output_path, index=False)
print(f"   ✅ {output_path}")

print()
print("=" * 80)
print("✅ WEATHER METADATA COMPLETE")
print("=" * 80)
print()

print("📁 Files created:")
print("   - results/file_metadata_with_weather.csv")
print("   - results/all_detections_with_weather.csv")
print()

print("🌦️  Weather Summary:")
print("   Oct 13: Light rain, fog (7-11°C) - Damp conditions")
print("   Oct 14 night: Light rain (11°C) - Wet overnight")
print("   Oct 14 afternoon: Clearing, broken clouds (11°C) - Improving")
print("   Oct 15 night: Partly cloudy (10-11°C) - Unsettled")
print()

print("📊 Weather Impact on Detections:")
wet_conditions = df[df['weather_conditions'].str.contains('rain|drizzle', case=False, na=False)]
dry_conditions = df[~df['weather_conditions'].str.contains('rain|drizzle', case=False, na=False)]

print(f"   Wet conditions (rain/drizzle): {len(wet_conditions):,} detections")
print(f"   Drier conditions (clouds only): {len(dry_conditions):,} detections")
print(f"   Mean confidence in wet: {wet_conditions['confidence'].mean():.3f}")
print(f"   Mean confidence in dry: {dry_conditions['confidence'].mean():.3f}")
print()
