#!/usr/bin/env python3
"""
Comprehensive Behavioral Analysis for Bird Calls
Detects and categorizes various vocal behaviors:
1. Flock/Social Calls (contact calls, gregarious species)
2. Dawn Chorus Activity
3. Alarm/Mobbing Behavior (rapid bursts)
4. Isolated Calls
5. Temporal Patterns (nighttime vs daytime)
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 80)
print("🎯 COMPREHENSIVE BEHAVIORAL ANALYSIS")
print("=" * 80)
print()

# Load detections
df = pd.read_csv('results/all_detections_with_weather.csv')
df['datetime'] = pd.to_datetime(df['absolute_timestamp'])
df['hour'] = df['datetime'].dt.hour

print(f"📊 Dataset: {len(df)} detections, {df['common_name'].nunique()} species")
print()

# Behavior categories
behaviors = {
    'flock_social': [],
    'dawn_chorus': [],
    'alarm_mobbing': [],
    'isolated': [],
    'nighttime': [],
    'all_detections': []
}

print("=" * 80)
print("BEHAVIOR 1: Flock/Social Calls (Contact Calls)")
print("=" * 80)
print()
print("Criteria:")
print("  • ≥3 calls from same species in same recording")
print("  • High temporal clustering (multiple calls within 60s)")
print("  • Indicates gregarious/social species")
print()

for (filename, species), group in df.groupby(['filename', 'common_name']):
    if len(group) < 3:  # Lowered from 5 to 3
        continue

    times = group['start_s'].values
    time_span = times.max() - times.min()

    if time_span == 0:
        continue

    # Calls per minute
    calls_per_minute = len(group) / (time_span / 60)

    # Find temporal clusters (calls within 60s - increased from 30s)
    time_diffs = np.diff(np.sort(times))
    close_calls = np.sum(time_diffs < 60)

    # Flock score (lowered threshold)
    avg_confidence = group['confidence'].mean()
    flock_score = calls_per_minute * (close_calls / len(group)) * avg_confidence

    # More lenient criteria
    if calls_per_minute > 1.0 or close_calls > 2:  # Lowered from 2.0 and 3
        for idx, row in group.iterrows():
            behaviors['flock_social'].append({
                'index': idx,
                'species': species,
                'filename': filename,
                'start_s': row['start_s'],
                'confidence': row['confidence'],
                'behavior': 'flock_social',
                'num_calls': len(group),
                'calls_per_minute': calls_per_minute,
                'flock_score': flock_score
            })

flock_df = pd.DataFrame(behaviors['flock_social'])
if len(flock_df) > 0:
    # Get unique flock events
    unique_flocks = flock_df.groupby(['filename', 'species']).first().reset_index()
    print(f"✅ Detected {len(unique_flocks)} flock/social call events")
    print(f"   Total detections in flocks: {len(flock_df)}")
    print()
    print("Top 10 Flock Events:")
    print("-" * 80)
    for idx, row in unique_flocks.nlargest(10, 'flock_score').iterrows():
        print(f"  {row['species']:30s} | {int(row['num_calls']):3d} calls | "
              f"{row['calls_per_minute']:5.1f} calls/min | Score: {row['flock_score']:6.1f}")
    print()
else:
    print("❌ No flock behavior detected")
    print()

print("=" * 80)
print("BEHAVIOR 2: Dawn Chorus (Early Morning Peaks)")
print("=" * 80)
print()
print("Criteria:")
print("  • High vocal activity 04:00-08:00")
print("  • Species with synchronized morning singing")
print()

dawn_hours = df[(df['hour'] >= 4) & (df['hour'] <= 8)]
dawn_species = dawn_hours.groupby('common_name').size().sort_values(ascending=False)

if len(dawn_species) > 0:
    print(f"✅ Dawn chorus participants: {len(dawn_species)} species")
    print()
    print("Top 15 Dawn Chorus Species:")
    print("-" * 80)
    for species, count in dawn_species.head(15).items():
        pct = count / len(dawn_hours) * 100
        print(f"  {species:40s} | {count:4d} calls ({pct:5.1f}%)")
    print()

    # Add to behaviors
    for idx, row in dawn_hours.iterrows():
        behaviors['dawn_chorus'].append({
            'index': idx,
            'species': row['common_name'],
            'filename': row['filename'],
            'start_s': row['start_s'],
            'confidence': row['confidence'],
            'behavior': 'dawn_chorus',
            'hour': row['hour']
        })

print("=" * 80)
print("BEHAVIOR 3: Alarm/Mobbing Calls (Rapid Bursts)")
print("=" * 80)
print()
print("Criteria:")
print("  • ≥4 rapid calls (<10s apart)")
print("  • Short duration bursts indicating alarm response")
print()

alarm_count = 0
for (filename, species), group in df.groupby(['filename', 'common_name']):
    if len(group) < 4:
        continue

    times = sorted(group['start_s'].values)

    # Look for rapid bursts (≥4 calls within 40s window)
    for i in range(len(times) - 3):
        window_times = times[i:i+4]
        if window_times[-1] - window_times[0] < 40:  # 4 calls within 40s
            # Check if calls are rapid (average <10s apart)
            diffs = np.diff(window_times)
            if np.mean(diffs) < 10:
                alarm_count += 1
                # Get detections in this burst
                burst_detections = group[
                    (group['start_s'] >= window_times[0]) &
                    (group['start_s'] <= window_times[-1])
                ]
                for idx, row in burst_detections.iterrows():
                    behaviors['alarm_mobbing'].append({
                        'index': idx,
                        'species': species,
                        'filename': filename,
                        'start_s': row['start_s'],
                        'confidence': row['confidence'],
                        'behavior': 'alarm_mobbing',
                        'burst_id': f"{filename}_{species}_{int(window_times[0])}"
                    })
                break  # Only count each burst once

if alarm_count > 0:
    print(f"✅ Detected {alarm_count} potential alarm/mobbing events")
    alarm_df = pd.DataFrame(behaviors['alarm_mobbing'])
    unique_bursts = alarm_df.groupby('burst_id').first().reset_index()
    print()
    print("Top 10 Alarm/Mobbing Events:")
    print("-" * 80)
    for idx, row in unique_bursts.nlargest(10, 'confidence').iterrows():
        print(f"  {row['species']:40s} | Conf: {row['confidence']:.3f}")
    print()
else:
    print("❌ No alarm/mobbing behavior detected")
    print()

print("=" * 80)
print("BEHAVIOR 4: Nighttime Calls (Nocturnal Activity)")
print("=" * 80)
print()
print("Criteria: Calls between 20:00-06:00")
print()

night_calls = df[(df['hour'] >= 20) | (df['hour'] <= 6)]
if len(night_calls) > 0:
    print(f"✅ Nighttime activity: {len(night_calls)} calls, {night_calls['common_name'].nunique()} species")
    print()
    night_species = night_calls.groupby('common_name').size().sort_values(ascending=False)
    print("Top 10 Nocturnal Species:")
    print("-" * 80)
    for species, count in night_species.head(10).items():
        avg_conf = night_calls[night_calls['common_name'] == species]['confidence'].mean()
        print(f"  {species:40s} | {count:4d} calls | Avg conf: {avg_conf:.3f}")
    print()

    for idx, row in night_calls.iterrows():
        behaviors['nighttime'].append({
            'index': idx,
            'species': row['common_name'],
            'filename': row['filename'],
            'start_s': row['start_s'],
            'confidence': row['confidence'],
            'behavior': 'nighttime',
            'hour': row['hour']
        })

print("=" * 80)
print("📋 ORGANIZED BY SPECIES - TOP 3 EXAMPLES EACH")
print("=" * 80)
print()

# Create comprehensive dataframe with all detections
for idx, row in df.iterrows():
    behaviors['all_detections'].append({
        'index': idx,
        'species': row['common_name'],
        'filename': row['filename'],
        'start_s': row['start_s'],
        'end_s': row['end_s'],
        'confidence': row['confidence'],
        'weather': row['weather_summary'],
        'hour': row['hour'],
        'file_stem': row['file_stem']
    })

all_df = pd.DataFrame(behaviors['all_detections'])

# Get top 3 per species by confidence
all_df_sorted = all_df.sort_values(['species', 'confidence'], ascending=[True, False])
top3_per_species = all_df_sorted.groupby('species').head(3).reset_index(drop=True)

print(f"Selected top 3 examples for {top3_per_species['species'].nunique()} species")
print(f"Total selections: {len(top3_per_species)}")
print()

# Save organized output
output_file = 'results/top3_per_species.csv'
top3_per_species.to_csv(output_file, index=False)
print(f"✅ Saved to: {output_file}")
print()

# Create species summary
print("=" * 80)
print("SPECIES SUMMARY (Top 3 Examples Each)")
print("=" * 80)
print()

species_summary = []
for species in sorted(top3_per_species['species'].unique()):
    species_data = top3_per_species[top3_per_species['species'] == species]

    # Check behaviors
    in_flock = len(flock_df[flock_df['species'] == species]) if len(flock_df) > 0 else 0
    in_dawn = len([b for b in behaviors['dawn_chorus'] if b['species'] == species])
    in_alarm = len([b for b in behaviors['alarm_mobbing'] if b['species'] == species])
    in_night = len([b for b in behaviors['nighttime'] if b['species'] == species])

    behaviors_str = []
    if in_flock > 0:
        behaviors_str.append(f"Flock({in_flock})")
    if in_dawn > 0:
        behaviors_str.append(f"Dawn({in_dawn})")
    if in_alarm > 0:
        behaviors_str.append(f"Alarm({in_alarm})")
    if in_night > 0:
        behaviors_str.append(f"Night({in_night})")

    behavior_tags = ", ".join(behaviors_str) if behaviors_str else "Isolated"

    species_summary.append({
        'species': species,
        'top3_count': len(species_data),
        'max_conf': species_data['confidence'].max(),
        'avg_conf': species_data['confidence'].mean(),
        'behaviors': behavior_tags
    })

    print(f"\n{species}")
    print("-" * 80)
    print(f"Behaviors: {behavior_tags}")
    print(f"\nTop 3 Examples:")
    for i, (idx, row) in enumerate(species_data.iterrows(), 1):
        hour_str = f"{int(row['hour']):02d}:00"
        print(f"  {i}. Conf: {row['confidence']:.3f} | Time: {hour_str} | "
              f"{row['weather']} | File: {row['file_stem']}")

# Save species summary
species_summary_df = pd.DataFrame(species_summary)
species_summary_df.to_csv('results/species_summary.csv', index=False)

print()
print("=" * 80)
print("✅ ANALYSIS COMPLETE")
print("=" * 80)
print()

print("Files created:")
print(f"  • results/top3_per_species.csv - Top 3 detections per species")
print(f"  • results/species_summary.csv - Species summary with behaviors")
print()

print("Behavioral Summary:")
print(f"  • Flock/Social calls: {len(flock_df)} detections" if len(flock_df) > 0 else "  • Flock/Social calls: 0 detections")
print(f"  • Dawn chorus: {len(behaviors['dawn_chorus'])} detections")
print(f"  • Alarm/mobbing: {len(behaviors['alarm_mobbing'])} detections")
print(f"  • Nighttime calls: {len(behaviors['nighttime'])} detections")
print()
