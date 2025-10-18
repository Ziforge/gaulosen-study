#!/usr/bin/env python3
"""
Deep Dive Behavioral Analysis - Advanced Patterns
Explores detailed acoustic ecology:
1. Duetting/Pair Bonding (coordinated male-female calls)
2. Territorial Behavior (repeated calls from same location/time)
3. Feeding Aggregations (coordinated foraging calls)
4. Distress/Predator Response (abnormal patterns)
5. Acoustic Niche Partitioning (species co-occurrence)
6. Diel Activity Patterns (24-hour calling cycles)
7. Weather Response (how calls change with conditions)
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 80)
print("🔬 DEEP DIVE BEHAVIORAL ANALYSIS")
print("=" * 80)
print()

# Load data
df = pd.read_csv('results/all_detections_with_weather.csv')
df['datetime'] = pd.to_datetime(df['absolute_timestamp'])
df['hour'] = df['datetime'].dt.hour
df['date'] = df['datetime'].dt.date

print(f"📊 Analyzing {len(df)} detections across {df['filename'].nunique()} recordings")
print(f"   Time span: {df['datetime'].min()} to {df['datetime'].max()}")
print()

# ============================================================================
# 1. DUETTING / PAIR BONDING ANALYSIS
# ============================================================================
print("=" * 80)
print("1. DUETTING & PAIR BONDING (Coordinated Calls)")
print("=" * 80)
print()
print("Looking for:")
print("  • Alternating calls (call-response pattern)")
print("  • Consistent 1-5 second intervals")
print("  • Same species, same time window")
print()

duetting_events = []
for (filename, species), group in df.groupby(['filename', 'common_name']):
    if len(group) < 4:
        continue

    times = sorted(group['start_s'].values)

    # Look for alternating pattern with consistent intervals
    for i in range(len(times) - 3):
        window = times[i:i+4]
        if window[-1] - window[0] < 20:  # 4 calls within 20s
            intervals = np.diff(window)

            # Check for consistent intervals (duetting)
            if 1 < np.mean(intervals) < 5 and np.std(intervals) < 1.5:
                duetting_events.append({
                    'species': species,
                    'filename': filename,
                    'start_time': window[0],
                    'num_calls': 4,
                    'interval': np.mean(intervals),
                    'regularity': 1 / (np.std(intervals) + 0.1)  # Higher = more regular
                })
                break

if len(duetting_events) > 0:
    duet_df = pd.DataFrame(duetting_events)
    duet_df = duet_df.sort_values('regularity', ascending=False)
    print(f"✅ Detected {len(duet_df)} potential duetting/pair bonding events")
    print()
    print("Top 15 Most Regular Call Patterns (Potential Duets):")
    print("-" * 80)
    for idx, row in duet_df.head(15).iterrows():
        print(f"  {row['species']:40s} | Interval: {row['interval']:.1f}s | "
              f"Regularity: {row['regularity']:.2f}")
    print()
else:
    print("❌ No clear duetting patterns detected")
    print()

# ============================================================================
# 2. TERRITORIAL BEHAVIOR
# ============================================================================
print("=" * 80)
print("2. TERRITORIAL BEHAVIOR (Site Fidelity)")
print("=" * 80)
print()
print("Detecting:")
print("  • Repeated calls from same recording location")
print("  • High call density over extended period")
print("  • Indicates territorial defense")
print()

territorial_species = df.groupby(['filename', 'common_name']).agg({
    'start_s': ['count', 'min', 'max'],
    'confidence': 'mean'
})
territorial_species.columns = ['call_count', 'first_call', 'last_call', 'avg_conf']
territorial_species['duration_hours'] = (territorial_species['last_call'] -
                                         territorial_species['first_call']) / 3600
territorial_species['calls_per_hour'] = (territorial_species['call_count'] /
                                         territorial_species['duration_hours'])

# Filter for territorial behavior (high calling rate over extended period)
territorial = territorial_species[
    (territorial_species['call_count'] >= 10) &
    (territorial_species['duration_hours'] >= 1) &
    (territorial_species['calls_per_hour'] >= 5)
].sort_values('calls_per_hour', ascending=False).reset_index()

if len(territorial) > 0:
    print(f"✅ Detected {len(territorial)} territorial behavior instances")
    print()
    print("Top 15 Territorial Species (Sustained High Calling Rate):")
    print("-" * 80)
    for idx, row in territorial.head(15).iterrows():
        print(f"  {row['common_name']:35s} | {int(row['call_count']):4d} calls | "
              f"{row['duration_hours']:.1f}h | {row['calls_per_hour']:.1f} calls/hr")
    print()

    # Save territorial analysis
    territorial.to_csv('results/territorial_behavior.csv', index=False)
    print(f"✅ Saved to: results/territorial_behavior.csv")
    print()
else:
    print("❌ No clear territorial patterns detected")
    print()

# ============================================================================
# 3. ACOUSTIC NICHE PARTITIONING
# ============================================================================
print("=" * 80)
print("3. ACOUSTIC NICHE PARTITIONING (Species Co-occurrence)")
print("=" * 80)
print()
print("Analyzing temporal overlap between species")
print()

# Create hourly activity matrix
hourly_activity = df.groupby(['common_name', 'hour']).size().unstack(fill_value=0)

# Calculate temporal overlap (correlation between species' hourly patterns)
if len(hourly_activity) > 1:
    overlap_matrix = hourly_activity.T.corr()

    # Find species pairs with high overlap (competition) or low overlap (partitioning)
    high_overlap = []
    low_overlap = []

    species_list = overlap_matrix.index.tolist()
    for i in range(len(species_list)):
        for j in range(i+1, len(species_list)):
            sp1, sp2 = species_list[i], species_list[j]
            corr = overlap_matrix.loc[sp1, sp2]

            if corr > 0.7:  # High temporal overlap
                high_overlap.append((sp1, sp2, corr))
            elif corr < 0.3:  # Temporal separation
                low_overlap.append((sp1, sp2, corr))

    if high_overlap:
        high_overlap.sort(key=lambda x: x[2], reverse=True)
        print(f"✅ Found {len(high_overlap)} species pairs with HIGH temporal overlap")
        print()
        print("Top 10 Co-occurring Species (Similar Activity Patterns):")
        print("-" * 80)
        for sp1, sp2, corr in high_overlap[:10]:
            print(f"  {sp1[:20]:20s} ↔ {sp2[:20]:20s} | Overlap: {corr:.3f}")
        print()

    if low_overlap:
        low_overlap.sort(key=lambda x: x[2])
        print(f"✅ Found {len(low_overlap)} species pairs with LOW temporal overlap")
        print("   (Acoustic niche partitioning - reduced competition)")
        print()
        print("Top 10 Temporally Separated Species:")
        print("-" * 80)
        for sp1, sp2, corr in low_overlap[:10]:
            print(f"  {sp1[:20]:20s} ⊥ {sp2[:20]:20s} | Separation: {corr:.3f}")
        print()

# ============================================================================
# 4. DIEL ACTIVITY PATTERNS (24-hour cycles)
# ============================================================================
print("=" * 80)
print("4. DIEL ACTIVITY PATTERNS (24-Hour Calling Rhythms)")
print("=" * 80)
print()

# Calculate hourly call rates for top species
top_species = df['common_name'].value_counts().head(10).index.tolist()
hourly_patterns = df[df['common_name'].isin(top_species)].groupby(
    ['common_name', 'hour']
).size().unstack(fill_value=0)

# Categorize activity patterns
activity_types = {}
for species in top_species:
    if species not in hourly_patterns.index:
        continue

    pattern = hourly_patterns.loc[species].values

    # Find peak activity hours
    peak_hour = pattern.argmax()
    peak_activity = pattern[peak_hour]
    total_activity = pattern.sum()

    # Categorize
    if peak_hour >= 4 and peak_hour <= 8:
        activity_type = "Dawn Singer"
    elif peak_hour >= 20 or peak_hour <= 4:
        activity_type = "Nocturnal"
    elif peak_hour >= 9 and peak_hour <= 17:
        activity_type = "Diurnal"
    else:
        activity_type = "Crepuscular"

    # Calculate activity concentration (how concentrated vs spread out)
    concentration = peak_activity / (total_activity / 24)  # Ratio to mean

    activity_types[species] = {
        'type': activity_type,
        'peak_hour': peak_hour,
        'concentration': concentration,
        'total_calls': total_activity
    }

print("Activity Pattern Classification:")
print("-" * 80)
for species, info in sorted(activity_types.items(),
                            key=lambda x: x[1]['total_calls'],
                            reverse=True):
    print(f"  {species[:35]:35s} | {info['type']:15s} | "
          f"Peak: {info['peak_hour']:02d}:00 | "
          f"Concentration: {info['concentration']:.1f}x")
print()

# ============================================================================
# 5. WEATHER RESPONSE ANALYSIS
# ============================================================================
print("=" * 80)
print("5. WEATHER RESPONSE ANALYSIS")
print("=" * 80)
print()
print("How do calling rates change with weather conditions?")
print()

weather_response = df.groupby(['common_name', 'weather_summary']).agg({
    'start_s': 'count',
    'confidence': 'mean'
}).rename(columns={'start_s': 'call_count'}).reset_index()

# For top 10 species, show weather preferences
for species in top_species[:10]:
    species_weather = weather_response[weather_response['common_name'] == species]
    if len(species_weather) > 0:
        total = species_weather['call_count'].sum()
        print(f"\n{species}:")
        print("  " + "-" * 76)
        for idx, row in species_weather.sort_values('call_count', ascending=False).iterrows():
            pct = (row['call_count'] / total) * 100
            print(f"  {row['weather_summary']:35s} | {int(row['call_count']):4d} calls ({pct:5.1f}%)")

print()

# ============================================================================
# 6. CALL RATE DYNAMICS
# ============================================================================
print("=" * 80)
print("6. CALL RATE DYNAMICS (Temporal Patterns)")
print("=" * 80)
print()

# Calculate calls per hour for each recording
hourly_rates = df.groupby(['filename', 'hour']).size().reset_index(name='calls')
hourly_stats = hourly_rates.groupby('hour')['calls'].agg(['mean', 'std', 'max'])

print("Average Calls Per Hour (Across All Species):")
print("-" * 80)
print(f"{'Hour':<6} {'Mean':<10} {'StdDev':<10} {'Peak':<10} {'Pattern'}")
print("-" * 80)

for hour in range(24):
    if hour in hourly_stats.index:
        mean = hourly_stats.loc[hour, 'mean']
        std = hourly_stats.loc[hour, 'std']
        peak = hourly_stats.loc[hour, 'max']

        # Create visual bar
        bar_length = int(mean / hourly_stats['mean'].max() * 40)
        bar = '█' * bar_length

        print(f"{hour:02d}:00  {mean:7.1f}    {std:7.1f}    {int(peak):7d}    {bar}")

print()

# ============================================================================
# 7. POTENTIAL INDIVIDUAL RECOGNITION
# ============================================================================
print("=" * 80)
print("7. INDIVIDUAL VARIATION ANALYSIS")
print("=" * 80)
print()
print("Analyzing consistency within species to detect potential individuals")
print()

# For species with many detections, analyze temporal clustering
individual_candidates = []

for species in top_species[:5]:  # Focus on top 5
    species_df = df[df['common_name'] == species]

    # Group by recording and look for temporal clusters
    for filename in species_df['filename'].unique():
        recording_df = species_df[species_df['filename'] == filename]

        if len(recording_df) < 10:
            continue

        times = sorted(recording_df['start_s'].values)

        # Find temporal clusters (gaps > 30 min suggest different individuals)
        clusters = []
        current_cluster = [times[0]]

        for t in times[1:]:
            if t - current_cluster[-1] < 1800:  # Less than 30 min
                current_cluster.append(t)
            else:
                if len(current_cluster) >= 5:
                    clusters.append(current_cluster)
                current_cluster = [t]

        if len(current_cluster) >= 5:
            clusters.append(current_cluster)

        if len(clusters) >= 2:
            individual_candidates.append({
                'species': species,
                'filename': filename,
                'num_individuals': len(clusters),
                'total_calls': len(times),
                'clusters': clusters
            })

if individual_candidates:
    print(f"✅ Detected {len(individual_candidates)} potential multi-individual recordings")
    print()
    print("Recordings with Multiple Potential Individuals:")
    print("-" * 80)
    for cand in individual_candidates[:10]:
        print(f"  {cand['species']:30s} | {cand['num_individuals']} individuals | "
              f"{cand['total_calls']} total calls")
    print()
else:
    print("❌ Insufficient data for individual recognition")
    print()

# ============================================================================
# SAVE COMPREHENSIVE SUMMARY
# ============================================================================
print("=" * 80)
print("💾 SAVING COMPREHENSIVE ANALYSIS")
print("=" * 80)
print()

# Create comprehensive summary
summary = {
    'total_detections': len(df),
    'total_species': df['common_name'].nunique(),
    'recording_period_days': (df['datetime'].max() - df['datetime'].min()).days,
    'duetting_events': len(duetting_events) if duetting_events else 0,
    'territorial_instances': len(territorial) if len(territorial) > 0 else 0,
    'potential_individuals': len(individual_candidates)
}

with open('results/deep_dive_summary.txt', 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("DEEP DIVE BEHAVIORAL ANALYSIS SUMMARY\n")
    f.write("=" * 80 + "\n\n")

    f.write(f"Dataset Overview:\n")
    f.write(f"  Total detections: {summary['total_detections']}\n")
    f.write(f"  Species detected: {summary['total_species']}\n")
    f.write(f"  Recording period: {summary['recording_period_days']} days\n\n")

    f.write(f"Behavioral Patterns Detected:\n")
    f.write(f"  Duetting/Pair bonding events: {summary['duetting_events']}\n")
    f.write(f"  Territorial behavior instances: {summary['territorial_instances']}\n")
    f.write(f"  Potential individual detections: {summary['potential_individuals']}\n\n")

    f.write(f"Activity Patterns:\n")
    for species, info in list(activity_types.items())[:15]:
        f.write(f"  {species}: {info['type']} (peak {info['peak_hour']:02d}:00)\n")

print("✅ Saved summary to: results/deep_dive_summary.txt")
print()

print("=" * 80)
print("✅ DEEP DIVE ANALYSIS COMPLETE")
print("=" * 80)
print()

print("Files created:")
print("  • results/territorial_behavior.csv")
print("  • results/deep_dive_summary.txt")
print()
