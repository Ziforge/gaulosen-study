#!/usr/bin/env python3
"""
Automated Detection Quality Assessment
Analyzes BirdNET detections and flags potentially problematic ones for manual review
"""

import pandas as pd
import numpy as np
import glob
import os
from pathlib import Path

print("=" * 80)
print("🔍 AUTOMATED DETECTION QUALITY ASSESSMENT")
print("=" * 80)
print()

# Configuration
RESULTS_DIR = "/Users/georgeredpath/Dev/mcp-pipeline/shared/gaulossen/results"
OUTPUT_DIR = f"{RESULTS_DIR}/verification_reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Quality thresholds
CONFIDENCE_HIGH = 0.75  # High confidence - likely correct
CONFIDENCE_MEDIUM = 0.50  # Medium - review recommended
CONFIDENCE_LOW = 0.25  # Low - definitely review

# Duration thresholds (seconds)
DURATION_TOO_SHORT = 0.5  # Suspiciously short
DURATION_TOO_LONG = 10.0  # Suspiciously long for most calls

# Load all detections
print("📊 Loading detection data...")
all_detections_path = f"{RESULTS_DIR}/all_detections.csv"
df = pd.read_csv(all_detections_path)

print(f"   Total detections: {len(df):,}")
print()

# Calculate detection duration
df['duration'] = df['end_s'] - df['start_s']

# Quality flags
quality_issues = []

print("🔍 Running quality checks...")
print("-" * 80)

# 1. Confidence-based filtering
low_conf = df[df['confidence'] < CONFIDENCE_LOW]
medium_conf = df[(df['confidence'] >= CONFIDENCE_LOW) & (df['confidence'] < CONFIDENCE_MEDIUM)]
high_conf = df[df['confidence'] >= CONFIDENCE_MEDIUM]

print(f"📊 Confidence Distribution:")
print(f"   High confidence (≥{CONFIDENCE_MEDIUM}):   {len(high_conf):>5,} ({len(high_conf)/len(df)*100:>5.1f}%)")
print(f"   Medium confidence ({CONFIDENCE_LOW}-{CONFIDENCE_MEDIUM}): {len(medium_conf):>5,} ({len(medium_conf)/len(df)*100:>5.1f}%)")
print(f"   Low confidence (<{CONFIDENCE_LOW}):     {len(low_conf):>5,} ({len(low_conf)/len(df)*100:>5.1f}%)")
print()

# 2. Duration analysis
short_calls = df[df['duration'] < DURATION_TOO_SHORT]
long_calls = df[df['duration'] > DURATION_TOO_LONG]

print(f"⏱️  Duration Analysis:")
print(f"   Mean duration:     {df['duration'].mean():.2f}s")
print(f"   Median duration:   {df['duration'].median():.2f}s")
print(f"   Too short (<{DURATION_TOO_SHORT}s): {len(short_calls):>5,} ({len(short_calls)/len(df)*100:>5.1f}%)")
print(f"   Too long (>{DURATION_TOO_LONG}s):  {len(long_calls):>5,} ({len(long_calls)/len(df)*100:>5.1f}%)")
print()

# 3. Rare species detection (potential false positives)
species_counts = df['common_name'].value_counts()
rare_species = species_counts[species_counts == 1].index.tolist()
rare_detections = df[df['common_name'].isin(rare_species)]

print(f"🦅 Rare Species (single detection):")
print(f"   Species count: {len(rare_species)}")
print(f"   Detections:    {len(rare_detections)}")
print(f"   Species: {', '.join(rare_species[:10])}")
if len(rare_species) > 10:
    print(f"            ... and {len(rare_species) - 10} more")
print()

# Use 'file_stem' as the file identifier
df['file'] = df['file_stem']

# 4. Temporal clustering analysis (multiple detections in short time)
df_sorted = df.sort_values(['file_stem', 'start_s'])
df_sorted['time_since_last'] = df_sorted.groupby('file_stem')['start_s'].diff()

