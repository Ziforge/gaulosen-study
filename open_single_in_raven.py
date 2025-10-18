#!/usr/bin/env python3
"""
Interactive Raven Pro Opener
Opens one file at a time with its selection table
"""

import os
import subprocess
import glob

# Paths
RAVEN_APP = "/Applications/Raven Pro 1.6/Raven Pro.app"
AUDIO_DIR = "/Users/georgeredpath/Dev/Gaulossen-recordings/audio_files"
RAVEN_TABLES = "/Users/georgeredpath/Dev/mcp-pipeline/shared/gaulossen/results/raven_mcp_converted"

print("🐦 Interactive Raven Pro Opener")
print("=" * 70)
print()

# Find all selection tables
tables = sorted(glob.glob(f"{RAVEN_TABLES}/*_raven.txt"))

if not tables:
    print("❌ No Raven selection tables found!")
    exit(1)

print(f"📊 Found {len(tables)} files to review:")
print()

# List files
for i, table in enumerate(tables, 1):
    basename = os.path.basename(table).replace("_raven.txt", "")
    # Extract date/time from filename
    parts = basename.split("_")
    if len(parts) >= 3:
        date = parts[1]  # YYYYMMDD
        time = parts[2]  # HHMMSS
        date_str = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
        time_str = f"{time[0:2]}:{time[2:4]}:{time[4:6]}"
        print(f"   {i}. {date_str} {time_str}")
    else:
        print(f"   {i}. {basename}")

print()
print("Options:")
print("   Enter number 1-4 to open a specific file")
print("   Enter 'all' to open all files")
print("   Enter 'quit' to exit")
print()

while True:
    choice = input("Select file to open in Raven Pro: ").strip().lower()

    if choice == 'quit' or choice == 'q':
        print("👋 Exiting...")
        break

    if choice == 'all' or choice == 'a':
        print()
        print("📂 Opening all files in Raven Pro...")
        for table in tables:
            basename = os.path.basename(table)
            print(f"   Opening: {basename}")
            subprocess.run(['open', '-a', RAVEN_APP, table])
        print("✅ All files opened!")
        break

    try:
        file_num = int(choice)
        if 1 <= file_num <= len(tables):
            table = tables[file_num - 1]
            basename = os.path.basename(table)
            print()
            print(f"📂 Opening: {basename}")
            subprocess.run(['open', '-a', RAVEN_APP, table])
            print("✅ File opened in Raven Pro!")
            print()

            cont = input("Open another file? (y/n): ").strip().lower()
            if cont != 'y' and cont != 'yes':
                break
            print()
        else:
            print(f"❌ Invalid choice. Please enter 1-{len(tables)}")
    except ValueError:
        print("❌ Invalid input. Please enter a number, 'all', or 'quit'")
    except Exception as e:
        print(f"❌ Error: {e}")

print()
print("📖 In Raven Pro:")
print("   - Selection table is loaded automatically")
print("   - You may need to locate the audio file when prompted")
print("   - Audio files are in: /Users/georgeredpath/Dev/Gaulossen-recordings/audio_files/")
print()
