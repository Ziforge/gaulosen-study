#!/usr/bin/env python3
"""
Generate spectrograms and compile audio samples for key behavioral findings.
Creates a comprehensive report with visual and audio evidence.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import librosa
import librosa.display
from datetime import datetime
import shutil

print("="*80)
print("BEHAVIORAL FINDINGS - EXAMPLE GENERATION")
print("="*80)
print()

# Create output directories
SPEC_DIR = Path("results/behavioral_spectrograms")
AUDIO_DIR = Path("results/behavioral_audio_examples")
SPEC_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

# Load data
detections = pd.read_csv('results/verified_detections.csv')
detections['absolute_timestamp'] = pd.to_datetime(detections['absolute_timestamp'])
detections['hour'] = detections['absolute_timestamp'].dt.hour

# Raven Pro-style spectrogram settings
SAMPLE_RATE = 44100
N_FFT = 2048
HOP_LENGTH = 512
FREQ_MAX = 12000

def create_spectrogram(audio_path, output_path, title):
    """Create Raven Pro-style spectrogram"""
    y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)
    y = librosa.effects.preemphasis(y, coef=0.97)

    D = librosa.stft(y, n_fft=N_FFT, hop_length=HOP_LENGTH, window='hamming')
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

    fig, ax = plt.subplots(figsize=(14, 6), facecolor='black')

    img = librosa.display.specshow(
        S_db, sr=sr, hop_length=HOP_LENGTH,
        x_axis='time', y_axis='hz', cmap='hot', ax=ax,
        vmin=-80, vmax=0
    )

    ax.set_ylim([0, FREQ_MAX])
    ax.set_facecolor('black')
    ax.set_xlabel('Time (s)', color='white', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency (Hz)', color='white', fontsize=12, fontweight='bold')
    ax.tick_params(colors='white', labelsize=10)
    ax.set_title(title, color='white', fontsize=14, fontweight='bold', pad=15)

    cbar = plt.colorbar(img, ax=ax, format='%+2.0f dB')
    cbar.ax.tick_params(colors='white', labelsize=10)
    cbar.set_label('Amplitude (dB)', color='white', fontsize=11, fontweight='bold')

    ax.grid(True, color='gray', alpha=0.3, linestyle='-', linewidth=0.5)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor='black', edgecolor='none', bbox_inches='tight')
    plt.close()

def find_audio_file(detection_row):
    """Find corresponding audio file for a detection"""
    # Try to construct filename from detection data
    date = detection_row['recording_date']
    time_str = detection_row['recording_start_time'].replace(':', 'h', 1).replace(':', 'm') + 'm'
    species = detection_row['common_name'].replace(' ', '_').replace("'", "")
    start_s = int(detection_row['start_s'])
    conf = int(detection_row['confidence'] * 1000)

    filename = f"{date}_{time_str}_{species}_{start_s}s_conf{conf:04d}.wav"
    audio_path = Path(f"results/audio_clips_enhanced/{filename}")

    if audio_path.exists():
        return audio_path
    return None

# ============================================================================
# 1. FLOCK BEHAVIOR EXAMPLES
# ============================================================================

print("1. Generating Flock Behavior Examples")
print("-"*80)

# Graylag Goose - Extreme flock calling
graylag = detections[detections['common_name'] == 'Graylag Goose']
graylag_sorted = graylag.sort_values('confidence', ascending=False)

# Get highest confidence examples with timestamps close together (flock)
flock_window = graylag[(graylag['absolute_timestamp'] >= '2025-10-13 15:55') &
                       (graylag['absolute_timestamp'] <= '2025-10-13 17:26')]

if len(flock_window) > 0:
    example = flock_window.iloc[0]
    audio_file = find_audio_file(example)

    if audio_file:
        # Copy audio
        dest_audio = AUDIO_DIR / "01_graylag_goose_flock_calling.wav"
        shutil.copy(audio_file, dest_audio)

        # Create spectrogram
        spec_path = SPEC_DIR / "01_graylag_goose_flock_calling.png"
        create_spectrogram(
            audio_file, spec_path,
            "Graylag Goose - Flock Calling (59 events, 98.7% in flocks)"
        )
        print(f"✓ Created: Graylag Goose flock example")
        print(f"  Timestamp: {example['absolute_timestamp']}")
        print(f"  Confidence: {example['confidence']:.1%}")

# Pink-footed Goose - Mixed flock
pinkfoot = detections[detections['common_name'] == 'Pink-footed Goose']
pinkfoot_sorted = pinkfoot.sort_values('confidence', ascending=False)

if len(pinkfoot_sorted) > 0:
    example = pinkfoot_sorted.iloc[0]
    audio_file = find_audio_file(example)

    if audio_file:
        dest_audio = AUDIO_DIR / "02_pinkfooted_goose_flock.wav"
        shutil.copy(audio_file, dest_audio)

        spec_path = SPEC_DIR / "02_pinkfooted_goose_flock.png"
        create_spectrogram(
            audio_file, spec_path,
            "Pink-footed Goose - Flock Calling (18 events, 71% in flocks)"
        )
        print(f"✓ Created: Pink-footed Goose flock example")

print()

# ============================================================================
# 2. CREPUSCULAR BEHAVIOR
# ============================================================================

print("2. Generating Crepuscular Behavior Examples")
print("-"*80)

# Common Grasshopper-Warbler - Dawn chorus (98% dawn activity!)
cgw = detections[detections['common_name'] == 'Common Grasshopper-Warbler']
cgw_dawn = cgw[cgw['hour'] == 8]  # Peak at 08:00

if len(cgw_dawn) > 0:
    example = cgw_dawn.sort_values('confidence', ascending=False).iloc[0]
    audio_file = find_audio_file(example)

    if audio_file:
        dest_audio = AUDIO_DIR / "03_grasshopper_warbler_dawn_chorus.wav"
        shutil.copy(audio_file, dest_audio)

        spec_path = SPEC_DIR / "03_grasshopper_warbler_dawn_chorus.png"
        create_spectrogram(
            audio_file, spec_path,
            "Common Grasshopper-Warbler - Dawn Chorus (98% dawn, 08:00 peak)"
        )
        print(f"✓ Created: Common Grasshopper-Warbler dawn chorus")

# Great Snipe - Dusk lek
great_snipe = detections[detections['common_name'] == 'Great Snipe']
snipe_dusk = great_snipe[(great_snipe['hour'] >= 20) & (great_snipe['hour'] <= 21)]

if len(snipe_dusk) > 0:
    example = snipe_dusk.sort_values('confidence', ascending=False).iloc[0]
    audio_file = find_audio_file(example)

    if audio_file:
        dest_audio = AUDIO_DIR / "04_great_snipe_lek_dusk.wav"
        shutil.copy(audio_file, dest_audio)

        spec_path = SPEC_DIR / "04_great_snipe_lek_dusk.png"
        create_spectrogram(
            audio_file, spec_path,
            "Great Snipe - Dusk Lek Display (20:00-21:00 peak, 61% crepuscular)"
        )
        print(f"✓ Created: Great Snipe lek display")

# Eurasian Woodcock - Dawn roding
woodcock = detections[detections['common_name'] == 'Eurasian Woodcock']
woodcock_dawn = woodcock[(woodcock['hour'] >= 6) & (woodcock['hour'] <= 8)]

if len(woodcock_dawn) > 0:
    example = woodcock_dawn.sort_values('confidence', ascending=False).iloc[0]
    audio_file = find_audio_file(example)

    if audio_file:
        dest_audio = AUDIO_DIR / "05_woodcock_roding_dawn.wav"
        shutil.copy(audio_file, dest_audio)

        spec_path = SPEC_DIR / "05_woodcock_roding_dawn.png"
        create_spectrogram(
            audio_file, spec_path,
            "Eurasian Woodcock - Dawn Roding Flight (75% crepuscular)"
        )
        print(f"✓ Created: Eurasian Woodcock roding")

print()

# ============================================================================
# 3. NOCTURNAL ACTIVITY
# ============================================================================

print("3. Generating Nocturnal Activity Examples")
print("-"*80)

# Tawny Owl - Nocturnal calling
tawny = detections[detections['common_name'] == 'Tawny Owl']
tawny_night = tawny[(tawny['hour'] >= 0) & (tawny['hour'] <= 4)]

if len(tawny_night) > 0:
    example = tawny_night.sort_values('confidence', ascending=False).iloc[0]
    audio_file = find_audio_file(example)

    if audio_file:
        dest_audio = AUDIO_DIR / "06_tawny_owl_nocturnal.wav"
        shutil.copy(audio_file, dest_audio)

        spec_path = SPEC_DIR / "06_tawny_owl_nocturnal.png"
        create_spectrogram(
            audio_file, spec_path,
            "Tawny Owl - Nocturnal Calling (48% night activity)"
        )
        print(f"✓ Created: Tawny Owl nocturnal")

# Mallard - Nocturnal activity
mallard = detections[detections['common_name'] == 'Mallard']
mallard_night = mallard[(mallard['hour'] >= 0) & (mallard['hour'] <= 4)]

if len(mallard_night) > 0:
    example = mallard_night.sort_values('confidence', ascending=False).iloc[0]
    audio_file = find_audio_file(example)

    if audio_file:
        dest_audio = AUDIO_DIR / "07_mallard_nocturnal.wav"
        shutil.copy(audio_file, dest_audio)

        spec_path = SPEC_DIR / "07_mallard_nocturnal.png"
        create_spectrogram(
            audio_file, spec_path,
            "Mallard - Nocturnal Activity (59% night activity)"
        )
        print(f"✓ Created: Mallard nocturnal")

print()

# ============================================================================
# 4. MIGRATION - Nocturnal Flight Calls
# ============================================================================

print("4. Generating Migration Flight Call Examples")
print("-"*80)

# Pink-footed Goose - Nocturnal migration
pinkfoot_night = pinkfoot[(pinkfoot['hour'] >= 2) & (pinkfoot['hour'] <= 4)]

if len(pinkfoot_night) > 0:
    example = pinkfoot_night.sort_values('confidence', ascending=False).iloc[0]
    audio_file = find_audio_file(example)

    if audio_file:
        dest_audio = AUDIO_DIR / "08_pinkfooted_goose_migration_night.wav"
        shutil.copy(audio_file, dest_audio)

        spec_path = SPEC_DIR / "08_pinkfooted_goose_migration_night.png"
        create_spectrogram(
            audio_file, spec_path,
            "Pink-footed Goose - Nocturnal Migration Flight Call (03:00 peak)"
        )
        print(f"✓ Created: Pink-footed Goose migration")

# Common Crane - Migration flight
crane = detections[detections['common_name'] == 'Common Crane']
crane_night = crane[(crane['hour'] >= 3) & (crane['hour'] <= 5)]

if len(crane_night) > 0:
    example = crane_night.sort_values('confidence', ascending=False).iloc[0]
    audio_file = find_audio_file(example)

    if audio_file:
        dest_audio = AUDIO_DIR / "09_common_crane_migration_night.wav"
        shutil.copy(audio_file, dest_audio)

        spec_path = SPEC_DIR / "09_common_crane_migration_night.png"
        create_spectrogram(
            audio_file, spec_path,
            "Common Crane - Nocturnal Migration Flight Call (04:00 peak)"
        )
        print(f"✓ Created: Common Crane migration")

print()

# ============================================================================
# 5. CORVID BEHAVIOR
# ============================================================================

print("5. Generating Corvid Behavior Examples")
print("-"*80)

# Hooded Crow - Flock calling
hooded = detections[detections['common_name'] == 'Hooded Crow']
hooded_sorted = hooded.sort_values('confidence', ascending=False)

if len(hooded_sorted) > 0:
    example = hooded_sorted.iloc[0]
    audio_file = find_audio_file(example)

    if audio_file:
        dest_audio = AUDIO_DIR / "10_hooded_crow_flock.wav"
        shutil.copy(audio_file, dest_audio)

        spec_path = SPEC_DIR / "10_hooded_crow_flock.png"
        create_spectrogram(
            audio_file, spec_path,
            "Hooded Crow - Flock Calling (69% in flocks, sentinel behavior)"
        )
        print(f"✓ Created: Hooded Crow flock")

# Carrion Crow
carrion = detections[detections['common_name'] == 'Carrion Crow']
carrion_sorted = carrion.sort_values('confidence', ascending=False)

if len(carrion_sorted) > 0:
    example = carrion_sorted.iloc[0]
    audio_file = find_audio_file(example)

    if audio_file:
        dest_audio = AUDIO_DIR / "11_carrion_crow_flock.wav"
        shutil.copy(audio_file, dest_audio)

        spec_path = SPEC_DIR / "11_carrion_crow_flock.png"
        create_spectrogram(
            audio_file, spec_path,
            "Carrion Crow - Flock Calling (63% in flocks)"
        )
        print(f"✓ Created: Carrion Crow flock")

print()

# ============================================================================
# 6. RARE/NOTABLE SPECIES
# ============================================================================

print("6. Generating Rare/Notable Species Examples")
print("-"*80)

# Red-breasted Flycatcher (long-distance migrant)
flycatcher = detections[detections['common_name'] == 'Red-breasted Flycatcher']

if len(flycatcher) > 0:
    example = flycatcher.sort_values('confidence', ascending=False).iloc[0]
    audio_file = find_audio_file(example)

    if audio_file:
        dest_audio = AUDIO_DIR / "12_red_breasted_flycatcher.wav"
        shutil.copy(audio_file, dest_audio)

        spec_path = SPEC_DIR / "12_red_breasted_flycatcher.png"
        create_spectrogram(
            audio_file, spec_path,
            "Red-breasted Flycatcher - Long-distance Migrant"
        )
        print(f"✓ Created: Red-breasted Flycatcher")

# Snow Bunting (arctic migrant)
bunting = detections[detections['common_name'] == 'Snow Bunting']

if len(bunting) > 0:
    example = bunting.sort_values('confidence', ascending=False).iloc[0]
    audio_file = find_audio_file(example)

    if audio_file:
        dest_audio = AUDIO_DIR / "13_snow_bunting_arctic.wav"
        shutil.copy(audio_file, dest_audio)

        spec_path = SPEC_DIR / "13_snow_bunting_arctic.png"
        create_spectrogram(
            audio_file, spec_path,
            "Snow Bunting - Arctic Migrant (100% flock calling)"
        )
        print(f"✓ Created: Snow Bunting")

print()

# ============================================================================
# SUMMARY
# ============================================================================

spec_count = len(list(SPEC_DIR.glob("*.png")))
audio_count = len(list(AUDIO_DIR.glob("*.wav")))

print("="*80)
print("EXAMPLE GENERATION COMPLETE")
print("="*80)
print()
print(f"Generated:")
print(f"  • {spec_count} spectrograms in results/behavioral_spectrograms/")
print(f"  • {audio_count} audio examples in results/behavioral_audio_examples/")
print()
print("Categories covered:")
print("  1. Flock Behavior (Graylag, Pink-footed Goose)")
print("  2. Crepuscular Activity (Grasshopper-Warbler, Great Snipe, Woodcock)")
print("  3. Nocturnal Behavior (Tawny Owl, Mallard)")
print("  4. Migration Flight Calls (Pink-footed Goose, Common Crane)")
print("  5. Corvid Flocks (Hooded Crow, Carrion Crow)")
print("  6. Rare Species (Flycatcher, Snow Bunting)")
print()
print("="*80)