# Detections within 3 seconds of each other (potential duplicates)
rapid_succession = df_sorted[df_sorted['time_since_last'] < 3.0]

print(f"⚡ Temporal Clustering:")
print(f"   Detections within 3s of previous: {len(rapid_succession):,}")
print(f"   (Potential duplicates or overlapping calls)")
print()

# 5. Priority review list
print("🎯 Priority Review Categories:")
print("-" * 80)

# High priority: Low confidence + rare species
high_priority = df[
    (df['confidence'] < CONFIDENCE_MEDIUM) &
    (df['common_name'].isin(rare_species))
]
print(f"1. HIGH PRIORITY - Low confidence rare species:  {len(high_priority):>5,}")

# Medium priority: Unusual duration + medium confidence
medium_priority = df[
    (df['confidence'] < CONFIDENCE_HIGH) &
    ((df['duration'] < DURATION_TOO_SHORT) | (df['duration'] > DURATION_TOO_LONG))
]
print(f"2. MEDIUM PRIORITY - Unusual duration:           {len(medium_priority):>5,}")

# All rare species
print(f"3. ALL RARE SPECIES - Single detections:         {len(rare_detections):>5,}")

# Low confidence common species
low_conf_common = df[
    (df['confidence'] < CONFIDENCE_MEDIUM) &
    (~df['common_name'].isin(rare_species))
]
print(f"4. LOW PRIORITY - Low confidence common:         {len(low_conf_common):>5,}")
print()

# Generate verification reports
print("📝 Generating verification reports...")

# Report 1: High priority review list
high_priority_sorted = high_priority.sort_values('confidence')
high_priority_report = high_priority_sorted[[
    'file_stem', 'start_s', 'end_s', 'duration', 'common_name',
    'scientific_name', 'confidence', 'absolute_timestamp'
]].copy()
high_priority_report['review_reason'] = 'Low confidence + rare species'
high_priority_report = high_priority_report.rename(columns={'file_stem': 'file'})

output_path = f"{OUTPUT_DIR}/high_priority_review.csv"
high_priority_report.to_csv(output_path, index=False)
print(f"   ✅ {output_path}")

# Report 2: Rare species (all)
rare_sorted = rare_detections.sort_values('confidence')
rare_report = rare_sorted[[
    'file_stem', 'start_s', 'end_s', 'duration', 'common_name',
    'scientific_name', 'confidence', 'absolute_timestamp'
]].copy()
rare_report['review_reason'] = 'Single detection (rare)'
rare_report = rare_report.rename(columns={'file_stem': 'file'})

output_path = f"{OUTPUT_DIR}/rare_species_review.csv"
rare_report.to_csv(output_path, index=False)
print(f"   ✅ {output_path}")

# Report 3: Duration anomalies
duration_anomalies = pd.concat([
    short_calls.assign(review_reason='Duration too short'),
    long_calls.assign(review_reason='Duration too long')
])
duration_report = duration_anomalies[[
    'file_stem', 'start_s', 'end_s', 'duration', 'common_name',
    'scientific_name', 'confidence', 'absolute_timestamp', 'review_reason'
]].copy()
duration_report = duration_report.rename(columns={'file_stem': 'file'})
duration_report = duration_report.sort_values('duration')

output_path = f"{OUTPUT_DIR}/duration_anomalies.csv"
duration_report.to_csv(output_path, index=False)
print(f"   ✅ {output_path}")

# Report 4: Confidence summary by species
species_confidence = df.groupby('common_name').agg({
    'confidence': ['count', 'mean', 'std', 'min', 'max'],
    'duration': 'mean'
}).round(3)
species_confidence.columns = ['count', 'conf_mean', 'conf_std', 'conf_min', 'conf_max', 'dur_mean']
species_confidence = species_confidence.sort_values('count', ascending=False)

output_path = f"{OUTPUT_DIR}/species_confidence_summary.csv"
species_confidence.to_csv(output_path)
print(f"   ✅ {output_path}")

