#!/usr/bin/env python3
"""
Export Specific Subsets for Focused Review
Creates targeted CSV and Raven table exports for different review scenarios
"""

import pandas as pd
import numpy as np
import os
import sys

# Import Raven MCP functions
sys.path.insert(0, '/Users/georgeredpath/Dev/mcp-pipeline/raven-mcp')
from server import create_raven_selection_table

print("=" * 80)
print("📦 EXPORTING FOCUSED REVIEW SUBSETS")
print("=" * 80)
print()

# Configuration
RESULTS_DIR = "/Users/georgeredpath/Dev/mcp-pipeline/shared/gaulossen/results"
EXPORT_DIR = f"{RESULTS_DIR}/focused_exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

# Load data
print("📊 Loading data...")
df = pd.read_csv(f"{RESULTS_DIR}/all_detections.csv")
df['duration'] = df['end_s'] - df['start_s']
df['file'] = df['file_stem']

checklist = pd.read_csv(f"{RESULTS_DIR}/verification_reports/master_verification_checklist.csv")

print(f"   Total detections: {len(df):,}")
print()

# === SUBSET 1: Low Confidence Species (for targeted verification) ===
print("📦 Subset 1: Low Confidence Species (conf < 0.40)")
print("-" * 80)

low_conf = df[df['confidence'] < 0.40].copy()
low_conf = low_conf.sort_values('confidence')

print(f"   Detections: {len(low_conf)}")
print(f"   Species: {low_conf['common_name'].nunique()}")

# Export CSV
output_path = f"{EXPORT_DIR}/low_confidence_subset.csv"
low_conf.to_csv(output_path, index=False)
print(f"   ✅ {output_path}")

# Export Raven tables per file
for file in low_conf['file_stem'].unique():
    file_detections = low_conf[low_conf['file_stem'] == file].copy()

    audio_file = f"{file}.WAV"
    audio_path = f"/workspace/shared/gaulossen/audio_files/{audio_file}"

    raven_df = create_raven_selection_table(
        file_detections,
        audio_file,
        audio_path,
        default_low_freq=500.0,
        default_high_freq=10000.0
    )

    output_path = f"{EXPORT_DIR}/{file}_low_confidence_raven.txt"
    raven_df.to_csv(output_path, sep='\t', index=False)
    print(f"   ✅ {os.path.basename(output_path)} ({len(raven_df)} selections)")

print()

# === SUBSET 2: Nighttime Detections (00:00-06:00) ===
print("📦 Subset 2: Nighttime Detections (00:00-06:00)")
print("-" * 80)

df['absolute_timestamp'] = pd.to_datetime(df['absolute_timestamp'])
df['hour'] = df['absolute_timestamp'].dt.hour

nighttime = df[(df['hour'] >= 0) & (df['hour'] < 6)].copy()
nighttime = nighttime.sort_values('absolute_timestamp')

print(f"   Detections: {len(nighttime)}")
print(f"   Species: {nighttime['common_name'].nunique()}")
print(f"   Top species: {nighttime['common_name'].value_counts().head(3).to_dict()}")

# Export CSV
output_path = f"{EXPORT_DIR}/nighttime_detections.csv"
nighttime.to_csv(output_path, index=False)
print(f"   ✅ {output_path}")

# Export Raven tables per file
for file in nighttime['file_stem'].unique():
    file_detections = nighttime[nighttime['file_stem'] == file].copy()

    audio_file = f"{file}.WAV"
    audio_path = f"/workspace/shared/gaulossen/audio_files/{audio_file}"

    raven_df = create_raven_selection_table(
        file_detections,
        audio_file,
        audio_path,
        default_low_freq=500.0,
        default_high_freq=10000.0
    )

    output_path = f"{EXPORT_DIR}/{file}_nighttime_raven.txt"
    raven_df.to_csv(output_path, sep='\t', index=False)
    print(f"   ✅ {os.path.basename(output_path)} ({len(raven_df)} selections)")

print()

# === SUBSET 3: Top 3 Species Sample (for quality check) ===
print("📦 Subset 3: Top 3 Species Random Sample (50 each)")
print("-" * 80)

top3_species = df['common_name'].value_counts().head(3).index
top3_sample = pd.DataFrame()

for species in top3_species:
    species_data = df[df['common_name'] == species]
    sample = species_data.sample(n=min(50, len(species_data)), random_state=42)
    top3_sample = pd.concat([top3_sample, sample])

top3_sample = top3_sample.sort_values(['common_name', 'confidence'])

print(f"   Total detections: {len(top3_sample)}")
for species in top3_species:
    count = len(top3_sample[top3_sample['common_name'] == species])
    print(f"   {species}: {count} samples")

# Export CSV
output_path = f"{EXPORT_DIR}/top3_species_sample.csv"
top3_sample.to_csv(output_path, index=False)
print(f"   ✅ {output_path}")

