#!/usr/bin/env python3
"""
Export Raven Pro Selection Tables
Creates selection tables compatible with Raven Pro for manual review
"""

import pandas as pd
from pathlib import Path

print("=" * 80)
print("📋 RAVEN PRO SELECTION TABLE EXPORT")
print("=" * 80)
print()

# Load all detections
df = pd.read_csv('results/all_detections_with_weather.csv')

# Load top 3 per species for focused review
top3_df = pd.read_csv('results/top3_per_species.csv')

print(f"📊 Dataset: {len(df)} total detections")
print(f"   Top examples: {len(top3_df)} selected for review")
print()

# ============================================================================
# RAVEN PRO FORMAT
# ============================================================================
# Raven expects:
# Selection	View	Channel	Begin Time (s)	End Time (s)	Low Freq (Hz)	High Freq (Hz)	Begin File	File Offset (s)

def create_raven_table(detections_df, output_name):
    """Create Raven Pro selection table"""

    raven_table = []

    for idx, row in detections_df.iterrows():
        selection_number = idx + 1
        begin_time = row['start_s']
        end_time = row['end_s']

        # Estimate frequency range based on common bird ranges
        # Most birds: 500-8000 Hz
        low_freq = 500
        high_freq = 8000

        raven_table.append({
            'Selection': selection_number,
            'View': 'Spectrogram 1',
            'Channel': 1,
            'Begin Time (s)': f"{begin_time:.6f}",
            'End Time (s)': f"{end_time:.6f}",
            'Low Freq (Hz)': low_freq,
            'High Freq (Hz)': high_freq,
            'Begin File': row['filename'],
            'File Offset (s)': 0,
            'Species': row.get('species', row.get('common_name', 'Unknown')),
            'Confidence': f"{row['confidence']:.3f}",
            'Weather': row.get('weather', row.get('weather_summary', 'Unknown'))
        })

    raven_df = pd.DataFrame(raven_table)

    # Save with tab-separated format (Raven standard)
    output_path = f'results/{output_name}.txt'
    raven_df.to_csv(output_path, sep='\t', index=False)

    print(f"✅ Created: {output_path}")
    print(f"   Selections: {len(raven_df)}")
    print()

    return raven_df

# ============================================================================
# CREATE MULTIPLE SELECTION TABLES
# ============================================================================

print("=" * 80)
print("CREATING SELECTION TABLES")
print("=" * 80)
print()

# 1. Top 3 per species (focused review)
print("1. Top 3 Per Species (Manual Review Priority)")
print("-" * 80)
create_raven_table(top3_df, 'raven_selections_top3_per_species')

# 2. High confidence (≥0.70) all species
high_conf = df[df['confidence'] >= 0.70]
print("2. High Confidence Detections (≥0.70)")
print("-" * 80)
create_raven_table(high_conf.head(500), 'raven_selections_high_confidence')

# 3. Nocturnal calls
nocturnal = df[(df['hour'] >= 20) | (df['hour'] <= 6)]
print("3. Nocturnal Calls (20:00-06:00)")
print("-" * 80)
create_raven_table(nocturnal.head(500), 'raven_selections_nocturnal')

# 4. Per-species tables for most common species
print("4. Individual Species Tables (Top 10 Species)")
print("-" * 80)
species_col = 'species' if 'species' in df.columns else 'common_name'
top_species = df[species_col].value_counts().head(10).index.tolist()

for species in top_species:
    species_df = df[df[species_col] == species]
    # Take top 50 by confidence
    species_df_sorted = species_df.nlargest(50, 'confidence')

    safe_species_name = species.replace(' ', '_').replace('/', '-')
    create_raven_table(species_df_sorted, f'raven_selections_{safe_species_name}')

# ============================================================================
# CREATE SUMMARY DOCUMENT
# ============================================================================

print("=" * 80)
print("CREATING REVIEW GUIDE")
print("=" * 80)
print()

with open('results/RAVEN_REVIEW_GUIDE.txt', 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("RAVEN PRO MANUAL REVIEW GUIDE\n")
    f.write("Gaulossen Nature Reserve Acoustic Survey - October 13-15, 2025\n")
    f.write("=" * 80 + "\n\n")

    f.write("OVERVIEW\n")
    f.write("-" * 80 + "\n")
    f.write(f"Total detections:     {len(df)}\n")
    f.write(f"Species detected:     {df['common_name'].nunique()}\n")
    f.write(f"Recording period:     48.8 hours\n\n")

    f.write("SELECTION TABLES CREATED\n")
    f.write("-" * 80 + "\n")
    f.write("1. raven_selections_top3_per_species.txt\n")
    f.write("   → 270 selections (3 per species × 90 species)\n")
    f.write("   → PRIORITY FOR MANUAL REVIEW\n\n")

    f.write("2. raven_selections_high_confidence.txt\n")
    f.write("   → 500 high-confidence detections (≥0.70)\n")
    f.write("   → Quality control verification\n\n")

    f.write("3. raven_selections_nocturnal.txt\n")
    f.write("   → 500 nocturnal calls (20:00-06:00)\n")
    f.write("   → Migration activity\n\n")

    f.write("4. Individual species tables (10 files)\n")
    f.write("   → 50 best examples per common species\n")
    f.write("   → For detailed species-specific review\n\n")

    f.write("HOW TO USE IN RAVEN PRO\n")
    f.write("-" * 80 + "\n")
    f.write("1. Open original WAV file in Raven Pro\n")
    f.write("2. File → Open Selection Table...\n")
    f.write("3. Select corresponding .txt file\n")
    f.write("4. Navigate through selections using arrow keys\n")
    f.write("5. Mark verified/rejected selections\n")
    f.write("6. Export corrected table: File → Export Selection Table As...\n\n")

    f.write("VERIFICATION CRITERIA\n")
    f.write("-" * 80 + "\n")
    f.write("✓ ACCEPT if:\n")
    f.write("  - Clear bird vocalization visible in spectrogram\n")
    f.write("  - Matches expected species characteristics\n")
    f.write("  - Minimal background noise interference\n\n")

    f.write("✗ REJECT if:\n")
    f.write("  - No visible vocalization (false positive)\n")
    f.write("  - Misidentified species (use Raven's annotation)\n")
    f.write("  - Too much noise to confirm\n\n")

    f.write("EXPECTED SPECIES\n")
    f.write("-" * 80 + "\n")
    for i, (species, count) in enumerate(df['common_name'].value_counts().head(20).items(), 1):
        f.write(f"{i:2d}. {species:40s} ({count:4d} detections)\n")

    f.write("\n")
    f.write("=" * 80 + "\n")
    f.write("For questions: https://ravensoundsoftware.com/\n")
    f.write("=" * 80 + "\n")

print("✅ Created review guide: results/RAVEN_REVIEW_GUIDE.txt")
print()

print("=" * 80)
print("✅ RAVEN EXPORT COMPLETE")
print("=" * 80)
print()
print("Files created in results/:")
print("  • raven_selections_*.txt (14 selection tables)")
print("  • RAVEN_REVIEW_GUIDE.txt (instructions)")
print()
