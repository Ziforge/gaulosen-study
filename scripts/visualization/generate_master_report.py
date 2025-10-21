#!/usr/bin/env python3
"""
Master Analysis Report
Compiles all analyses into a comprehensive scientific report
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("📄 GENERATING MASTER ANALYSIS REPORT")
print("=" * 80)
print()

# Load all data
df = pd.read_csv('results/all_detections_with_weather.csv')
df['datetime'] = pd.to_datetime(df['absolute_timestamp'])

# Load analysis results
try:
    migration_df = pd.read_csv('results/migration_detections.csv')
    flight_df = pd.read_csv('results/flight_calls.csv')
    territorial_df = pd.read_csv('results/territorial_behavior.csv')
    top3_df = pd.read_csv('results/top3_per_species.csv')
except:
    migration_df = flight_df = territorial_df = top3_df = None

print("Compiling comprehensive report...")
print()

# ============================================================================
# CREATE MASTER REPORT
# ============================================================================

report = []

report.append("=" * 100)
report.append("GAULOSEN NATURE RESERVE ACOUSTIC SURVEY")
report.append("Comprehensive Bioacoustic Analysis Report")
report.append("=" * 100)
report.append("")
report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append(f"Analysis Period: {df['datetime'].min()} to {df['datetime'].max()}")
report.append(f"Duration: {(df['datetime'].max() - df['datetime'].min()).total_seconds() / 3600:.1f} hours")
report.append("")

# ============================================================================
# EXECUTIVE SUMMARY
# ============================================================================

report.append("=" * 100)
report.append("EXECUTIVE SUMMARY")
report.append("=" * 100)
report.append("")

report.append(f"Total Detections:          {len(df):,}")
report.append(f"Species Detected:          {df['common_name'].nunique()}")
report.append(f"Recording Files:           {df['filename'].nunique()}")
report.append(f"Average Confidence:        {df['confidence'].mean():.3f}")
report.append(f"High Confidence (≥0.70):   {len(df[df['confidence'] >= 0.70]):,} ({len(df[df['confidence'] >= 0.70])/len(df)*100:.1f}%)")
report.append("")

# Top species
top_10_species = df['common_name'].value_counts().head(10)
report.append("Top 10 Most Detected Species:")
report.append("-" * 100)
for i, (species, count) in enumerate(top_10_species.items(), 1):
    pct = count / len(df) * 100
    report.append(f"  {i:2d}. {species:45s} {count:5,d} detections ({pct:5.1f}%)")
report.append("")

# ============================================================================
# MIGRATION ANALYSIS
# ============================================================================

report.append("=" * 100)
report.append("MIGRATION TIMING ANALYSIS")
report.append("=" * 100)
report.append("")

if migration_df is not None:
    report.append(f"Migrant Detections:        {len(migration_df):,} ({len(migration_df)/len(df)*100:.1f}% of total)")
    report.append(f"Migrant Species:           {migration_df['common_name'].nunique()}")

    # Nocturnal migration
    nocturnal = df[(df['hour'] >= 20) | (df['hour'] <= 6)]
    report.append(f"Nocturnal Calls:           {len(nocturnal):,} ({len(nocturnal)/len(df)*100:.1f}%)")

    report.append("")
    report.append("Peak Migration Hours:")
    hourly = df.groupby('hour').size()
    peak_hours = hourly.nlargest(5)
    for hour, count in peak_hours.items():
        report.append(f"  {hour:02d}:00 - {count:,d} detections")
    report.append("")

# ============================================================================
# BEHAVIORAL PATTERNS
# ============================================================================

report.append("=" * 100)
report.append("BEHAVIORAL ECOLOGY")
report.append("=" * 100)
report.append("")

if flight_df is not None:
    flight_behaviors = flight_df['behavior'].value_counts()
    report.append("Flight Call Behaviors:")
    for behavior, count in flight_behaviors.items():
        report.append(f"  {behavior.replace('_', ' ').title():25s} {count:4d} detections")
    report.append("")

if territorial_df is not None:
    report.append(f"Territorial Behavior:      {len(territorial_df)} instances detected")
    report.append("Top territorial species:")
    for idx, row in territorial_df.head(5).iterrows():
        report.append(f"  {row['common_name']:35s} {int(row['call_count']):4d} calls, {row['calls_per_hour']:.1f} calls/hr")
    report.append("")

# ============================================================================
# TEMPORAL PATTERNS
# ============================================================================

report.append("=" * 100)
report.append("TEMPORAL PATTERNS")
report.append("=" * 100)
report.append("")

# Diel activity
dawn = df[(df['hour'] >= 4) & (df['hour'] <= 8)]
day = df[(df['hour'] > 8) & (df['hour'] < 18)]
dusk = df[(df['hour'] >= 18) & (df['hour'] < 22)]
night = df[((df['hour'] >= 22) | (df['hour'] < 4))]

report.append("Activity Distribution:")
report.append(f"  Dawn (04:00-08:00):       {len(dawn):5,d} calls ({len(dawn)/len(df)*100:5.1f}%)")
report.append(f"  Day (08:00-18:00):        {len(day):5,d} calls ({len(day)/len(df)*100:5.1f}%)")
report.append(f"  Dusk (18:00-22:00):       {len(dusk):5,d} calls ({len(dusk)/len(df)*100:5.1f}%)")
report.append(f"  Night (22:00-04:00):      {len(night):5,d} calls ({len(night)/len(df)*100:5.1f}%)")
report.append("")

# ============================================================================
# WEATHER CORRELATIONS
# ============================================================================

report.append("=" * 100)
report.append("WEATHER CORRELATIONS")
report.append("=" * 100)
report.append("")

weather_summary = df.groupby('weather_summary').size().sort_values(ascending=False)
report.append("Detections by Weather Condition:")
for weather, count in weather_summary.items():
    pct = count / len(df) * 100
    report.append(f"  {weather:35s} {count:5,d} calls ({pct:5.1f}%)")
report.append("")

# ============================================================================
# DATA QUALITY METRICS
# ============================================================================

report.append("=" * 100)
report.append("DATA QUALITY ASSESSMENT")
report.append("=" * 100)
report.append("")

# Confidence distribution
high_conf = len(df[df['confidence'] >= 0.70])
med_conf = len(df[(df['confidence'] >= 0.50) & (df['confidence'] < 0.70)])
low_conf = len(df[df['confidence'] < 0.50])

report.append("Confidence Distribution:")
report.append(f"  High (≥0.70):             {high_conf:5,d} ({high_conf/len(df)*100:5.1f}%)")
report.append(f"  Medium (0.50-0.70):       {med_conf:5,d} ({med_conf/len(df)*100:5.1f}%)")
report.append(f"  Low (<0.50):              {low_conf:5,d} ({low_conf/len(df)*100:5.1f}%)")
report.append("")

# ============================================================================
# SPECIES RICHNESS
# ============================================================================

report.append("=" * 100)
report.append("SPECIES RICHNESS & DIVERSITY")
report.append("=" * 100)
report.append("")

report.append(f"Total Species Detected:    {df['common_name'].nunique()}")
report.append("")

# Species by number of detections
single_det = len(df.groupby('common_name').filter(lambda x: len(x) == 1).groupby('common_name').size())
few_det = len(df.groupby('common_name').filter(lambda x: 2 <= len(x) <= 5).groupby('common_name').size())
many_det = len(df.groupby('common_name').filter(lambda x: len(x) > 5).groupby('common_name').size())

report.append("Species by Detection Frequency:")
report.append(f"  Single detection:         {single_det} species")
report.append(f"  2-5 detections:           {few_det} species")
report.append(f"  >5 detections:            {many_det} species")
report.append("")

# ============================================================================
# FILES GENERATED
# ============================================================================

report.append("=" * 100)
report.append("OUTPUT FILES")
report.append("=" * 100)
report.append("")

results_dir = Path('results')
csv_files = sorted(results_dir.glob('*.csv'))
txt_files = sorted(results_dir.glob('*.txt'))

report.append("CSV Data Files:")
for f in csv_files:
    file_size = f.stat().st_size / 1024
    report.append(f"  {f.name:50s} ({file_size:.1f} KB)")
report.append("")

report.append("Analysis Reports:")
for f in txt_files:
    report.append(f"  {f.name}")
report.append("")

# Check for spectrograms
spec_dir = results_dir / 'spectrograms'
if spec_dir.exists():
    n_spectrograms = len(list(spec_dir.glob('*.png')))
    report.append(f"Spectrograms:              {n_spectrograms} images")
    report.append("")

# Check for enhanced audio
audio_dir = results_dir / 'audio_clips_enhanced'
if audio_dir.exists():
    n_audio = len(list(audio_dir.glob('*.wav')))
    report.append(f"Enhanced Audio Clips:      {n_audio} files")
    report.append("")

# ============================================================================
# RECOMMENDED NEXT STEPS
# ============================================================================

report.append("=" * 100)
report.append("RECOMMENDED NEXT STEPS")
report.append("=" * 100)
report.append("")

report.append("1. MANUAL VERIFICATION")
report.append("   → Review top3_per_species selections in Raven Pro")
report.append("   → Use raven_selections_*.txt tables")
report.append("   → Verify species identifications")
report.append("")

report.append("2. SPECTROGRAM REVIEW")
report.append("   → Open spectrogram_gallery.html in web browser")
report.append("   → Visual inspection of call structures")
report.append("   → Identify any misclassifications")
report.append("")

report.append("3. PUBLICATION PREPARATION")
report.append("   → Use high-confidence detections (≥0.70)")
report.append("   → Focus on species with multiple detections")
report.append("   → Include migration wave analysis")
report.append("")

report.append("4. FURTHER ANALYSIS")
report.append("   → Compare with historical Gaulosen data")
report.append("   → Correlate with weather patterns")
report.append("   → Analyze seasonal trends if more data available")
report.append("")

# ============================================================================
# CITATION & ACKNOWLEDGMENTS
# ============================================================================

report.append("=" * 100)
report.append("METHODS & SOFTWARE")
report.append("=" * 100)
report.append("")

report.append("Detection Software:        BirdNET v2.4 (Cornell Lab of Ornithology)")
report.append("Analysis Tools:            Python 3.x, librosa, pandas, numpy, scikit-learn")
report.append("Audio Processing:          Advanced DSP denoising pipeline")
report.append("                           (Wiener filtering, spectral subtraction, HPSS)")
report.append("")

report.append("Reference:")
report.append("Kahl, S., Wood, C.M., Eibl, M., & Klinck, H. (2021).")
report.append("BirdNET: A deep learning solution for avian diversity monitoring.")
report.append("Ecological Informatics, 61, 101236.")
report.append("")

report.append("=" * 100)
report.append("END OF REPORT")
report.append("=" * 100)

# ============================================================================
# SAVE REPORT
# ============================================================================

report_text = "\n".join(report)
output_path = Path('results/MASTER_ANALYSIS_REPORT.txt')
output_path.write_text(report_text)

print(f"✅ Generated master report: {output_path}")
print(f"   Length: {len(report)} lines")
print()

# Also print to console
print("=" * 80)
print("PREVIEW OF MASTER REPORT")
print("=" * 80)
print()
for line in report[:50]:  # First 50 lines
    print(line)
print()
print("[... report continues ...]")
print()

print("=" * 80)
print("✅ MASTER REPORT GENERATION COMPLETE")
print("=" * 80)
print()