# Export combined Raven table (all files together)
for file in top3_sample['file_stem'].unique():
    file_detections = top3_sample[top3_sample['file_stem'] == file].copy()

    audio_file = f"{file}.WAV"
    audio_path = f"/workspace/shared/gaulossen/audio_files/{audio_file}"

    raven_df = create_raven_selection_table(
        file_detections,
        audio_file,
        audio_path,
        default_low_freq=500.0,
        default_high_freq=10000.0
    )

    output_path = f"{EXPORT_DIR}/{file}_top3_sample_raven.txt"
    raven_df.to_csv(output_path, sep='\t', index=False)
    print(f"   ✅ {os.path.basename(output_path)} ({len(raven_df)} selections)")

print()

# === SUBSET 4: Confidence Threshold Comparison ===
print("📦 Subset 4: Confidence Threshold Comparison")
print("-" * 80)

thresholds = [0.25, 0.30, 0.40, 0.50, 0.60, 0.75]
threshold_stats = []

for threshold in thresholds:
    above = df[df['confidence'] >= threshold]
    below = df[df['confidence'] < threshold]

    threshold_stats.append({
        'threshold': threshold,
        'above_count': len(above),
        'above_percent': len(above) / len(df) * 100,
        'below_count': len(below),
        'below_percent': len(below) / len(df) * 100,
        'above_species': above['common_name'].nunique(),
        'below_species': below['common_name'].nunique()
    })

threshold_df = pd.DataFrame(threshold_stats)
print(threshold_df.to_string(index=False))

output_path = f"{EXPORT_DIR}/confidence_threshold_comparison.csv"
threshold_df.to_csv(output_path, index=False)
print(f"\n   ✅ {output_path}")

print()

# === SUBSET 5: Species of Interest (customizable) ===
print("📦 Subset 5: Species of Interest")
print("-" * 80)

# Define species of interest (raptors, owls, waterfowl)
species_of_interest = [
    'Common Buzzard',
    'Eurasian Eagle-Owl',
    'Boreal Owl',
    'Common Crane',
    'Great Bittern',
    'Spotted Crake',
    'Great Snipe'
]

soi = df[df['common_name'].isin(species_of_interest)].copy()
soi = soi.sort_values(['common_name', 'confidence'])

print(f"   Total detections: {len(soi)}")
for species in species_of_interest:
    count = len(soi[soi['common_name'] == species])
    if count > 0:
        mean_conf = soi[soi['common_name'] == species]['confidence'].mean()
        print(f"   {species}: {count} detections (mean conf: {mean_conf:.3f})")

# Export CSV
output_path = f"{EXPORT_DIR}/species_of_interest.csv"
soi.to_csv(output_path, index=False)
print(f"   ✅ {output_path}")

# Export Raven tables per file
for file in soi['file_stem'].unique():
    file_detections = soi[soi['file_stem'] == file].copy()

    audio_file = f"{file}.WAV"
    audio_path = f"/workspace/shared/gaulossen/audio_files/{audio_file}"

    raven_df = create_raven_selection_table(
        file_detections,
        audio_file,
        audio_path,
        default_low_freq=500.0,
        default_high_freq=10000.0
    )

    output_path = f"{EXPORT_DIR}/{file}_species_of_interest_raven.txt"
    raven_df.to_csv(output_path, sep='\t', index=False)
    print(f"   ✅ {os.path.basename(output_path)} ({len(raven_df)} selections)")

print()

# === SUBSET 6: Date-Specific Exports ===
print("📦 Subset 6: Date-Specific Exports")
print("-" * 80)

df['date'] = df['absolute_timestamp'].dt.date

for date in df['date'].unique():
    date_detections = df[df['date'] == date].copy()

    print(f"\n   Date: {date}")
    print(f"   Detections: {len(date_detections)}")
    print(f"   Species: {date_detections['common_name'].nunique()}")

    # Export CSV
    output_path = f"{EXPORT_DIR}/detections_{date}.csv"
    date_detections.to_csv(output_path, index=False)
    print(f"   ✅ {output_path}")

print()

# === SUMMARY ===
print("=" * 80)
print("✅ EXPORT COMPLETE")
print("=" * 80)
print()

print(f"📁 All exports saved to:")
print(f"   {EXPORT_DIR}/")
print()

print(f"📊 Exported Subsets:")
print(f"   1. Low Confidence (conf < 0.40) - {len(low_conf):,} detections")
print(f"   2. Nighttime (00:00-06:00) - {len(nighttime):,} detections")
print(f"   3. Top 3 Species Sample - {len(top3_sample):,} detections")
print(f"   4. Confidence Threshold Comparison - Reference table")
print(f"   5. Species of Interest - {len(soi):,} detections")
print(f"   6. Date-Specific - 3 daily exports")
print()

print(f"🔧 Usage:")
print(f"   - Open any *_raven.txt file in Raven Pro")
print(f"   - Or use CSV files for statistical analysis")
print(f"   - All exports maintain absolute timestamps and metadata")
print()
