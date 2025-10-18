#!/usr/bin/env python3
"""
Migration Timing Analysis
Analyzes temporal patterns during October 13-15, 2025 migration window
Detects:
1. Overnight migration activity (20:00-06:00)
2. Stopover vs. passage migrants
3. Species turnover patterns
4. Peak migration hours
5. Migratory vs. resident species activity
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

print("=" * 80)
print("🦅 MIGRATION TIMING ANALYSIS")
print("=" * 80)
print()

# Load data
df = pd.read_csv('results/all_detections_with_weather.csv')
df['datetime'] = pd.to_datetime(df['absolute_timestamp'])
df['hour'] = df['datetime'].dt.hour
df['date'] = df['datetime'].dt.date
df['day_of_study'] = (df['datetime'] - df['datetime'].min()).dt.total_seconds() / 86400

print(f"📊 Dataset: {len(df)} detections, {df['common_name'].nunique()} species")
print(f"   Recording period: {df['datetime'].min()} to {df['datetime'].max()}")
print(f"   Duration: {(df['datetime'].max() - df['datetime'].min()).total_seconds() / 3600:.1f} hours")
print()

# Known migratory species (long-distance migrants)
migratory_species = [
    'Pink-footed Goose', 'Greater White-fronted Goose', 'Graylag Goose',
    'Whooper Swan', 'Tundra Swan', 'Brant', 'Taiga Bean-Goose', 'Tundra Bean-Goose',
    'Common Crane', 'Eurasian Curlew', 'Northern Lapwing', 'Common Sandpiper',
    'Redwing', 'Fieldfare', 'Ring Ouzel', 'Common Chiffchaff',
    'Yellow-browed Warbler', 'Arctic Warbler', 'Red-throated Pipit',
    'Water Pipit', 'Meadow Pipit', 'Tree Pipit', 'Yellow Wagtail',
    'Common Scoter', 'Common Goldeneye', 'Mallard'
]

# Partial migrants (some populations migrate)
partial_migrants = [
    'Great Bittern', 'Eurasian Woodcock', 'Common Snipe', 'Great Snipe',
    'Spotted Crake', 'Water Rail', 'Eurasian Coot', 'Common Moorhen',
    'Song Thrush', 'Common Blackbird', 'European Robin', 'Common Starling'
]

# Residents (mostly sedentary)
resident_species = [
    'Hooded Crow', 'Carrion Crow', 'Common Raven', 'Eurasian Magpie',
    'Eurasian Jay', 'Great Spotted Woodpecker', 'Lesser Spotted Woodpecker',
    'Black Woodpecker', 'Willow Tit', 'Great Tit', 'Blue Tit'
]

df['migration_status'] = df['common_name'].apply(
    lambda x: 'Migrant' if x in migratory_species else
              'Partial' if x in partial_migrants else
              'Resident' if x in resident_species else
              'Unknown'
)

print("Species Classification:")
print("-" * 80)
migrant_count = df[df['migration_status'] == 'Migrant']['common_name'].nunique()
partial_count = df[df['migration_status'] == 'Partial']['common_name'].nunique()
resident_count = df[df['migration_status'] == 'Resident']['common_name'].nunique()
unknown_count = df[df['migration_status'] == 'Unknown']['common_name'].nunique()

print(f"  Long-distance migrants: {migrant_count} species")
print(f"  Partial migrants:       {partial_count} species")
print(f"  Resident species:       {resident_count} species")
print(f"  Unknown status:         {unknown_count} species")
print()

# ============================================================================
# 1. NOCTURNAL MIGRATION ACTIVITY
# ============================================================================
print("=" * 80)
print("1. NOCTURNAL MIGRATION ACTIVITY (20:00-06:00)")
print("=" * 80)
print()

nocturnal_hours = list(range(20, 24)) + list(range(0, 7))
nocturnal_df = df[df['hour'].isin(nocturnal_hours)]

print(f"Nocturnal detections: {len(nocturnal_df)} ({len(nocturnal_df)/len(df)*100:.1f}% of all calls)")
print()

nocturnal_by_status = nocturnal_df.groupby('migration_status').agg({
    'common_name': 'count'
}).rename(columns={'common_name': 'detections'})

print("Nocturnal Activity by Migration Status:")
print("-" * 80)
for status, row in nocturnal_by_status.iterrows():
    pct = row['detections'] / len(nocturnal_df) * 100
    print(f"  {status:15s} | {int(row['detections']):5d} detections ({pct:5.1f}%)")
print()

# Top nocturnal migrants
nocturnal_migrants = nocturnal_df[nocturnal_df['migration_status'] == 'Migrant']
if len(nocturnal_migrants) > 0:
    nocturnal_species = nocturnal_migrants.groupby('common_name').agg({
        'start_s': 'count',
        'confidence': 'mean'
    }).rename(columns={'start_s': 'detections'}).sort_values('detections', ascending=False)

    print("Top 15 Nocturnal Migrant Species:")
    print("-" * 80)
    for species, row in nocturnal_species.head(15).iterrows():
        print(f"  {species:40s} | {int(row['detections']):4d} calls | Conf: {row['confidence']:.3f}")
    print()

# ============================================================================
# 2. HOURLY MIGRATION INTENSITY
# ============================================================================
print("=" * 80)
print("2. MIGRATION INTENSITY BY HOUR")
print("=" * 80)
print()

hourly_migrants = df[df['migration_status'] == 'Migrant'].groupby('hour').size()
hourly_total = df.groupby('hour').size()

print("Hour-by-Hour Migration Activity:")
print("-" * 80)
print(f"{'Hour':<6} {'Migrants':<10} {'Total':<10} {'% Migrants':<12} {'Pattern'}")
print("-" * 80)

max_migrants = hourly_migrants.max() if len(hourly_migrants) > 0 else 1

for hour in range(24):
    migrants = hourly_migrants.get(hour, 0)
    total = hourly_total.get(hour, 0)
    pct = (migrants / total * 100) if total > 0 else 0

    bar_length = int(migrants / max_migrants * 40) if migrants > 0 else 0
    bar = '█' * bar_length

    # Mark peak migration hours
    marker = " 🔥" if migrants > max_migrants * 0.7 else ""

    print(f"{hour:02d}:00  {int(migrants):7d}    {int(total):7d}    {pct:5.1f}%       {bar}{marker}")

print()

# Identify peak migration windows
peak_hours = hourly_migrants[hourly_migrants > hourly_migrants.quantile(0.75)].index.tolist()
print(f"Peak Migration Hours: {', '.join([f'{h:02d}:00' for h in sorted(peak_hours)])}")
print()

# ============================================================================
# 3. SPECIES TURNOVER (Daily Patterns)
# ============================================================================
print("=" * 80)
print("3. SPECIES TURNOVER PATTERNS")
print("=" * 80)
print()

# Calculate species richness per 6-hour block
df['time_block'] = df['hour'] // 6  # 0=00-06, 1=06-12, 2=12-18, 3=18-24
df['day_block'] = df['datetime'].dt.date.astype(str) + '_' + df['time_block'].astype(str)

turnover = df.groupby('day_block').agg({
    'common_name': lambda x: len(set(x)),
    'start_s': 'count'
}).rename(columns={'common_name': 'species_richness', 'start_s': 'detections'})

print("Species Richness by Time Block (6-hour windows):")
print("-" * 80)
print(f"{'Date':<12} {'Time Block':<20} {'Species':<10} {'Detections'}")
print("-" * 80)

time_block_names = {0: '00:00-06:00 (Night)', 1: '06:00-12:00 (Morning)',
                    2: '12:00-18:00 (Afternoon)', 3: '18:00-00:00 (Evening)'}

for block_id, row in turnover.iterrows():
    date_str = block_id.split('_')[0]
    block_num = int(block_id.split('_')[1])
    block_name = time_block_names[block_num]

    print(f"{date_str}  {block_name:20s}  {int(row['species_richness']):3d}          {int(row['detections']):5d}")

print()

# ============================================================================
# 4. STOPOVER vs PASSAGE ANALYSIS
# ============================================================================
print("=" * 80)
print("4. STOPOVER vs PASSAGE MIGRANTS")
print("=" * 80)
print()
print("Methodology:")
print("  • STOPOVER: Detected across multiple time blocks (feeding/resting)")
print("  • PASSAGE: Single time block detection (flying over)")
print()

migrant_df = df[df['migration_status'] == 'Migrant']
species_blocks = migrant_df.groupby('common_name')['day_block'].nunique()

stopover_species = species_blocks[species_blocks >= 3].sort_values(ascending=False)
passage_species = species_blocks[species_blocks == 1].sort_values(ascending=False)

print(f"Stopover Species (≥3 time blocks): {len(stopover_species)}")
print("-" * 80)
for species, blocks in stopover_species.head(15).items():
    species_df = migrant_df[migrant_df['common_name'] == species]
    duration_hours = (species_df['datetime'].max() - species_df['datetime'].min()).total_seconds() / 3600
    print(f"  {species:40s} | {int(blocks)} blocks | {duration_hours:5.1f}h duration")
print()

print(f"Passage Species (single time block): {len(passage_species)}")
print("-" * 80)
for species, blocks in passage_species.head(15).items():
    species_df = migrant_df[migrant_df['common_name'] == species]
    detections = len(species_df)
    avg_conf = species_df['confidence'].mean()
    print(f"  {species:40s} | {detections:3d} calls | Conf: {avg_conf:.3f}")
print()

# ============================================================================
# 5. MIGRATION WAVES (Temporal Clustering)
# ============================================================================
print("=" * 80)
print("5. MIGRATION WAVE DETECTION")
print("=" * 80)
print()
print("Detecting concentrated bursts of migrant activity...")
print()

# Calculate rolling 1-hour migration rate
df_sorted = df.sort_values('datetime')
df_sorted['is_migrant'] = df_sorted['migration_status'] == 'Migrant'

# Group by hour and calculate migration intensity
hourly_migration = df_sorted.groupby(df_sorted['datetime'].dt.floor('H')).agg({
    'is_migrant': 'sum',
    'common_name': 'count'
}).rename(columns={'is_migrant': 'migrants', 'common_name': 'total'})

hourly_migration['migration_rate'] = hourly_migration['migrants'] / hourly_migration['total']
hourly_migration = hourly_migration[hourly_migration['total'] >= 5]  # At least 5 detections

# Detect waves (migration rate > 75th percentile)
threshold = hourly_migration['migration_rate'].quantile(0.75)
waves = hourly_migration[hourly_migration['migration_rate'] >= threshold]

if len(waves) > 0:
    print(f"✅ Detected {len(waves)} migration wave periods")
    print()
    print("Top 10 Migration Waves:")
    print("-" * 80)
    for timestamp, row in waves.nlargest(10, 'migration_rate').iterrows():
        print(f"  {timestamp} | {int(row['migrants']):3d}/{int(row['total']):3d} migrants ({row['migration_rate']*100:5.1f}%)")
    print()
else:
    print("No concentrated migration waves detected")
    print()

# ============================================================================
# 6. MIGRATION SUMMARY STATISTICS
# ============================================================================
print("=" * 80)
print("6. MIGRATION SUMMARY")
print("=" * 80)
print()

total_migrants = df[df['migration_status'] == 'Migrant']
print(f"Total Migrant Detections: {len(total_migrants)} ({len(total_migrants)/len(df)*100:.1f}%)")
print(f"Migrant Species: {total_migrants['common_name'].nunique()}")
print()

print("Top 10 Most Active Migrants:")
print("-" * 80)
top_migrants = total_migrants.groupby('common_name').agg({
    'start_s': 'count',
    'confidence': 'mean',
    'day_block': 'nunique'
}).rename(columns={'start_s': 'detections', 'day_block': 'time_blocks'})
top_migrants = top_migrants.sort_values('detections', ascending=False)

for species, row in top_migrants.head(10).iterrows():
    status = "Stopover" if row['time_blocks'] >= 3 else "Passage"
    print(f"  {species:40s} | {int(row['detections']):4d} calls | {status:8s} | Conf: {row['confidence']:.3f}")
print()

# ============================================================================
# SAVE RESULTS
# ============================================================================
print("=" * 80)
print("💾 SAVING RESULTS")
print("=" * 80)
print()

# Save detailed migration data
migration_data = df[df['migration_status'] == 'Migrant'].copy()
migration_data.to_csv('results/migration_detections.csv', index=False)
print("✅ Saved migration detections: results/migration_detections.csv")

# Save species classification
species_classification = df.groupby('common_name').agg({
    'migration_status': 'first',
    'start_s': 'count',
    'day_block': 'nunique'
}).rename(columns={'start_s': 'total_detections', 'day_block': 'time_blocks'})
species_classification['behavior'] = species_classification.apply(
    lambda x: 'Stopover' if x['time_blocks'] >= 3 else 'Passage' if x['migration_status'] == 'Migrant' else 'Resident',
    axis=1
)
species_classification.to_csv('results/species_migration_status.csv')
print("✅ Saved species classification: results/species_migration_status.csv")

# Save hourly migration intensity
hourly_summary = pd.DataFrame({
    'hour': range(24),
    'migrants': [hourly_migrants.get(h, 0) for h in range(24)],
    'total': [hourly_total.get(h, 0) for h in range(24)]
})
hourly_summary['migration_rate'] = hourly_summary['migrants'] / hourly_summary['total']
hourly_summary.to_csv('results/hourly_migration_intensity.csv', index=False)
print("✅ Saved hourly summary: results/hourly_migration_intensity.csv")

print()
print("=" * 80)
print("✅ MIGRATION TIMING ANALYSIS COMPLETE")
print("=" * 80)
print()
