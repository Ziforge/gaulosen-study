#!/usr/bin/env python3
"""
Add spectrogram images to all audio players in the HTML
"""

import re
from pathlib import Path

print("Adding spectrograms to HTML...")

html_file = Path('website/index.html')
html_content = html_file.read_text()

# Define audio files and their corresponding spectrograms
audio_to_spectrogram = {
    '2025-10-14_12h25m_Spotted_Crake_2727s_conf0993.wav': '245AAA0563ED3DA7_20251014_122526_Spotted_Crake_2727s_conf0993.png',
    '2025-10-15_00h00m_Spotted_Crake_42288s_conf0992.wav': '245AAA0563ED3DA7_20251015_000000_Spotted_Crake_42288s_conf0992.png',
    '2025-10-13_11h37m_Spotted_Crake_4251s_conf0992.wav': '245AAA0563ED3DA7_20251013_113753_Spotted_Crake_4251s_conf0992.png',
    '2025-10-15_00h00m_Graylag_Goose_1932s_conf0456.wav': '245AAA0563ED3DA7_20251015_000000_Graylag_Goose_1932s_conf0456.png',
    '2025-10-13_11h37m_Graylag_Goose_7089s_conf0977.wav': '245AAA0563ED3DA7_20251013_113753_Graylag_Goose_7089s_conf0977.png',
    '2025-10-13_11h37m_Spotted_Crake_15s_conf0874.wav': '245AAA0563ED3DA7_20251013_113753_Spotted_Crake_15s_conf0874.png',
    '2025-10-15_00h00m_Graylag_Goose_8685s_conf0332.wav': '245AAA0563ED3DA7_20251015_000000_Graylag_Goose_8685s_conf0332.png',
    '2025-10-14_00h00m_Pink-footed_Goose_43503s_conf0974.wav': '245AAA0563ED3DA7_20251014_000000_Pink-footed_Goose_43503s_conf0974.png',
    '2025-10-14_12h25m_Common_Crane_20082s_conf0763.wav': '245AAA0563ED3DA7_20251014_122526_Common_Crane_20082s_conf0763.png',
}

# Add spectrogram images before each audio element
for audio_file, spectrogram_file in audio_to_spectrogram.items():
    # Skip if already added
    if spectrogram_file in html_content:
        print(f"  Already added: {spectrogram_file}")
        continue

    # Find audio element and add spectrogram before it
    pattern = f'(<h4>.*?</h4>\\n)\\s*(<audio controls>\\n\\s*<source src="results/audio_clips_enhanced/{re.escape(audio_file)}")'
    replacement = f'\\1<img src="results/spectrograms_best/{spectrogram_file}" alt="Spectrogram" class="spectrogram">\\n        \\2'

    new_content = re.sub(pattern, replacement, html_content)

    if new_content != html_content:
        print(f"  Added: {spectrogram_file}")
        html_content = new_content
    else:
        print(f"  Not found: {audio_file}")

# Write updated HTML
html_file.write_text(html_content)

print("\n✅ Spectrograms added to HTML")
print(f"   Total audio players updated: {len([s for s in audio_to_spectrogram.values() if s in html_content])}")
