#!/usr/bin/env python3
"""
Call Type Classification
Analyzes acoustic features to classify calls into functional types:
1. Contact calls (short, regular)
2. Alarm calls (rapid, intense)
3. Territorial/Song (long, complex)
4. Flight calls (specific tempo patterns)
5. Distress calls (unusual patterns)
"""

import pandas as pd
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from collections import defaultdict

print("=" * 80)
print("🔊 CALL TYPE CLASSIFICATION")
print("=" * 80)
print()

# Load detections
df = pd.read_csv('results/all_detections_with_weather.csv')
print(f"📊 Analyzing {len(df)} detections")
print()

# We'll analyze the top 3 per species (already enhanced)
top3_df = pd.read_csv('results/top3_per_species.csv')
print(f"Focusing on {len(top3_df)} high-quality examples")
print()

# Load flight call data if available
try:
    flight_df = pd.read_csv('results/flight_calls.csv')
    flight_behaviors = dict(zip(
        zip(flight_df['filename'], flight_df['start_s']),
        flight_df['behavior']
    ))
except:
    flight_behaviors = {}

def extract_acoustic_features(audio_path):
    """Extract features for call type classification"""
    try:
        y, sr = librosa.load(audio_path, sr=None)

        # Duration
        duration = len(y) / sr

        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]

        # Temporal features
        rms = librosa.feature.rms(y=y)[0]
        zcr = librosa.feature.zero_crossing_rate(y)[0]

        # Pitch features
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)

        return {
            'duration': duration,
            'mean_freq': np.mean(spectral_centroids),
            'std_freq': np.std(spectral_centroids),
            'mean_bandwidth': np.mean(spectral_bandwidth),
            'mean_rolloff': np.mean(spectral_rolloff),
            'mean_rms': np.mean(rms),
            'std_rms': np.std(rms),
            'rms_variability': np.std(rms) / (np.mean(rms) + 1e-6),
            'mean_zcr': np.mean(zcr),
            'pitch_range': np.max(pitch_values) - np.min(pitch_values) if pitch_values else 0,
            'pitch_mean': np.mean(pitch_values) if pitch_values else 0
        }
    except Exception as e:
        return None

# Extract features for top 3 per species
print("Extracting acoustic features...")
print()

features_list = []
audio_dir = Path('results/audio_clips_enhanced')

for idx, row in top3_df.iterrows():
    filename_stem = Path(row['filename']).stem
    start_s = row['start_s']

    # Find matching audio file
    pattern = f"{filename_stem}_{int(start_s)}_*.wav"
    matching_files = list(audio_dir.glob(pattern))

    if not matching_files:
        continue

    audio_path = matching_files[0]
    features = extract_acoustic_features(audio_path)

    if features:
        features['species'] = row['common_name']
        features['filename'] = row['filename']
        features['start_s'] = start_s
        features['confidence'] = row['confidence']

        # Check if it's a known flight call
        key = (row['filename'], start_s)
        if key in flight_behaviors:
            features['known_type'] = flight_behaviors[key]
        else:
            features['known_type'] = 'unknown'

        features_list.append(features)

features_df = pd.DataFrame(features_list)
print(f"✅ Extracted features from {len(features_df)} calls")
print()

# ============================================================================
# CLASSIFY CALL TYPES BASED ON ACOUSTIC FEATURES
# ============================================================================

print("=" * 80)
print("CALL TYPE CLASSIFICATION")
print("=" * 80)
print()

def classify_call_type(row):
    """Rule-based classification of call types"""

    # Already classified flight calls
    if row['known_type'] != 'unknown':
        return row['known_type']

    duration = row['duration']
    rms_var = row['rms_variability']
    freq_std = row['std_freq']
    bandwidth = row['mean_bandwidth']

    # ALARM CALL: Short, intense, variable
    if duration < 0.5 and rms_var > 0.4 and freq_std > 500:
        return 'alarm'

    # CONTACT CALL: Short, simple, consistent
    elif duration < 1.0 and rms_var < 0.3 and bandwidth < 2000:
        return 'contact'

    # TERRITORIAL/SONG: Long, complex, variable frequency
    elif duration > 2.0 and freq_std > 400:
        return 'territorial'

    # QUIET/FEEDING: Soft, short
    elif row['mean_rms'] < 0.05 and duration < 0.8:
        return 'feeding'

    # DEFAULT: Generic call
    else:
        return 'generic'

