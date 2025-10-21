#!/usr/bin/env python3
"""
Comprehensive behavioral analysis using ONLY verified species data.
Includes: migration, dawn/dusk, nocturnal, social, temporal, ecological patterns.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
from pathlib import Path

print("=" * 80)
print("GAULOSEN COMPREHENSIVE BEHAVIORAL ANALYSIS")
print("Human-Verified Species Only")
print("=" * 80)
print()

# Load verified data
detections = pd.read_csv('results/verified_detections.csv')
verified_species = pd.read_csv('results/verified_species_list.csv')

print(f"Verified species: {len(verified_species)}")
print(f"Verified detections: {len(detections)}")
print(f"Recording period: {detections['recording_date'].min()} to {detections['recording_date'].max()}")
print()

# Parse timestamps
detections['absolute_timestamp'] = pd.to_datetime(detections['absolute_timestamp'])
detections['hour'] = detections['absolute_timestamp'].dt.hour
detections['date'] = detections['absolute_timestamp'].dt.date
detections['time'] = detections['absolute_timestamp'].dt.time

# ============================================================================
# 1. MIGRATION PATTERNS
# ============================================================================

print("=" * 80)
print("1. MIGRATION PATTERNS (Migratory vs. Resident Species)")
print("=" * 80)
print()

# Define migratory species (known migrants in Norway)
migratory_species = {
    # Waterfowl migrants
    'Pink-footed Goose': 'arctic_migrant',
    'Brant': 'arctic_migrant',
    'Greater White-fronted Goose': 'arctic_migrant',
    'Taiga Bean-Goose': 'arctic_migrant',
    'Tundra Bean-Goose': 'arctic_migrant',
    'Whooper Swan': 'arctic_migrant',
    'Tundra Swan': 'arctic_migrant',

    # Common Crane - notable migrant
    'Common Crane': 'long_distance_migrant',

    # Wader migrants
    'Great Snipe': 'long_distance_migrant',
    'Common Snipe': 'partial_migrant',
    'Eurasian Woodcock': 'partial_migrant',
    'Northern Lapwing': 'partial_migrant',
    'Eurasian Curlew': 'partial_migrant',
    'Common Sandpiper': 'short_distance_migrant',
    'Eurasian Oystercatcher': 'partial_migrant',
    'Dunlin': 'arctic_migrant',
    'Black-bellied Plover': 'arctic_migrant',
    'European Golden-Plover': 'partial_migrant',

    # Passerine migrants
    'Snow Bunting': 'arctic_migrant',
    'Lapland Longspur': 'arctic_migrant',
    'Brambling': 'short_distance_migrant',
    'Redwing': 'short_distance_migrant',
    'Fieldfare': 'short_distance_migrant',
    'Common Grasshopper-Warbler': 'long_distance_migrant',
    'Arctic Warbler': 'long_distance_migrant',
    'River Warbler': 'long_distance_migrant',
    'Red-breasted Flycatcher': 'long_distance_migrant',
    'Tree Pipit': 'long_distance_migrant',
    'Meadow Pipit': 'short_distance_migrant',
    'Richard\'s Pipit': 'long_distance_migrant',
    'Bank Swallow': 'long_distance_migrant',
    'Common House-Martin': 'long_distance_migrant',

    # Other migrants
    'Corn Crake': 'long_distance_migrant',
    'Common Tern': 'long_distance_migrant',
    'Arctic Tern': 'long_distance_migrant',
    'Manx Shearwater': 'oceanic_migrant',
    'European Storm-Petrel': 'oceanic_migrant',
}

migrant_detections = detections[detections['common_name'].isin(migratory_species.keys())].copy()
migrant_detections['migration_type'] = migrant_detections['common_name'].map(migratory_species)

print("Migration Categories:")
print("-" * 80)

for mig_type in ['arctic_migrant', 'long_distance_migrant', 'partial_migrant', 'short_distance_migrant', 'oceanic_migrant']:
    type_data = migrant_detections[migrant_detections['migration_type'] == mig_type]
    if len(type_data) > 0:
        print(f"\n{mig_type.upper().replace('_', ' ')}:")
        print(f"  Species: {type_data['common_name'].nunique()}")
        print(f"  Detections: {len(type_data)}")

        top_species = type_data.groupby('common_name').size().sort_values(ascending=False).head(5)
        print(f"  Top species:")
        for species, count in top_species.items():
            print(f"    - {species}: {count}")

print()
print(f"Total migratory species: {migrant_detections['common_name'].nunique()}")
print(f"Total migratory detections: {len(migrant_detections)} ({len(migrant_detections)/len(detections)*100:.1f}%)")

# Export
migration_summary = migrant_detections.groupby(['migration_type', 'common_name']).size().reset_index(name='detections')
migration_summary = migration_summary.sort_values(['migration_type', 'detections'], ascending=[True, False])
migration_summary.to_csv('results/verified_migration_patterns.csv', index=False)
print()
print("✓ Saved: results/verified_migration_patterns.csv")
print()

# ============================================================================
# 2. DAWN/DUSK ACTIVITY (Crepuscular Patterns)
# ============================================================================

print("=" * 80)
print("2. DAWN/DUSK ACTIVITY PATTERNS (Crepuscular Species)")
print("=" * 80)
print()

# Define dawn/dusk periods (October in Norway ~60°N)
# Approximate sunrise: 07:30, sunset: 18:30
dawn_hours = [5, 6, 7, 8]  # Pre-dawn to morning
dusk_hours = [17, 18, 19, 20]  # Evening to post-dusk

detections['period'] = detections['hour'].apply(lambda h:
    'dawn' if h in dawn_hours else
    'dusk' if h in dusk_hours else
    'day' if 9 <= h <= 16 else
    'night'
)

# Find species with strong dawn/dusk preference
crepuscular_candidates = []

for species in detections['common_name'].unique():
    sp_data = detections[detections['common_name'] == species]

    if len(sp_data) < 10:  # Need sufficient data
        continue

    period_counts = sp_data['period'].value_counts()
    total = len(sp_data)

    dawn_pct = (period_counts.get('dawn', 0) / total) * 100
    dusk_pct = (period_counts.get('dusk', 0) / total) * 100
    crepuscular_pct = dawn_pct + dusk_pct

    if crepuscular_pct > 50:  # More than 50% activity at dawn/dusk
        crepuscular_candidates.append({
            'species': species,
            'total_detections': total,
            'dawn_detections': period_counts.get('dawn', 0),
            'dusk_detections': period_counts.get('dusk', 0),
            'dawn_percentage': dawn_pct,
            'dusk_percentage': dusk_pct,
            'crepuscular_percentage': crepuscular_pct,
            'peak_period': 'dawn' if dawn_pct > dusk_pct else 'dusk'
        })

crepuscular_df = pd.DataFrame(crepuscular_candidates).sort_values('crepuscular_percentage', ascending=False)

print("Species with Strong Dawn/Dusk Activity (>50% crepuscular):")
print("-" * 80)

for _, row in crepuscular_df.iterrows():
    print(f"\n{row['species']}:")
    print(f"  Total detections: {row['total_detections']}")
    print(f"  Dawn: {row['dawn_detections']} ({row['dawn_percentage']:.1f}%)")
    print(f"  Dusk: {row['dusk_detections']} ({row['dusk_percentage']:.1f}%)")
    print(f"  Crepuscular total: {row['crepuscular_percentage']:.1f}%")
    print(f"  Peak: {row['peak_period']}")

if not crepuscular_df.empty:
    crepuscular_df.to_csv('results/verified_crepuscular_species.csv', index=False)
    print()
    print("✓ Saved: results/verified_crepuscular_species.csv")

print()

# ============================================================================
# 3. NOCTURNAL SPECIES
# ============================================================================

print("=" * 80)
print("3. NOCTURNAL SPECIES ACTIVITY")
print("=" * 80)
print()

night_hours = list(range(0, 5)) + list(range(21, 24))

nocturnal_candidates = []

for species in detections['common_name'].unique():
    sp_data = detections[detections['common_name'] == species]

    if len(sp_data) < 5:
        continue

    night_detections = sp_data[sp_data['hour'].isin(night_hours)]
    night_pct = (len(night_detections) / len(sp_data)) * 100

    if night_pct > 30:  # Significant nocturnal activity
        nocturnal_candidates.append({
            'species': species,
            'total_detections': len(sp_data),
            'night_detections': len(night_detections),
            'night_percentage': night_pct,
            'peak_night_hour': night_detections['hour'].mode()[0] if len(night_detections) > 0 else None
        })

nocturnal_df = pd.DataFrame(nocturnal_candidates).sort_values('night_percentage', ascending=False)

print("Nocturnal/Partially Nocturnal Species (>30% night activity):")
print("-" * 80)

for _, row in nocturnal_df.iterrows():
    print(f"\n{row['species']}:")
    print(f"  Total detections: {row['total_detections']}")
    print(f"  Night detections: {row['night_detections']} ({row['night_percentage']:.1f}%)")
    if row['peak_night_hour'] is not None:
        print(f"  Peak night hour: {int(row['peak_night_hour']):02d}:00")

if not nocturnal_df.empty:
    nocturnal_df.to_csv('results/verified_nocturnal_species.csv', index=False)
    print()
    print("✓ Saved: results/verified_nocturnal_species.csv")

print()

# ============================================================================
# 4. FLIGHT CALLS (Nocturnal Migration)
# ============================================================================

print("=" * 80)
print("4. NOCTURNAL FLIGHT CALLS (Migration Detection)")
print("=" * 80)
print()

# Species known to give flight calls during migration
flight_call_species = [
    'Pink-footed Goose', 'Brant', 'Greater White-fronted Goose',
    'Common Crane', 'Redwing', 'Fieldfare', 'Snow Bunting',
    'Lapland Longspur', 'Brambling', 'Tree Pipit', 'Meadow Pipit'
]

flight_calls = detections[
    (detections['common_name'].isin(flight_call_species)) &
    (detections['hour'].isin(night_hours))
].copy()

if len(flight_calls) > 0:
    print("Nocturnal Flight Calls Detected:")
    print("-" * 80)

    fc_summary = flight_calls.groupby('common_name').agg({
        'common_name': 'size',
        'hour': lambda x: x.mode()[0] if len(x) > 0 else None
    }).rename(columns={'common_name': 'night_calls', 'hour': 'peak_hour'})

    fc_summary = fc_summary.sort_values('night_calls', ascending=False)

    for species, row in fc_summary.iterrows():
        print(f"\n{species}:")
        print(f"  Nocturnal calls: {row['night_calls']}")
        print(f"  Peak hour: {int(row['peak_hour']):02d}:00")

    flight_calls.to_csv('results/verified_nocturnal_flight_calls.csv', index=False)
    print()
    print("✓ Saved: results/verified_nocturnal_flight_calls.csv")
else:
    print("No nocturnal flight calls detected from known migratory species.")

print()

# ============================================================================
# 5. HABITAT GUILDS
# ============================================================================

print("=" * 80)
print("5. ECOLOGICAL GUILDS (Habitat Associations)")
print("=" * 80)
print()

habitat_guilds = {
    # Waterfowl
    'Graylag Goose': 'wetland',
    'Pink-footed Goose': 'wetland',
    'Greater White-fronted Goose': 'wetland',
    'Canada Goose': 'wetland',
    'Brant': 'coastal',
    'Mallard': 'wetland',
    'Common Goldeneye': 'wetland',
    'Gadwall': 'wetland',
    'Whooper Swan': 'wetland',
    'Tundra Swan': 'wetland',
    'Taiga Bean-Goose': 'wetland',
    'Tundra Bean-Goose': 'wetland',
    'Bar-headed Goose': 'wetland',

    # Waders/Shorebirds
    'Great Snipe': 'wetland',
    'Common Snipe': 'wetland',
    'Eurasian Woodcock': 'forest',
    'Common Sandpiper': 'wetland',
    'Northern Lapwing': 'grassland',
    'Eurasian Curlew': 'wetland',
    'Eurasian Oystercatcher': 'coastal',
    'Dunlin': 'coastal',
    'Black-bellied Plover': 'coastal',
    'European Golden-Plover': 'grassland',

    # Corvids
    'Hooded Crow': 'generalist',
    'Carrion Crow': 'generalist',
    'Rook': 'grassland',
    'Eurasian Magpie': 'generalist',
    'Common Raven': 'generalist',
    'Eurasian Jay': 'forest',
    'Eurasian Nutcracker': 'forest',

    # Forest species
    'Black Woodpecker': 'forest',
    'Lesser Spotted Woodpecker': 'forest',
    'Western Capercaillie': 'forest',
    'Eurasian Pygmy-Owl': 'forest',
    'Tawny Owl': 'forest',
    'Eurasian Eagle-Owl': 'forest',

    # Grassland/Scrub
    'Common Crane': 'wetland',
    'Corn Crake': 'grassland',
    'Gray Partridge': 'grassland',
    'Ring-necked Pheasant': 'grassland',

    # Passerines
    'Common Grasshopper-Warbler': 'wetland',
    'Snow Bunting': 'alpine',
    'Lapland Longspur': 'alpine',
    'Yellowhammer': 'grassland',
    'Reed Bunting': 'wetland',
    'Ortolan Bunting': 'grassland',

    # Seabirds
    'Common Tern': 'coastal',
    'Arctic Tern': 'coastal',
    'Black-headed Gull': 'coastal',
    'Herring Gull': 'coastal',
    'Black-legged Kittiwake': 'coastal',
    'Manx Shearwater': 'oceanic',
    'European Storm-Petrel': 'oceanic',
    'Red-throated Loon': 'coastal',
}

guild_detections = detections[detections['common_name'].isin(habitat_guilds.keys())].copy()
guild_detections['habitat_guild'] = guild_detections['common_name'].map(habitat_guilds)

print("Habitat Guild Distribution:")
print("-" * 80)

for guild in ['wetland', 'forest', 'grassland', 'coastal', 'generalist', 'alpine', 'oceanic']:
    guild_data = guild_detections[guild_detections['habitat_guild'] == guild]
    if len(guild_data) > 0:
        print(f"\n{guild.upper()}:")
        print(f"  Species: {guild_data['common_name'].nunique()}")
        print(f"  Detections: {len(guild_data)} ({len(guild_data)/len(detections)*100:.1f}%)")

guild_summary = guild_detections.groupby(['habitat_guild', 'common_name']).size().reset_index(name='detections')
guild_summary = guild_summary.sort_values(['habitat_guild', 'detections'], ascending=[True, False])
guild_summary.to_csv('results/verified_habitat_guilds.csv', index=False)
print()
print("✓ Saved: results/verified_habitat_guilds.csv")
print()

# ============================================================================
# 6. CALLING INTENSITY (Vocal Activity Levels)
# ============================================================================

print("=" * 80)
print("6. VOCAL ACTIVITY PATTERNS")
print("=" * 80)
print()

# Calculate calling rate per species (detections per hour of recording)
recording_hours = (detections['absolute_timestamp'].max() - detections['absolute_timestamp'].min()).total_seconds() / 3600

vocal_activity = []

for species in detections['common_name'].unique():
    sp_count = len(detections[detections['common_name'] == species])
    calls_per_hour = sp_count / recording_hours

    vocal_activity.append({
        'species': species,
        'total_detections': sp_count,
        'calls_per_hour': calls_per_hour,
        'vocal_intensity': 'high' if calls_per_hour > 10 else 'moderate' if calls_per_hour > 1 else 'low'
    })

vocal_df = pd.DataFrame(vocal_activity).sort_values('calls_per_hour', ascending=False)

print(f"Recording duration: {recording_hours:.1f} hours")
print()
print("Top 15 Most Vocal Species (calls per hour):")
print("-" * 80)

for _, row in vocal_df.head(15).iterrows():
    print(f"{row['species']:<35s} {row['calls_per_hour']:6.1f} calls/hr  ({row['total_detections']:4d} total) - {row['vocal_intensity']}")

vocal_df.to_csv('results/verified_vocal_activity.csv', index=False)
print()
print("✓ Saved: results/verified_vocal_activity.csv")
print()

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 80)
print("COMPREHENSIVE ANALYSIS COMPLETE")
print("=" * 80)
print()
print("Generated Files:")
print("  1. results/verified_migration_patterns.csv - Migration categories")
print("  2. results/verified_crepuscular_species.csv - Dawn/dusk active species")
print("  3. results/verified_nocturnal_species.csv - Night-active species")
print("  4. results/verified_nocturnal_flight_calls.csv - Migration flight calls")
print("  5. results/verified_habitat_guilds.csv - Ecological associations")
print("  6. results/verified_vocal_activity.csv - Calling intensity")
print()
print("Key Ecological Patterns:")
print(f"  - {len(migratory_species)} migratory species ({len(migrant_detections)/len(detections)*100:.1f}% of detections)")
print(f"  - {len(crepuscular_df)} species with strong dawn/dusk activity")
print(f"  - {len(nocturnal_df)} nocturnal/partially nocturnal species")
print(f"  - {len(flight_calls)} nocturnal flight calls detected")
print(f"  - {guild_detections['habitat_guild'].nunique()} habitat guilds represented")
print()
print("=" * 80)
