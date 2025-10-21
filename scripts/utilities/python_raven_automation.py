#!/usr/bin/env python3
"""
Python-based Raven Selection Table Automation
No R dependencies - pure Python implementation
"""

import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path

print("=" * 80)
print("🔊 PYTHON-BASED RAVEN SELECTION TABLE AUTOMATION")
print("=" * 80)
print()

# Configuration
RAVEN_TABLES_DIR = "results/verification_reports"
AUDIO_DIR = "/Users/georgeredpath/Dev/Gaulosen-recordings/audio_files"
OUTPUT_DIR = "results/python_raven_automated"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("📊 Configuration:")
print(f"   Raven tables: {RAVEN_TABLES_DIR}")
print(f"   Audio files: {AUDIO_DIR}")
print(f"   Output: {OUTPUT_DIR}")
print()

# ==============================================================================
# STEP 1: Import High Priority Raven Selection Tables
# ==============================================================================

print("📥 Step 1: Importing high priority Raven selection tables...")
print("-" * 80)

high_priority_files = glob.glob(f"{RAVEN_TABLES_DIR}/*_high_priority_raven.txt")

print(f"   Found {len(high_priority_files)} high priority files\n")

# Import all high priority selections
all_hp_selections = []

for file in high_priority_files:
    print(f"   📄 Importing: {os.path.basename(file)}")

    # Read tab-delimited Raven format
    df = pd.read_csv(file, sep='\t')

    if len(df) > 0:
        all_hp_selections.append(df)
        print(f"      ✅ Imported {len(df)} selections")

if all_hp_selections:
    all_hp_df = pd.concat(all_hp_selections, ignore_index=True)
else:
    all_hp_df = pd.DataFrame()

print(f"\n   Total high priority selections imported: {len(all_hp_df)}\n")

# ==============================================================================
# STEP 2: Quality Metrics Calculation
# ==============================================================================

print("📊 Step 2: Calculating quality metrics...")
print("-" * 80)

if len(all_hp_df) > 0:
    # Calculate duration
    all_hp_df['duration'] = all_hp_df['End Time (s)'] - all_hp_df['Begin Time (s)']

    # Calculate bandwidth
    all_hp_df['bandwidth'] = all_hp_df['High Freq (Hz)'] - all_hp_df['Low Freq (Hz)']

    # Quality flags
    all_hp_df['flag_short_duration'] = all_hp_df['duration'] < 0.5
    all_hp_df['flag_wide_bandwidth'] = all_hp_df['bandwidth'] > 8000
    all_hp_df['flag_narrow_bandwidth'] = all_hp_df['bandwidth'] < 500
    all_hp_df['flag_low_frequency'] = all_hp_df['Low Freq (Hz)'] < 200
    all_hp_df['flag_high_frequency'] = all_hp_df['High Freq (Hz)'] > 12000

    # Quality score (0 = best, higher = more suspicious)
    all_hp_df['quality_score'] = (
        all_hp_df['flag_short_duration'].astype(int) +
        all_hp_df['flag_wide_bandwidth'].astype(int) +
        all_hp_df['flag_narrow_bandwidth'].astype(int) +
        all_hp_df['flag_low_frequency'].astype(int) +
        all_hp_df['flag_high_frequency'].astype(int)
    )

    print(f"   Duration range: {all_hp_df['duration'].min():.2f} - {all_hp_df['duration'].max():.2f} seconds")
    print(f"   Bandwidth range: {all_hp_df['bandwidth'].min():.0f} - {all_hp_df['bandwidth'].max():.0f} Hz")
    print(f"   Short duration flags: {all_hp_df['flag_short_duration'].sum()}")
    print(f"   Wide bandwidth flags: {all_hp_df['flag_wide_bandwidth'].sum()}")
    print(f"   Narrow bandwidth flags: {all_hp_df['flag_narrow_bandwidth'].sum()}")
    print(f"   Low frequency flags: {all_hp_df['flag_low_frequency'].sum()}")
    print(f"   High frequency flags: {all_hp_df['flag_high_frequency'].sum()}")
    print()

    # Suspicious detections (quality score > 0)
    suspicious = all_hp_df[all_hp_df['quality_score'] > 0]
    print(f"   Suspicious detections (quality score > 0): {len(suspicious)}")
    if len(suspicious) > 0:
        print(f"   Most suspicious: quality score {all_hp_df['quality_score'].max()}")
    print()

# ==============================================================================
# STEP 3: Export Enhanced Selection Tables
# ==============================================================================

print("📤 Step 3: Exporting enhanced selection tables...")
print("-" * 80)

if len(all_hp_df) > 0:
    # Save combined high priority table (Raven format)
    output_file = f"{OUTPUT_DIR}/high_priority_enhanced.txt"
    all_hp_df.to_csv(output_file, sep='\t', index=False)
    print(f"   ✅ Exported: {os.path.basename(output_file)}")

    # Save CSV for analysis
    csv_file = f"{OUTPUT_DIR}/high_priority_enhanced.csv"
    all_hp_df.to_csv(csv_file, index=False)
    print(f"   ✅ Exported: {os.path.basename(csv_file)}")

    # Save suspicious detections only
    if len(suspicious) > 0:
        susp_file = f"{OUTPUT_DIR}/suspicious_detections.csv"
        suspicious.to_csv(susp_file, index=False)
        print(f"   ✅ Exported: {os.path.basename(susp_file)} ({len(suspicious)} detections)")
    print()

