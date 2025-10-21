#!/usr/bin/env python3
"""
Select Best Examples: Cleanest of ALL Species + Flock Behavior
Strategy:
1. Get cleanest example (highest confidence) for EVERY species detected
2. Identify flock behavior (multiple simultaneous calls, high call density)
3. Apply advanced denoising to all selected examples
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("🎯 SELECTING BEST EXAMPLES: ALL SPECIES + FLOCK BEHAVIOR")
print("=" * 80)
print()

# Load detections
df = pd.read_csv('results/all_detections_with_weather.csv')

print(f"📊 Dataset Overview:")
print(f"   Total detections: {len(df)}")
print(f"   Total species: {df['common_name'].nunique()}")
print()

# Strategy 1: Best example of EVERY species
print("=" * 80)
print("STRATEGY 1: Cleanest Example of Every Species")
print("=" * 80)
print()

# Get best detection for each species (highest confidence)
best_per_species_all = df.loc[df.groupby('common_name')['confidence'].idxmax()]

print(f"Selected {len(best_per_species_all)} species")
print()
print("Top 20 by confidence:")
for idx, row in best_per_species_all.nlargest(20, 'confidence').iterrows():
    print(f"  {row['common_name']:40s} | Conf: {row['confidence']:.3f} | {row['weather_summary']}")
print()

# Strategy 2: Identify flock behavior
print("=" * 80)
print("STRATEGY 2: Flock Behavior Detection")
print("=" * 80)
print()

# Flock indicators:
# 1. Multiple detections of same species in short time window
# 2. High call density (many calls per minute)
# 3. Overlapping or near-simultaneous calls

# Group by file and species, calculate call density
df['recording_id'] = df['filename']
flock_candidates = []

for (filename, species), group in df.groupby(['filename', 'common_name']):
    if len(group) < 5:  # Need at least 5 calls to consider flock
        continue

    # Calculate temporal metrics
    times = group['start_s'].values
    durations = (group['end_s'] - group['start_s']).values

    if len(times) == 0:
        continue

    time_span = times.max() - times.min()
    if time_span == 0:
        continue

    # Calls per minute
    calls_per_minute = len(group) / (time_span / 60)

    # Find clusters (calls within 30 seconds of each other)
    time_diffs = np.diff(np.sort(times))
    close_calls = np.sum(time_diffs < 30)  # Calls within 30s

    # Flock score
    avg_confidence = group['confidence'].mean()
    flock_score = calls_per_minute * (close_calls / len(group)) * avg_confidence

    if calls_per_minute > 2.0 and close_calls > 3:  # Significant activity
        flock_candidates.append({
            'filename': filename,
            'species': species,
            'num_calls': len(group),
            'time_span_min': time_span / 60,
            'calls_per_minute': calls_per_minute,
            'close_calls': close_calls,
            'avg_confidence': avg_confidence,
            'flock_score': flock_score,
            'start_time': times.min(),
            'end_time': times.max()
        })

flock_df = pd.DataFrame(flock_candidates)

if len(flock_df) > 0:
    flock_df = flock_df.sort_values('flock_score', ascending=False)

    print(f"Identified {len(flock_df)} potential flock behavior instances")
    print()
    print("Top 10 Flock Behaviors:")
    print("-" * 80)
    for idx, row in flock_df.head(10).iterrows():
        print(f"  {row['species']:30s} | {row['num_calls']:3d} calls | "
              f"{row['calls_per_minute']:5.1f} calls/min | "
              f"Score: {row['flock_score']:6.1f}")
    print()

    # Get specific detections for top flock behaviors
    flock_detections = []
    for idx, flock in flock_df.head(10).iterrows():
        # Get all detections in this flock timespan
        flock_segment = df[
            (df['filename'] == flock['filename']) &
            (df['common_name'] == flock['species']) &
            (df['start_s'] >= flock['start_time'] - 5) &  # 5s before
            (df['start_s'] <= flock['end_time'] + 5)       # 5s after
        ]
        flock_detections.append(flock_segment)

    flock_detections_df = pd.concat(flock_detections).drop_duplicates()
    print(f"Selected {len(flock_detections_df)} detections for flock behavior analysis")
    print()
else:
    flock_detections_df = pd.DataFrame()
    print("No significant flock behavior detected")
    print()

# Strategy 3: Temporal variation (nighttime vs morning calls)
print("=" * 80)
print("STRATEGY 3: Temporal Variation (Nighttime vs Morning)")
print("=" * 80)
print()

# Parse absolute_timestamp to get hour of day
df['datetime'] = pd.to_datetime(df['absolute_timestamp'])
df['hour'] = df['datetime'].dt.hour

# Nighttime calls (22:00 - 05:00)
night_calls = df[(df['hour'] >= 22) | (df['hour'] <= 5)]
# Morning calls (05:00 - 10:00)
morning_calls = df[(df['hour'] > 5) & (df['hour'] <= 10)]

# Get best example of each species during night and morning
night_best = pd.DataFrame()
morning_best = pd.DataFrame()

if len(night_calls) > 0:
    night_best = night_calls.loc[night_calls.groupby('common_name')['confidence'].idxmax()]
    print(f"Nighttime detections (22:00-05:00): {len(night_calls)} total")
    print(f"Unique nighttime species: {night_calls['common_name'].nunique()}")
    print(f"Selected {len(night_best)} nighttime examples")
    print()
    print("Top 10 Nighttime Calls:")
    print("-" * 80)
    for idx, row in night_best.nlargest(10, 'confidence').iterrows():
        hour_str = f"{row['hour']:02d}:00"
        print(f"  {row['common_name']:30s} | {hour_str} | Conf: {row['confidence']:.3f}")
    print()
else:
    print("No nighttime detections found")
    print()

if len(morning_calls) > 0:
    morning_best = morning_calls.loc[morning_calls.groupby('common_name')['confidence'].idxmax()]
    print(f"Morning detections (05:00-10:00): {len(morning_calls)} total")
    print(f"Unique morning species: {morning_calls['common_name'].nunique()}")
    print(f"Selected {len(morning_best)} morning examples")
    print()
    print("Top 10 Morning Calls:")
    print("-" * 80)
    for idx, row in morning_best.nlargest(10, 'confidence').iterrows():
        hour_str = f"{row['hour']:02d}:00"
        print(f"  {row['common_name']:30s} | {hour_str} | Conf: {row['confidence']:.3f}")
    print()
else:
    print("No morning detections found")
    print()

# Combine all selections
print("=" * 80)
print("FINAL SELECTION")
print("=" * 80)
print()

selected = pd.concat([
    best_per_species_all,
    flock_detections_df,
    night_best,
    morning_best
]).drop_duplicates()

print(f"📊 Summary:")
print(f"   Species representations: {selected['common_name'].nunique()}")
print(f"   Total detections selected: {len(selected)}")
print()

# Break down by category
print(f"Breakdown by Selection Strategy:")
print(f"   Best species examples: {len(best_per_species_all)}")
print(f"   Flock behavior: {len(flock_detections_df)}")
print(f"   Nighttime calls: {len(night_best)}")
print(f"   Morning calls: {len(morning_best)}")
print(f"   (Note: some detections may appear in multiple categories)")
print()

# Confidence distribution
high_conf = selected[selected['confidence'] >= 0.70]
med_conf = selected[(selected['confidence'] >= 0.50) & (selected['confidence'] < 0.70)]
low_conf = selected[selected['confidence'] < 0.50]

print(f"Confidence Distribution:")
print(f"   High (≥0.70): {len(high_conf)} ({len(high_conf)/len(selected)*100:.1f}%)")
print(f"   Medium (0.50-0.70): {len(med_conf)} ({len(med_conf)/len(selected)*100:.1f}%)")
print(f"   Low (<0.50): {len(low_conf)} ({len(low_conf)/len(selected)*100:.1f}%)")
print()

# Save selection
output_file = 'results/best_examples_selection.csv'
selected.to_csv(output_file, index=False)
print(f"✅ Saved selection to: {output_file}")
print()

# Also save flock behavior summary
if len(flock_df) > 0:
    flock_output = 'results/flock_behavior_summary.csv'
    flock_df.to_csv(flock_output, index=False)
    print(f"✅ Saved flock behavior analysis to: {flock_output}")
    print()

print("=" * 80)
print("📋 SPECIES COVERAGE")
print("=" * 80)
print()

species_coverage = selected.groupby('common_name').agg({
    'confidence': ['count', 'mean', 'max']
}).round(3)
species_coverage.columns = ['count', 'avg_conf', 'max_conf']
species_coverage = species_coverage.sort_values('max_conf', ascending=False)

print(f"All {len(species_coverage)} species with best examples:")
print("-" * 80)
for species, row in species_coverage.iterrows():
    print(f"  {species:40s} | {int(row['count']):3d} clips | "
          f"Max conf: {row['max_conf']:.3f} | Avg: {row['avg_conf']:.3f}")
print()

print("=" * 80)
print("✅ SELECTION COMPLETE")
print("=" * 80)
print()
print(f"🎯 Next step: Apply advanced denoising to all {len(selected)} selected clips")
print()
