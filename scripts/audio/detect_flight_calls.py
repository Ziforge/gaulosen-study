#!/usr/bin/env python3
"""
Flight Call Detection for Waterfowl and Migratory Birds
Detects:
1. Pre-flight/Intent calls (accelerating call rate)
2. In-flight contact calls (steady tempo)
3. Landing calls (rapid then decelerating)
4. Nocturnal flight calls (nighttime migration)
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 80)
print("🦆 FLIGHT CALL DETECTION ANALYSIS")
print("=" * 80)
print()

# Load detections
df = pd.read_csv('results/all_detections_with_weather.csv')
df['datetime'] = pd.to_datetime(df['absolute_timestamp'])
df['hour'] = df['datetime'].dt.hour

print(f"📊 Dataset: {len(df)} detections, {df['common_name'].nunique()} species")
print()

# Focus on waterfowl and known flight callers
flight_species = [
    'Graylag Goose', 'Pink-footed Goose', 'Greater White-fronted Goose',
    'Canada Goose', 'Brant', 'Bar-headed Goose', 'Taiga Bean-Goose',
    'Tundra Bean-Goose', 'Whooper Swan', 'Tundra Swan',
    'Common Crane', 'Mallard', 'Common Goldeneye', 'Common Scoter',
    'Eurasian Curlew', 'Northern Lapwing', 'Common Sandpiper',
    'Spotted Crake', 'Water Rail', 'Eurasian Coot'
]

flight_df = df[df['common_name'].isin(flight_species)]
print(f"🎯 Focusing on {len(flight_species)} flight-calling species")
print(f"   Found {len(flight_df)} detections from these species")
print()

# Flight call categories
flight_behaviors = {
    'pre_flight': [],
    'in_flight_contact': [],
    'landing': [],
    'nocturnal_flight': []
}

print("=" * 80)
print("BEHAVIOR 1: Pre-Flight/Intent Calls (Accelerating Tempo)")
print("=" * 80)
print()
print("Acoustic signature:")
print("  • Accelerating call rate (2-5 calls within 10-20 seconds)")
print("  • Calls get progressively closer together")
print("  • Indicates imminent takeoff")
print()

pre_flight_events = 0
for (filename, species), group in flight_df.groupby(['filename', 'common_name']):
    if len(group) < 2:
        continue

    times = sorted(group['start_s'].values)

    # Look for accelerating patterns (calls getting closer together)
    for i in range(len(times) - 2):
        window = times[i:i+3]
        if window[-1] - window[0] < 20:  # 3 calls within 20 seconds
            # Check if interval is decreasing (accelerating)
            interval1 = window[1] - window[0]
            interval2 = window[2] - window[1]

            if interval2 < interval1 and interval1 < 15:  # Accelerating pattern
                pre_flight_events += 1
                burst_detections = group[
                    (group['start_s'] >= window[0]) &
                    (group['start_s'] <= window[-1])
                ]
                for idx, row in burst_detections.iterrows():
                    flight_behaviors['pre_flight'].append({
                        'index': idx,
                        'species': species,
                        'filename': filename,
                        'start_s': row['start_s'],
                        'confidence': row['confidence'],
                        'behavior': 'pre_flight',
                        'event_id': f"{filename}_{species}_{int(window[0])}"
                    })
                break

if pre_flight_events > 0:
    print(f"✅ Detected {pre_flight_events} potential pre-flight/intent call sequences")
    pre_flight_df = pd.DataFrame(flight_behaviors['pre_flight'])
    unique_events = pre_flight_df.groupby('event_id').first().reset_index()
    print()
    print("Top 10 Pre-Flight Events:")
    print("-" * 80)
    for idx, row in unique_events.nlargest(10, 'confidence').iterrows():
        print(f"  {row['species']:40s} | Conf: {row['confidence']:.3f} | "
              f"Time: {int(row['start_s']//3600):02d}:{int((row['start_s']%3600)//60):02d}")
    print()
else:
    print("❌ No pre-flight call patterns detected")
    print()

print("=" * 80)
print("BEHAVIOR 2: In-Flight Contact Calls (Steady Tempo)")
print("=" * 80)
print()
print("Acoustic signature:")
print("  • Regular, evenly-spaced calls (3-10s intervals)")
print("  • ≥4 calls maintaining consistent tempo")
print("  • Indicates birds in flight formation")
print()

in_flight_events = 0
for (filename, species), group in flight_df.groupby(['filename', 'common_name']):
    if len(group) < 4:
        continue

    times = sorted(group['start_s'].values)

    # Look for steady tempo patterns
    for i in range(len(times) - 3):
        window = times[i:i+4]
        if window[-1] - window[0] < 40:  # 4 calls within 40 seconds
            # Check interval consistency (steady tempo)
            intervals = np.diff(window)
            mean_interval = np.mean(intervals)
            interval_std = np.std(intervals)

            # Steady if intervals are 3-10s and consistent (low std deviation)
            if 3 < mean_interval < 10 and interval_std < 3:
                in_flight_events += 1
                burst_detections = group[
                    (group['start_s'] >= window[0]) &
                    (group['start_s'] <= window[-1])
                ]
                for idx, row in burst_detections.iterrows():
                    flight_behaviors['in_flight_contact'].append({
                        'index': idx,
                        'species': species,
                        'filename': filename,
                        'start_s': row['start_s'],
                        'confidence': row['confidence'],
                        'behavior': 'in_flight_contact',
                        'tempo': mean_interval,
                        'event_id': f"{filename}_{species}_{int(window[0])}"
                    })
                break

if in_flight_events > 0:
    print(f"✅ Detected {in_flight_events} potential in-flight contact call sequences")
    in_flight_df = pd.DataFrame(flight_behaviors['in_flight_contact'])
    unique_events = in_flight_df.groupby('event_id').first().reset_index()
    print()
    print("Top 10 In-Flight Contact Events:")
    print("-" * 80)
    for idx, row in unique_events.nlargest(10, 'confidence').iterrows():
        print(f"  {row['species']:40s} | Tempo: {row['tempo']:.1f}s | "
              f"Conf: {row['confidence']:.3f}")
    print()
else:
    print("❌ No in-flight contact call patterns detected")
    print()

print("=" * 80)
print("BEHAVIOR 3: Landing Calls (Fast then Decelerating)")
print("=" * 80)
print()
print("Acoustic signature:")
print("  • Rapid burst (≥3 calls <5s apart)")
print("  • Then longer interval (deceleration)")
print("  • Indicates landing/touchdown")
print()

landing_events = 0
for (filename, species), group in flight_df.groupby(['filename', 'common_name']):
    if len(group) < 4:
        continue

    times = sorted(group['start_s'].values)

    # Look for fast-then-slow patterns (landing)
    for i in range(len(times) - 3):
        window = times[i:i+4]
        if window[-1] - window[0] < 30:
            # Check for deceleration pattern
            interval1 = window[1] - window[0]
            interval2 = window[2] - window[1]
            interval3 = window[3] - window[2]

            # Fast initial calls then slower
            if interval1 < 5 and interval2 < 5 and interval3 > interval2:
                landing_events += 1
                burst_detections = group[
                    (group['start_s'] >= window[0]) &
                    (group['start_s'] <= window[-1])
                ]
                for idx, row in burst_detections.iterrows():
                    flight_behaviors['landing'].append({
                        'index': idx,
                        'species': species,
                        'filename': filename,
                        'start_s': row['start_s'],
                        'confidence': row['confidence'],
                        'behavior': 'landing',
                        'event_id': f"{filename}_{species}_{int(window[0])}"
                    })
                break

if landing_events > 0:
    print(f"✅ Detected {landing_events} potential landing call sequences")
    landing_df = pd.DataFrame(flight_behaviors['landing'])
    unique_events = landing_df.groupby('event_id').first().reset_index()
    print()
    print("Top 10 Landing Events:")
    print("-" * 80)
    for idx, row in unique_events.nlargest(10, 'confidence').iterrows():
        print(f"  {row['species']:40s} | Conf: {row['confidence']:.3f} | "
              f"Time: {int(row['start_s']//3600):02d}:{int((row['start_s']%3600)//60):02d}")
    print()
else:
    print("❌ No landing call patterns detected")
    print()

print("=" * 80)
print("BEHAVIOR 4: Nocturnal Flight Calls (Migration)")
print("=" * 80)
print()
print("Acoustic signature:")
print("  • Calls during deep night hours (22:00-04:00)")
print("  • From migratory species")
print("  • Often single or paired calls")
print()

# Nocturnal flight calls (deep night, likely migration)
nocturnal_flight = flight_df[(flight_df['hour'] >= 22) | (flight_df['hour'] <= 4)]

if len(nocturnal_flight) > 0:
    print(f"✅ Detected {len(nocturnal_flight)} nocturnal flight calls")
    print()

    nocturnal_summary = nocturnal_flight.groupby('common_name').agg({
        'start_s': 'count',
        'confidence': 'mean'
    }).rename(columns={'start_s': 'count', 'confidence': 'avg_conf'})
    nocturnal_summary = nocturnal_summary.sort_values('count', ascending=False)

    print("Top 10 Nocturnal Flight Callers:")
    print("-" * 80)
    for species, row in nocturnal_summary.head(10).iterrows():
        print(f"  {species:40s} | {int(row['count']):3d} calls | "
              f"Avg conf: {row['avg_conf']:.3f}")
    print()

    for idx, row in nocturnal_flight.iterrows():
        flight_behaviors['nocturnal_flight'].append({
            'index': idx,
            'species': row['common_name'],
            'filename': row['filename'],
            'start_s': row['start_s'],
            'confidence': row['confidence'],
            'behavior': 'nocturnal_flight',
            'hour': row['hour']
        })
else:
    print("❌ No nocturnal flight calls detected")
    print()

print("=" * 80)
print("📊 FLIGHT BEHAVIOR SUMMARY")
print("=" * 80)
print()

# Compile all flight behaviors
all_flight_calls = []
for behavior_type, detections in flight_behaviors.items():
    all_flight_calls.extend(detections)

if len(all_flight_calls) > 0:
    flight_summary_df = pd.DataFrame(all_flight_calls)

    print(f"Total flight-related detections: {len(flight_summary_df)}")
    print()

    behavior_counts = flight_summary_df.groupby('behavior').size()
    print("Breakdown by behavior type:")
    for behavior, count in behavior_counts.items():
        behavior_name = behavior.replace('_', ' ').title()
        print(f"  • {behavior_name}: {count} detections")
    print()

    # Species with most flight activity
    species_flight = flight_summary_df.groupby('species').size().sort_values(ascending=False)
    print("Top 10 Species with Flight Activity:")
    print("-" * 80)
    for species, count in species_flight.head(10).items():
        print(f"  {species:40s} | {count:4d} flight calls")
    print()

    # Save results
    output_file = 'results/flight_calls.csv'
    flight_summary_df.to_csv(output_file, index=False)
    print(f"✅ Saved flight call detections to: {output_file}")
    print()

    # Also save species summary
    species_behavior_summary = flight_summary_df.groupby(['species', 'behavior']).size().unstack(fill_value=0)
    species_behavior_summary.to_csv('results/flight_calls_by_species.csv')
    print(f"✅ Saved species-level summary to: results/flight_calls_by_species.csv")
    print()
else:
    print("No flight behaviors detected in the dataset")
    print()

print("=" * 80)
print("✅ FLIGHT CALL ANALYSIS COMPLETE")
print("=" * 80)
print()