# Report 5: Master verification checklist (combines all flags)
df_verify = df.copy()
df_verify['flag_low_confidence'] = df_verify['confidence'] < CONFIDENCE_MEDIUM
df_verify['flag_rare_species'] = df_verify['common_name'].isin(rare_species)
df_verify['flag_short_duration'] = df_verify['duration'] < DURATION_TOO_SHORT
df_verify['flag_long_duration'] = df_verify['duration'] > DURATION_TOO_LONG
df_verify['total_flags'] = (
    df_verify['flag_low_confidence'].astype(int) +
    df_verify['flag_rare_species'].astype(int) +
    df_verify['flag_short_duration'].astype(int) +
    df_verify['flag_long_duration'].astype(int)
)

# Priority score (higher = needs review more)
df_verify['priority_score'] = (
    df_verify['flag_rare_species'].astype(int) * 3 +
    df_verify['flag_low_confidence'].astype(int) * 2 +
    df_verify['flag_short_duration'].astype(int) * 1 +
    df_verify['flag_long_duration'].astype(int) * 1
)

df_verify_sorted = df_verify.sort_values('priority_score', ascending=False)

output_path = f"{OUTPUT_DIR}/master_verification_checklist.csv"
df_verify_sorted.to_csv(output_path, index=False)
print(f"   ✅ {output_path}")

print()
print("=" * 80)
print("✅ QUALITY ASSESSMENT COMPLETE")
print("=" * 80)
print()

# Summary statistics
needs_review = df_verify[df_verify['total_flags'] > 0]
print(f"📊 Verification Summary:")
print(f"   Total detections:           {len(df):>6,}")
print(f"   Flagged for review:         {len(needs_review):>6,} ({len(needs_review)/len(df)*100:.1f}%)")
print(f"   High confidence, no flags:  {len(df) - len(needs_review):>6,} ({(len(df) - len(needs_review))/len(df)*100:.1f}%)")
print()

print(f"🎯 Recommended Review Order:")
print(f"   1. High priority (rare + low conf):  {len(high_priority):>5,} detections")
print(f"   2. All rare species:                  {len(rare_detections):>5,} detections")
print(f"   3. Duration anomalies:                {len(duration_anomalies):>5,} detections")
print(f"   4. Use master checklist sorted by priority_score")
print()

print(f"📁 Reports saved to:")
print(f"   {OUTPUT_DIR}/")
print()

print(f"🔧 Next Steps:")
print(f"   1. Review high_priority_review.csv first (most important)")
print(f"   2. Use master_verification_checklist.csv in Raven Pro")
print(f"   3. Sort by 'priority_score' column (highest first)")
print(f"   4. Focus on detections with multiple flags")
print()

# Generate a quick-open script for priority detections
print("📝 Generating filtered Raven selection tables...")

for priority_level, (df_subset, filename) in enumerate([
    (high_priority, "high_priority"),
    (rare_detections, "rare_species"),
], 1):
    if len(df_subset) == 0:
        continue

    # Group by file
    for file in df_subset['file_stem'].unique():
        file_detections = df_subset[df_subset['file_stem'] == file].copy()

        # Create Raven-format table
        import sys
        sys.path.insert(0, '/Users/georgeredpath/Dev/mcp-pipeline/raven-mcp')
        from server import create_raven_selection_table

        # Prepare data (columns already named start_s, end_s)

        audio_file = f"{file}.WAV"
        audio_path = f"/workspace/shared/gaulossen/audio_files/{audio_file}"

        raven_df = create_raven_selection_table(
            file_detections,
            audio_file,
            audio_path,
            default_low_freq=500.0,
            default_high_freq=10000.0
        )

        # Save filtered table
        output_file = f"{OUTPUT_DIR}/{file}_{filename}_raven.txt"
        raven_df.to_csv(output_file, sep='\t', index=False)
        print(f"   ✅ {os.path.basename(output_file)} ({len(raven_df)} selections)")

print()
print("🎯 You can now open these filtered tables in Raven Pro to focus on")
print("   detections that need verification!")
print()
