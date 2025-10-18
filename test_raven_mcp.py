#!/usr/bin/env python3
"""
Test Raven MCP Integration with Gaulossen Results
Demonstrates programmatic access to Raven format conversion
"""

import requests
import json

# MCP Raven server endpoint
RAVEN_MCP_URL = "http://localhost:7085"

print("🐦 Testing Raven MCP Integration with Gaulossen Results")
print("=" * 70)
print()

# Test 1: Export single CSV to Raven format
print("📋 Test 1: Export single detection CSV to Raven format")
print("-" * 70)

response = requests.post(f"{RAVEN_MCP_URL}/tools/export_to_raven", json={
    "detections_csv": "shared/gaulossen/results/csvs/245AAA0563ED3DA7_20251013_113753_detections.csv",
    "output_path": "shared/gaulossen/results/raven_mcp_test/245AAA0563ED3DA7_20251013_113753_raven.txt",
    "audio_file": "245AAA0563ED3DA7_20251013_113753.WAV",
    "audio_path": "shared/gaulossen/audio_files/245AAA0563ED3DA7_20251013_113753.WAV",
    "default_low_freq": 500.0,
    "default_high_freq": 10000.0
})

if response.status_code == 200:
    result = response.json()
    print(f"✅ Success!")
    print(f"   Output: {result.get('output_path')}")
    print(f"   Selections: {result.get('num_selections')}")
    print(f"   Audio file: {result.get('audio_file')}")
else:
    print(f"❌ Error: {response.status_code}")
    print(f"   {response.text}")

print()

# Test 2: Batch export all CSVs
print("📦 Test 2: Batch export all detection CSVs to Raven format")
print("-" * 70)

response = requests.post(f"{RAVEN_MCP_URL}/tools/batch_export_to_raven", json={
    "detections_dir": "shared/gaulossen/results/csvs",
    "output_dir": "shared/gaulossen/results/raven_mcp_batch",
    "audio_dir": "shared/gaulossen/audio_files",
    "file_pattern": "*_detections.csv",
    "default_low_freq": 500.0,
    "default_high_freq": 10000.0
})

if response.status_code == 200:
    result = response.json()
    print(f"✅ Success!")
    print(f"   Total files processed: {result.get('total_files')}")
    print(f"   Successful: {result.get('successful')}")
    print(f"   Failed: {result.get('failed')}")
    print(f"   Output directory: {result.get('output_dir')}")
else:
    print(f"❌ Error: {response.status_code}")
    print(f"   {response.text}")

print()
print("=" * 70)
print("✅ Raven MCP Integration Test Complete!")
print()
print("📁 Check results in:")
print("   - shared/gaulossen/results/raven_mcp_test/")
print("   - shared/gaulossen/results/raven_mcp_batch/")
print()
print("🔧 These Raven selection tables can be opened in Raven Pro:")
print("   File → Import Selections → [select .txt file]")
print()
