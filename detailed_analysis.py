#!/usr/bin/env python3
"""
Detailed Analysis of Flagged Detections
Provides deeper insights into verification priorities
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

print("=" * 80)
print("📊 DETAILED ANALYSIS OF FLAGGED DETECTIONS")
print("=" * 80)
print()

# Configuration
RESULTS_DIR = "/Users/georgeredpath/Dev/mcp-pipeline/shared/gaulossen/results"
VERIFICATION_DIR = f"{RESULTS_DIR}/verification_reports"
OUTPUT_DIR = f"{RESULTS_DIR}/detailed_analysis"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load data
print("📊 Loading data...")
df = pd.read_csv(f"{RESULTS_DIR}/all_detections.csv")
df['duration'] = df['end_s'] - df['start_s']
df['file'] = df['file_stem']

# Parse timestamps
df['absolute_timestamp'] = pd.to_datetime(df['absolute_timestamp'])
df['hour'] = df['absolute_timestamp'].dt.hour
df['date'] = df['absolute_timestamp'].dt.date

print(f"   Total detections: {len(df):,}")
print()

# Load verification checklist
checklist = pd.read_csv(f"{VERIFICATION_DIR}/master_verification_checklist.csv")

# === ANALYSIS 1: Confidence Distribution by Species ===
print("📊 Analysis 1: Confidence Distribution by Species")
print("-" * 80)

species_stats = df.groupby('common_name').agg({
    'confidence': ['count', 'mean', 'std', 'min', 'max'],
}).round(3)
species_stats.columns = ['count', 'conf_mean', 'conf_std', 'conf_min', 'conf_max']
species_stats = species_stats.sort_values('count', ascending=False)

# Top 10 most detected species
top10 = species_stats.head(10)
print("\nTop 10 Most Detected Species:")
print(top10.to_string())

# Bottom 10 least confident species (with at least 5 detections)
least_confident = species_stats[species_stats['count'] >= 5].sort_values('conf_mean').head(10)
print("\n10 Least Confident Species (min 5 detections):")
print(least_confident.to_string())

# === ANALYSIS 2: Temporal Patterns of Flagged Detections ===
print("\n")
print("📊 Analysis 2: Temporal Patterns of Flagged Detections")
print("-" * 80)

# Merge with checklist to get flags
df_flagged = df.merge(checklist[['common_name', 'start_s', 'file_stem', 'priority_score']],
                      left_on=['common_name', 'start_s', 'file_stem'],
                      right_on=['common_name', 'start_s', 'file_stem'],
                      how='left')

df_flagged['priority_score'] = df_flagged['priority_score'].fillna(0)
high_priority = df_flagged[df_flagged['priority_score'] >= 5]

print(f"\nHigh Priority Detections by Hour of Day:")
hourly_hp = high_priority.groupby('hour').size()
for hour, count in hourly_hp.items():
    print(f"   {hour:02d}:00 - {count:2d} detections")

print(f"\nHigh Priority Detections by Date:")
daily_hp = high_priority.groupby('date').size()
for date, count in daily_hp.items():
    print(f"   {date} - {count:2d} detections")

# === ANALYSIS 3: Co-occurrence Analysis ===
print("\n")
print("📊 Analysis 3: Species Co-occurrence in Same Files")
print("-" * 80)

# Count species per file
species_per_file = df.groupby(['file', 'common_name']).size().reset_index(name='count')
file_species_counts = species_per_file.groupby('file')['common_name'].count()

print("\nSpecies Richness per File:")
for file, count in file_species_counts.items():
    print(f"   {file}: {count} species")

# High priority species co-occurrence
hp_species = high_priority['common_name'].unique()
print(f"\nHigh Priority Species ({len(hp_species)} total):")
for species in sorted(hp_species):
    count = len(high_priority[high_priority['common_name'] == species])
    files = high_priority[high_priority['common_name'] == species]['file'].unique()
    print(f"   {species}: {count} detection(s) in {len(files)} file(s)")

# === ANALYSIS 4: Detection Density Analysis ===
print("\n")
print("📊 Analysis 4: Detection Density (detections per hour)")
print("-" * 80)

# Calculate recording duration per file
file_durations = df.groupby('file')['end_s'].max() / 3600  # Convert to hours

# Calculate detection density
detection_density = df.groupby('file').size() / file_durations

print("\nDetection Density by File:")
for file, density in detection_density.items():
    print(f"   {file}: {density:.1f} detections/hour")

# High priority density
hp_density = high_priority.groupby('file').size() / file_durations

print("\nHigh Priority Detection Density by File:")
for file in file_durations.index:
    hp_count = len(high_priority[high_priority['file'] == file])
    total_count = len(df[df['file'] == file])
    percentage = (hp_count / total_count * 100) if total_count > 0 else 0
    print(f"   {file}: {hp_count}/{total_count} ({percentage:.1f}%)")

# === ANALYSIS 5: Confidence Trends Over Time ===
print("\n")
print("📊 Analysis 5: Confidence Trends Over Recording Period")
print("-" * 80)

# Average confidence by date
daily_conf = df.groupby('date')['confidence'].agg(['mean', 'std', 'count'])
print("\nMean Confidence by Date:")
print(daily_conf.to_string())

# === VISUALIZATIONS ===
print("\n")
print("📊 Generating detailed visualizations...")

# Create figure with subplots
fig = plt.figure(figsize=(20, 12))

# 1. Confidence distribution by top species
ax1 = plt.subplot(3, 3, 1)
top5_species = species_stats.head(5).index
df_top5 = df[df['common_name'].isin(top5_species)]
df_top5.boxplot(column='confidence', by='common_name', ax=ax1)
ax1.set_title('Confidence Distribution - Top 5 Species')
ax1.set_xlabel('Species')
ax1.set_ylabel('Confidence')
plt.sca(ax1)
plt.xticks(rotation=45, ha='right')

# 2. High priority detections by hour
ax2 = plt.subplot(3, 3, 2)
hourly_hp.plot(kind='bar', ax=ax2, color='red', alpha=0.7)
ax2.set_title('High Priority Detections by Hour')
ax2.set_xlabel('Hour of Day')
ax2.set_ylabel('Count')

# 3. Detection density by file
ax3 = plt.subplot(3, 3, 3)
detection_density.plot(kind='bar', ax=ax3, color='steelblue')
ax3.set_title('Detection Density (detections/hour)')
ax3.set_xlabel('File')
ax3.set_ylabel('Detections per Hour')
plt.sca(ax3)
plt.xticks(rotation=45, ha='right')

# 4. Priority score distribution
ax4 = plt.subplot(3, 3, 4)
checklist['priority_score'].value_counts().sort_index().plot(kind='bar', ax=ax4, color='orange')
ax4.set_title('Priority Score Distribution')
ax4.set_xlabel('Priority Score')
ax4.set_ylabel('Count')

# 5. Confidence vs Duration scatter (top species)
ax5 = plt.subplot(3, 3, 5)
for species in top5_species[:3]:
    species_data = df[df['common_name'] == species]
    ax5.scatter(species_data['duration'], species_data['confidence'],
                alpha=0.3, label=species, s=10)
ax5.set_title('Confidence vs Duration (Top 3 Species)')
ax5.set_xlabel('Duration (s)')
ax5.set_ylabel('Confidence')
ax5.legend()

# 6. Species richness per file
ax6 = plt.subplot(3, 3, 6)
file_species_counts.plot(kind='bar', ax=ax6, color='green')
ax6.set_title('Species Richness per File')
ax6.set_xlabel('File')
ax6.set_ylabel('Number of Species')
plt.sca(ax6)
plt.xticks(rotation=45, ha='right')

# 7. Confidence timeline
ax7 = plt.subplot(3, 3, 7)
df_sorted = df.sort_values('absolute_timestamp')
ax7.scatter(df_sorted['absolute_timestamp'], df_sorted['confidence'],
            alpha=0.1, s=5, color='blue')
ax7.axhline(y=0.5, color='r', linestyle='--', label='Medium Threshold')
ax7.set_title('Confidence Over Time')
ax7.set_xlabel('Timestamp')
ax7.set_ylabel('Confidence')
ax7.legend()
plt.xticks(rotation=45)

# 8. High priority species bar chart
ax8 = plt.subplot(3, 3, 8)
hp_species_counts = high_priority['common_name'].value_counts()
hp_species_counts.plot(kind='barh', ax=ax8, color='red')
ax8.set_title('High Priority Species Counts')
ax8.set_xlabel('Count')
ax8.set_ylabel('Species')

# 9. Confidence distribution histogram with flags
ax9 = plt.subplot(3, 3, 9)
ax9.hist(df['confidence'], bins=50, alpha=0.5, label='All', color='blue')
ax9.hist(high_priority['confidence'], bins=50, alpha=0.5, label='High Priority', color='red')
ax9.axvline(x=0.5, color='black', linestyle='--', label='Medium Threshold')
ax9.set_title('Confidence Distribution')
ax9.set_xlabel('Confidence')
ax9.set_ylabel('Count')
ax9.legend()

plt.tight_layout()
output_path = f"{OUTPUT_DIR}/detailed_analysis.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"   ✅ {output_path}")

# === EXPORT DETAILED REPORTS ===
print("\n")
print("📝 Exporting detailed reports...")

# Report 1: Species-level analysis
species_full = df.groupby('common_name').agg({
    'confidence': ['count', 'mean', 'std', 'min', 'max'],
    'duration': 'mean',
    'file': lambda x: x.nunique()
}).round(3)
species_full.columns = ['count', 'conf_mean', 'conf_std', 'conf_min', 'conf_max', 'dur_mean', 'files']

# Add high priority counts
hp_counts = high_priority.groupby('common_name').size().rename('hp_count')
species_full = species_full.join(hp_counts, how='left')
species_full['hp_count'] = species_full['hp_count'].fillna(0).astype(int)
species_full['hp_percentage'] = (species_full['hp_count'] / species_full['count'] * 100).round(1)

species_full = species_full.sort_values('count', ascending=False)
output_path = f"{OUTPUT_DIR}/species_full_analysis.csv"
species_full.to_csv(output_path)
print(f"   ✅ {output_path}")

# Report 2: Temporal analysis
temporal = df.groupby(['date', 'hour']).agg({
    'common_name': 'count',
    'confidence': 'mean'
}).rename(columns={'common_name': 'detections', 'confidence': 'mean_confidence'}).round(3)
output_path = f"{OUTPUT_DIR}/temporal_analysis.csv"
temporal.to_csv(output_path)
print(f"   ✅ {output_path}")

# Report 3: File-level summary with verification stats
file_summary = df.groupby('file').agg({
    'common_name': ['count', 'nunique'],
    'confidence': 'mean',
    'duration': 'sum'
}).round(3)
file_summary.columns = ['total_detections', 'species_count', 'mean_confidence', 'total_duration_s']
file_summary['total_duration_h'] = (file_summary['total_duration_s'] / 3600).round(2)

# Add high priority counts
hp_file = high_priority.groupby('file').size().rename('hp_detections')
file_summary = file_summary.join(hp_file, how='left')
file_summary['hp_detections'] = file_summary['hp_detections'].fillna(0).astype(int)
file_summary['hp_percentage'] = (file_summary['hp_detections'] / file_summary['total_detections'] * 100).round(1)

output_path = f"{OUTPUT_DIR}/file_analysis.csv"
file_summary.to_csv(output_path)
print(f"   ✅ {output_path}")

print("\n")
print("=" * 80)
print("✅ DETAILED ANALYSIS COMPLETE")
print("=" * 80)
print()

print(f"📁 Reports saved to:")
print(f"   {OUTPUT_DIR}/")
print()

print(f"📊 Key Findings:")
print(f"   - {len(species_stats)} species detected")
print(f"   - {len(hp_species)} species flagged as high priority")
print(f"   - Most detections: {species_stats.index[0]} ({species_stats['count'].iloc[0]:,})")
print(f"   - Least confident (min 5): {least_confident.index[0]} ({least_confident['conf_mean'].iloc[0]:.3f})")
print(f"   - Peak activity hour: {df.groupby('hour').size().idxmax():02d}:00")
print()