features_df['call_type'] = features_df.apply(classify_call_type, axis=1)

# ============================================================================
# SUMMARIZE BY SPECIES AND CALL TYPE
# ============================================================================

print("Call Type Distribution:")
print("-" * 80)
call_type_counts = features_df['call_type'].value_counts()
for call_type, count in call_type_counts.items():
    pct = count / len(features_df) * 100
    print(f"  {call_type.capitalize():20s} | {count:3d} calls ({pct:5.1f}%)")
print()

print("=" * 80)
print("CALL TYPE REPERTOIRE BY SPECIES")
print("=" * 80)
print()

# Species with multiple call types
species_call_types = features_df.groupby('species')['call_type'].apply(
    lambda x: sorted(set(x))
).reset_index()

# Filter species with multiple call types
multi_type_species = species_call_types[
    species_call_types['call_type'].apply(len) > 1
].copy()

if len(multi_type_species) > 0:
    print(f"✅ Found {len(multi_type_species)} species with multiple call types")
    print()

    for idx, row in multi_type_species.iterrows():
        species = row['species']
        call_types = row['call_type']

        species_data = features_df[features_df['species'] == species]
        type_counts = species_data['call_type'].value_counts()

        print(f"{species}:")
        print(f"  Call types: {', '.join(call_types)}")
        for call_type in call_types:
            count = type_counts[call_type]
            examples = species_data[species_data['call_type'] == call_type].head(1)
            if len(examples) > 0:
                ex = examples.iloc[0]
                print(f"    • {call_type.capitalize()}: {count} calls "
                      f"(dur: {ex['duration']:.2f}s, freq: {ex['mean_freq']:.0f}Hz)")
        print()

# ============================================================================
# ACOUSTIC FEATURE PROFILES
# ============================================================================

print("=" * 80)
print("ACOUSTIC FEATURE PROFILES BY CALL TYPE")
print("=" * 80)
print()

for call_type in ['contact', 'alarm', 'territorial', 'in_flight_contact', 'landing']:
    type_data = features_df[features_df['call_type'] == call_type]

    if len(type_data) == 0:
        continue

    print(f"{call_type.upper().replace('_', ' ')} CALLS ({len(type_data)} examples):")
    print("-" * 80)
    print(f"  Duration:        {type_data['duration'].mean():.2f} ± {type_data['duration'].std():.2f} s")
    print(f"  Frequency:       {type_data['mean_freq'].mean():.0f} ± {type_data['std_freq'].mean():.0f} Hz")
    print(f"  Bandwidth:       {type_data['mean_bandwidth'].mean():.0f} Hz")
    print(f"  Amplitude var:   {type_data['rms_variability'].mean():.3f}")

    # Top species for this call type
    top_species = type_data['species'].value_counts().head(3)
    print(f"  Top species:     {', '.join(top_species.index.tolist())}")
    print()

# ============================================================================
# SAVE RESULTS
# ============================================================================

print("=" * 80)
print("💾 SAVING RESULTS")
print("=" * 80)
print()

features_df.to_csv('results/call_type_classification.csv', index=False)
print("✅ Saved classification: results/call_type_classification.csv")

# Species repertoire summary
species_repertoire = features_df.groupby('species').agg({
    'call_type': lambda x: len(set(x)),
    'duration': ['mean', 'std'],
    'mean_freq': ['mean', 'std']
}).reset_index()
species_repertoire.columns = ['species', 'num_call_types', 'mean_duration',
                               'std_duration', 'mean_frequency', 'std_frequency']
species_repertoire = species_repertoire.sort_values('num_call_types', ascending=False)
species_repertoire.to_csv('results/species_vocal_repertoire.csv', index=False)
print("✅ Saved repertoire: results/species_vocal_repertoire.csv")

print()
print("=" * 80)
print("✅ CALL TYPE CLASSIFICATION COMPLETE")
print("=" * 80)
print()