# ==============================================================================
# STEP 4: Species-Level Summary
# ==============================================================================

print("📊 Step 4: Generating species-level summary...")
print("-" * 80)

if len(all_hp_df) > 0 and 'Common Name' in all_hp_df.columns:
    species_summary = all_hp_df.groupby('Common Name').agg({
        'duration': ['count', 'mean', 'std'],
        'bandwidth': ['mean', 'std'],
        'Confidence': ['mean', 'std', 'min', 'max'],
        'quality_score': 'mean'
    }).round(3)

    species_summary.columns = ['_'.join(col).strip() for col in species_summary.columns.values]

    print("\n   Species Summary:")
    print(species_summary.to_string())

    # Export species summary
    csv_file = f"{OUTPUT_DIR}/species_summary_python.csv"
    species_summary.to_csv(csv_file)
    print(f"\n   ✅ Exported: {os.path.basename(csv_file)}\n")

# ==============================================================================
# STEP 5: Import All Rare Species Tables
# ==============================================================================

print("📥 Step 5: Importing rare species Raven selection tables...")
print("-" * 80)

rare_species_files = glob.glob(f"{RAVEN_TABLES_DIR}/*_rare_species_raven.txt")

print(f"   Found {len(rare_species_files)} rare species files\n")

all_rare_selections = []

for file in rare_species_files:
    print(f"   📄 Importing: {os.path.basename(file)}")

    df = pd.read_csv(file, sep='\t')

    if len(df) > 0:
        all_rare_selections.append(df)
        print(f"      ✅ Imported {len(df)} selections")

if all_rare_selections:
    all_rare_df = pd.concat(all_rare_selections, ignore_index=True)
else:
    all_rare_df = pd.DataFrame()

print(f"\n   Total rare species selections imported: {len(all_rare_df)}\n")

# Export rare species combined table
if len(all_rare_df) > 0:
    # Add quality metrics
    all_rare_df['duration'] = all_rare_df['End Time (s)'] - all_rare_df['Begin Time (s)']
    all_rare_df['bandwidth'] = all_rare_df['High Freq (Hz)'] - all_rare_df['Low Freq (Hz)']

    output_file = f"{OUTPUT_DIR}/rare_species_combined.txt"
    all_rare_df.to_csv(output_file, sep='\t', index=False)
    print(f"   ✅ Exported: {os.path.basename(output_file)}")

    csv_file = f"{OUTPUT_DIR}/rare_species_combined.csv"
    all_rare_df.to_csv(csv_file, index=False)
    print(f"   ✅ Exported: {os.path.basename(csv_file)}\n")

# ==============================================================================
# STEP 6: Frequency Analysis
# ==============================================================================

print("📊 Step 6: Frequency range analysis...")
print("-" * 80)

if len(all_hp_df) > 0:
    # Bin frequencies
    freq_bins = [0, 500, 1000, 2000, 4000, 8000, 12000, 20000]
    all_hp_df['freq_bin'] = pd.cut(
        all_hp_df['Low Freq (Hz)'],
        bins=freq_bins,
        labels=['<500', '500-1k', '1k-2k', '2k-4k', '4k-8k', '8k-12k', '>12k']
    )

    freq_dist = all_hp_df['freq_bin'].value_counts().sort_index()
    print("\n   Frequency Distribution (Low Freq):")
    for freq, count in freq_dist.items():
        print(f"   {freq:>10}: {count:>3} detections")

    print()

# ==============================================================================
# SUMMARY
# ==============================================================================

print("=" * 80)
print("✅ PYTHON RAVEN AUTOMATION COMPLETE")
print("=" * 80)
print()

print("📊 Summary:")
print(f"   High priority selections processed: {len(all_hp_df)}")
print(f"   Rare species selections processed: {len(all_rare_df)}")
print(f"   Total selections: {len(all_hp_df) + len(all_rare_df)}")
if len(all_hp_df) > 0:
    print(f"   Suspicious detections flagged: {len(suspicious)}")
    print(f"   Unique species (HP): {all_hp_df['Common Name'].nunique() if 'Common Name' in all_hp_df.columns else 'N/A'}")
print()

print("📁 Output files in results/python_raven_automated/:")
print("   - high_priority_enhanced.txt (Raven format)")
print("   - high_priority_enhanced.csv (for analysis)")
print("   - suspicious_detections.csv (flagged detections)")
print("   - rare_species_combined.txt (Raven format)")
print("   - rare_species_combined.csv (for analysis)")
print("   - species_summary_python.csv (statistics)")
print()

print("🔧 Next Steps:")
print("   1. Open *_enhanced.txt files in Raven Pro")
print("   2. Review suspicious_detections.csv for problematic calls")
print("   3. Use CSV files for statistical analysis")
print("   4. Import enhanced tables back into Raven Pro")
print()

print("📊 Quality Flags Explained:")
print("   - flag_short_duration: < 0.5 seconds")
print("   - flag_wide_bandwidth: > 8000 Hz (unnaturally wide)")
print("   - flag_narrow_bandwidth: < 500 Hz (too narrow for most birds)")
print("   - flag_low_frequency: < 200 Hz (below bird range)")
print("   - flag_high_frequency: > 12000 Hz (ultrasonic)")
print("   - quality_score: Sum of all flags (0 = best)")
print()
