#!/usr/bin/env python3
"""
Generate Spectrograms for Top Detections
Creates publication-quality spectrograms for manual review
"""

import pandas as pd
import numpy as np
import librosa
import librosa.display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import soundfile as sf
from pathlib import Path

print("=" * 80)
print("📊 SPECTROGRAM GENERATION")
print("=" * 80)
print()

# Load top 3 per species
top3_df = pd.read_csv('results/top3_per_species.csv')
print(f"📊 Generating spectrograms for {len(top3_df)} detections")
print()

# Create output directory
output_dir = Path('results/spectrograms')
output_dir.mkdir(exist_ok=True)

audio_dir = Path('results/audio_clips_enhanced')

def generate_spectrogram(audio_path, output_path, species_name, confidence):
    """Generate publication-quality spectrogram"""
    try:
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Generate spectrogram
        D = librosa.amplitude_to_db(
            np.abs(librosa.stft(y, n_fft=2048, hop_length=512)),
            ref=np.max
        )

        # Plot
        img = librosa.display.specshow(
            D,
            sr=sr,
            x_axis='time',
            y_axis='hz',
            ax=ax,
            cmap='viridis',
            fmin=200,
            fmax=10000
        )

        # Add colorbar
        cbar = fig.colorbar(img, ax=ax, format='%+2.0f dB')
        cbar.set_label('Amplitude (dB)', rotation=270, labelpad=15)

        # Labels
        ax.set_title(f"{species_name} (Confidence: {confidence:.3f})", fontsize=14, fontweight='bold')
        ax.set_xlabel('Time (s)', fontsize=12)
        ax.set_ylabel('Frequency (Hz)', fontsize=12)

        # Grid
        ax.grid(True, alpha=0.3)

        # Save
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return True

    except Exception as e:
        print(f"  Error: {e}")
        return False

# Generate spectrograms
print("Generating spectrograms...")
print()

generated = 0
skipped = 0

for idx, row in top3_df.iterrows():
    filename_stem = Path(row['filename']).stem
    start_s = row['start_s']
    species = row['common_name']
    confidence = row['confidence']

    # Find matching audio file
    pattern = f"{filename_stem}_{int(start_s)}_*.wav"
    matching_files = list(audio_dir.glob(pattern))

    if not matching_files:
        skipped += 1
        continue

    audio_path = matching_files[0]

    # Create safe filename
    safe_species = species.replace(' ', '_').replace('/', '-')
    output_filename = f"{safe_species}_{filename_stem}_{int(start_s)}.png"
    output_path = output_dir / output_filename

    if generate_spectrogram(audio_path, output_path, species, confidence):
        generated += 1

        if generated % 50 == 0:
            print(f"  Generated {generated}/{len(top3_df)} spectrograms...")

print()
print(f"✅ Generated: {generated} spectrograms")
print(f"   Skipped:   {skipped} (no audio file)")
print(f"   Output:    {output_dir}")
print()

# Create index HTML for easy viewing
print("Creating HTML index...")

html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Gaulosen Spectrograms - Top 3 Per Species</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        h1 { color: #2c3e50; }
        .species-section { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .species-title { color: #27ae60; font-size: 24px; margin-bottom: 15px; border-bottom: 2px solid #27ae60; padding-bottom: 10px; }
        img { width: 100%; max-width: 800px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
        .info { color: #7f8c8d; font-size: 14px; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>🐦 Gaulosen Nature Reserve - Spectrogram Gallery</h1>
    <p><strong>Recording Period:</strong> October 13-15, 2025</p>
    <p><strong>Total Species:</strong> 90 | <strong>Spectrograms:</strong> {}</p>
    <hr>
""".format(generated)

# Group by species
for species in sorted(top3_df['common_name'].unique()):
    species_df = top3_df[top3_df['common_name'] == species]

    html_content += f'<div class="species-section">\n'
    html_content += f'<div class="species-title">{species}</div>\n'

    for idx, row in species_df.iterrows():
        filename_stem = Path(row['filename']).stem
        start_s = row['start_s']
        confidence = row['confidence']

        safe_species = species.replace(' ', '_').replace('/', '-')
        img_filename = f"{safe_species}_{filename_stem}_{int(start_s)}.png"
        img_path = output_dir / img_filename

        if img_path.exists():
            html_content += f'<div class="info">Confidence: {confidence:.3f} | File: {row["filename"]} | Time: {start_s:.1f}s</div>\n'
            html_content += f'<img src="spectrograms/{img_filename}" alt="{species}">\n'

    html_content += '</div>\n'

html_content += """
</body>
</html>
"""

html_path = Path('results/spectrogram_gallery.html')
html_path.write_text(html_content)

print(f"✅ Created HTML gallery: {html_path}")
print()

print("=" * 80)
print("✅ SPECTROGRAM GENERATION COMPLETE")
print("=" * 80)
print()
print(f"Open in browser: file://{html_path.absolute()}")
print()
