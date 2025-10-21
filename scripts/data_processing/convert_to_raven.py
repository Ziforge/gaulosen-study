#!/usr/bin/env python3
"""
Convert Gaulosen BirdNET Results to Raven Pro Format
Uses the Raven MCP functions directly
"""

import os
import sys
import glob
import pandas as pd
from pathlib import Path

# Import from Raven MCP (we'll call the functions directly)
sys.path.insert(0, '/Users/georgeredpath/Dev/mcp-pipeline/raven-mcp')
from server import create_raven_selection_table, normalize_path

print("=" * 80)
print("🐦 CONVERTING GAULOSEN RESULTS TO RAVEN PRO FORMAT")
print("=" * 80)
print()

# Directories
RESULTS_DIR = "/Users/georgeredpath/Dev/mcp-pipeline/shared/gaulosen/results"
OUTPUT_DIR = f"{RESULTS_DIR}/raven_mcp_converted"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Find all detection CSV files
csv_files = sorted(glob.glob(f"{RESULTS_DIR}/csvs/*_detections.csv"))

print(f"📊 Found {len(csv_files)} detection CSV files")
print()

results = []

for csv_file in csv_files:
    file_stem = Path(csv_file).stem.replace("_detections", "")
    audio_file = f"{file_stem}.WAV"
    audio_path = f"/workspace/shared/gaulosen/audio_files/{audio_file}"

    print(f"📄 Processing: {file_stem}")

    try:
        # Load detections
        df = pd.read_csv(csv_file)

        # Rename columns to match expected format
        if 'start_time' in df.columns:
            df = df.rename(columns={'start_time': 'start_s', 'end_time': 'end_s'})

        # Convert to Raven format
        raven_df = create_raven_selection_table(
            df,
            audio_file,
            audio_path,
            default_low_freq=500.0,
            default_high_freq=10000.0
        )

        # Save as tab-delimited text (Raven format)
        output_path = f"{OUTPUT_DIR}/{file_stem}_raven.txt"
        raven_df.to_csv(output_path, sep='\t', index=False)

        print(f"   ✅ Exported {len(raven_df)} selections")
        print(f"   💾 Saved: {output_path}")

        results.append({
            'file': file_stem,
            'selections': len(raven_df),
            'output': output_path,
            'status': 'success'
        })

    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append({
            'file': file_stem,
            'error': str(e),
            'status': 'failed'
        })

    print()

# Summary
print("=" * 80)
print("✅ CONVERSION COMPLETE")
print("=" * 80)

successful = sum(1 for r in results if r['status'] == 'success')
failed = sum(1 for r in results if r['status'] == 'failed')
total_selections = sum(r.get('selections', 0) for r in results if r['status'] == 'success')

print(f"📊 Summary:")
print(f"   Total files: {len(results)}")
print(f"   Successful: {successful}")
print(f"   Failed: {failed}")
print(f"   Total selections: {total_selections:,}")
print()
print(f"📁 Raven Pro selection tables saved to:")
print(f"   {OUTPUT_DIR}/")
print()
print("🔧 To open in Raven Pro:")
print("   1. Open audio file in Raven Pro")
print("   2. File → Import Selections...")
print("   3. Select the corresponding *_raven.txt file")
print()
