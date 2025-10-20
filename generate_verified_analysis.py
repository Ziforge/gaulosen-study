#!/usr/bin/env python3
"""
Generate behavioral analysis using ONLY verified species data.
Focus on social/flock species and documented interactions.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

print("=" * 80)
print("GAULOSEN VERIFIED SPECIES BEHAVIORAL ANALYSIS")
print("=" * 80)
print()

# Load verified data only
detections = pd.read_csv('results/verified_detections.csv')
verified_species = pd.read_csv('results/verified_species_list.csv')

print(f"Verified species: {len(verified_species)}")
print(f"Verified detections: {len(detections)}")
print()

# Parse timestamps
detections['absolute_timestamp'] = pd.to_datetime(detections['absolute_timestamp'])
detections['hour'] = detections['absolute_timestamp'].dt.hour
detections['date'] = detections['absolute_timestamp'].dt.date

# ============================================================================
# 1. SPECIES INVENTORY
# ============================================================================

print("=" * 80)
print("1. SPECIES INVENTORY (Human-Verified)")
print("=" * 80)
print()

species_counts = detections.groupby('common_name').size().sort_values(ascending=False)

print("Top 20 Most Frequently Detected Species:")
print("-" * 80)
for i, (species, count) in enumerate(species_counts.head(20).items(), 1):
    print(f"{i:2d}. {species:<35s} {count:5d} detections")

print()
print(f"Total: {len(species_counts)} verified species")
print()

# Export
species_summary = pd.DataFrame({
    'species': species_counts.index,
    'detections': species_counts.values,
    'verification_status': 'human_verified'
})
species_summary.to_csv('results/verified_species_summary.csv', index=False)
print("✓ Saved: results/verified_species_summary.csv")
print()

# ============================================================================
# 2. SOCIAL/FLOCK SPECIES ANALYSIS
# ============================================================================

print("=" * 80)
print("2. SOCIAL/FLOCK SPECIES ANALYSIS")
print("=" * 80)
print()

# Define known social/flock species
social_species = {
    'Graylag Goose': 'waterfowl',
    'Pink-footed Goose': 'waterfowl',
    'Greater White-fronted Goose': 'waterfowl',
    'Canada Goose': 'waterfowl',
    'Brant': 'waterfowl',
    'Taiga Bean-Goose': 'waterfowl',
    'Tundra Bean-Goose': 'waterfowl',
    'Bar-headed Goose': 'waterfowl',
    'Whooper Swan': 'waterfowl',
    'Tundra Swan': 'waterfowl',
    'Common Crane': 'large_wader',
    'Hooded Crow': 'corvid',
    'Carrion Crow': 'corvid',
    'Rook': 'corvid',
    'Eurasian Magpie': 'corvid',
    'Common Raven': 'corvid',
    'Eurasian Jay': 'corvid',
    'Snow Bunting': 'passerine_flock',
    'Brambling': 'passerine_flock',
    'Common Redpoll': 'passerine_flock',
    'Fieldfare': 'passerine_flock',
    'Redwing': 'passerine_flock',
    'Lapland Longspur': 'passerine_flock',
    'Black-headed Gull': 'gull',
    'Herring Gull': 'gull',
    'Black-legged Kittiwake': 'gull',
    'Northern Lapwing': 'shorebird',
    'European Golden-Plover': 'shorebird',
    'Black-bellied Plover': 'shorebird',
}

social_detections = detections[detections['common_name'].isin(social_species.keys())].copy()
social_detections['guild'] = social_detections['common_name'].map(social_species)

print("Social/Flock Species Categories:")
print("-" * 80)

for guild in ['waterfowl', 'corvid', 'passerine_flock', 'gull', 'shorebird', 'large_wader']:
    guild_data = social_detections[social_detections['guild'] == guild]
    guild_species = guild_data['common_name'].nunique()
    guild_detections = len(guild_data)

    print(f"\n{guild.upper().replace('_', ' ')}:")
    print(f"  Species: {guild_species}")
    print(f"  Detections: {guild_detections}")

    if guild_detections > 0:
        top_species = guild_data.groupby('common_name').size().sort_values(ascending=False).head(3)
        print(f"  Top species:")
        for species, count in top_species.items():
            print(f"    - {species}: {count}")

print()
print(f"Total social species: {social_detections['common_name'].nunique()}")
print(f"Total social detections: {len(social_detections)} ({len(social_detections)/len(detections)*100:.1f}% of all detections)")
print()

# Export
social_summary = social_detections.groupby(['guild', 'common_name']).size().reset_index(name='detections')
social_summary = social_summary.sort_values(['guild', 'detections'], ascending=[True, False])
social_summary.to_csv('results/verified_social_species.csv', index=False)
print("✓ Saved: results/verified_social_species.csv")
print()

# ============================================================================
# 3. TEMPORAL CLUSTERING (Flock Activity)
# ============================================================================

print("=" * 80)
print("3. TEMPORAL CLUSTERING ANALYSIS (Flock Detection)")
print("=" * 80)
print()

# Find temporal clusters (multiple detections within 5 minutes = potential flock)
def find_temporal_clusters(species_data, time_window_minutes=5):
    """Find clusters of detections suggesting flock activity"""
    if len(species_data) < 2:
        return []

    species_data = species_data.sort_values('absolute_timestamp')
    clusters = []
    current_cluster = [species_data.iloc[0]]

    for i in range(1, len(species_data)):
        current = species_data.iloc[i]
        prev = current_cluster[-1]

        time_diff = (current['absolute_timestamp'] - prev['absolute_timestamp']).total_seconds() / 60

        if time_diff <= time_window_minutes:
            current_cluster.append(current)
        else:
            if len(current_cluster) >= 3:  # At least 3 detections = likely flock
                clusters.append(current_cluster)
            current_cluster = [current]

    if len(current_cluster) >= 3:
        clusters.append(current_cluster)

    return clusters

print("Flock Activity Detection (3+ calls within 5 minutes):")
print("-" * 80)

flock_summary = []

for species in social_species.keys():
    species_data = detections[detections['common_name'] == species]

    if len(species_data) < 3:
        continue

    clusters = find_temporal_clusters(species_data, time_window_minutes=5)

    if clusters:
        total_flock_calls = sum(len(cluster) for cluster in clusters)
        print(f"\n{species}:")
        print(f"  Flock events detected: {len(clusters)}")
        print(f"  Total calls in flocks: {total_flock_calls}/{len(species_data)} ({total_flock_calls/len(species_data)*100:.1f}%)")
        print(f"  Largest flock event: {max(len(c) for c in clusters)} calls")

        # Show largest flock event
        largest = max(clusters, key=len)
        start_time = largest[0]['absolute_timestamp']
        end_time = largest[-1]['absolute_timestamp']
        duration = (end_time - start_time).total_seconds() / 60
        print(f"  Example: {len(largest)} calls over {duration:.1f} minutes at {start_time.strftime('%Y-%m-%d %H:%M')}")

        flock_summary.append({
            'species': species,
            'guild': social_species[species],
            'flock_events': len(clusters),
            'total_calls': len(species_data),
            'flock_calls': total_flock_calls,
            'flock_percentage': total_flock_calls/len(species_data)*100,
            'largest_event': max(len(c) for c in clusters)
        })

flock_df = pd.DataFrame(flock_summary)
if not flock_df.empty:
    flock_df = flock_df.sort_values('flock_events', ascending=False)
    flock_df.to_csv('results/verified_flock_activity.csv', index=False)
    print()
    print("✓ Saved: results/verified_flock_activity.csv")

print()

# ============================================================================
# 4. SPECIES CO-OCCURRENCE (Within Same Time Window)
# ============================================================================

print("=" * 80)
print("4. SPECIES CO-OCCURRENCE ANALYSIS")
print("=" * 80)
print()

# Find species detected within same 10-minute window
time_window = timedelta(minutes=10)
detections_sorted = detections.sort_values('absolute_timestamp')

co_occurrences = []

for i in range(len(detections_sorted)):
    det1 = detections_sorted.iloc[i]

    # Find all detections within time window
    window_start = det1['absolute_timestamp']
    window_end = window_start + time_window

    window_detections = detections_sorted[
        (detections_sorted['absolute_timestamp'] >= window_start) &
        (detections_sorted['absolute_timestamp'] <= window_end) &
        (detections_sorted['common_name'] != det1['common_name'])
    ]

    for _, det2 in window_detections.iterrows():
        pair = tuple(sorted([det1['common_name'], det2['common_name']]))
        co_occurrences.append({
            'species_1': pair[0],
            'species_2': pair[1],
            'timestamp': det1['absolute_timestamp'],
            'time_diff_seconds': (det2['absolute_timestamp'] - det1['absolute_timestamp']).total_seconds()
        })

if co_occurrences:
    co_occur_df = pd.DataFrame(co_occurrences)

    # Count co-occurrence frequency
    co_occur_summary = co_occur_df.groupby(['species_1', 'species_2']).size().reset_index(name='co_occurrence_count')
    co_occur_summary = co_occur_summary.sort_values('co_occurrence_count', ascending=False)

    print("Top 20 Species Co-occurrences (within 10-minute windows):")
    print("-" * 80)

    for i, row in co_occur_summary.head(20).iterrows():
        print(f"{row['species_1']:<30s} + {row['species_2']:<30s}: {row['co_occurrence_count']:4d} times")

    co_occur_summary.to_csv('results/verified_co_occurrences.csv', index=False)
    print()
    print("✓ Saved: results/verified_co_occurrences.csv")

print()

# ============================================================================
# 5. HOURLY ACTIVITY PATTERNS
# ============================================================================

print("=" * 80)
print("5. HOURLY ACTIVITY PATTERNS (Top 10 Species)")
print("=" * 80)
print()

top_10_species = species_counts.head(10).index

hourly_activity = detections[detections['common_name'].isin(top_10_species)].groupby(
    ['common_name', 'hour']
).size().reset_index(name='detections')

# Pivot for easier viewing
hourly_pivot = hourly_activity.pivot(index='common_name', columns='hour', values='detections').fillna(0)

print("Activity by Hour (24-hour format):")
print("-" * 80)
print(hourly_pivot.to_string())

hourly_activity.to_csv('results/verified_hourly_activity.csv', index=False)
print()
print("✓ Saved: results/verified_hourly_activity.csv")
print()

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print()
print("Generated Files:")
print("  1. results/verified_species_summary.csv - Species inventory")
print("  2. results/verified_social_species.csv - Social/flock species breakdown")
print("  3. results/verified_flock_activity.csv - Temporal clustering analysis")
print("  4. results/verified_co_occurrences.csv - Species co-occurrence patterns")
print("  5. results/verified_hourly_activity.csv - Temporal activity patterns")
print()
print("Key Findings:")
print(f"  - {len(verified_species)} human-verified species")
print(f"  - {len(detections)} verified detections")
print(f"  - {social_detections['common_name'].nunique()} social/flock species")
print(f"  - {len(flock_summary) if flock_summary else 0} species showing flock behavior")
print()
print("=" * 80)
