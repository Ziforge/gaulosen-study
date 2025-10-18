#!/usr/bin/env python3
"""
Acoustic Fingerprinting / Individual Recognition
Uses MFCC and spectral features to cluster calls and identify potential individuals
"""

import pandas as pd
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("🎵 ACOUSTIC FINGERPRINTING & INDIVIDUAL RECOGNITION")
print("=" * 80)
print()

# Load top 3 per species
top3_df = pd.read_csv('results/top3_per_species.csv')
print(f"📊 Analyzing {len(top3_df)} high-quality examples")
print()

# Focus on species with multiple examples
species_col = 'species' if 'species' in top3_df.columns else 'common_name'
species_counts = top3_df[species_col].value_counts()
multi_example_species = species_counts[species_counts >= 3].index.tolist()

print(f"Focusing on {len(multi_example_species)} species with ≥3 examples")
print()

def extract_mfcc_fingerprint(audio_path, n_mfcc=13):
    """Extract MFCC fingerprint for individual recognition"""
    try:
        y, sr = librosa.load(audio_path, sr=None)

        # MFCCs (mel-frequency cepstral coefficients) - voice characteristics
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)

        # Statistics of MFCCs over time
        mfcc_mean = np.mean(mfccs, axis=1)
        mfcc_std = np.std(mfccs, axis=1)
        mfcc_delta = np.mean(librosa.feature.delta(mfccs), axis=1)

        # Spectral features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
        spectral_contrast = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr), axis=1)

        # Combine into fingerprint vector
        fingerprint = np.concatenate([
            mfcc_mean,
            mfcc_std,
            mfcc_delta,
            [spectral_centroid, spectral_bandwidth],
            spectral_contrast
        ])

        return fingerprint

    except Exception as e:
        return None

# ============================================================================
# EXTRACT FINGERPRINTS FOR EACH SPECIES
# ============================================================================

print("Extracting acoustic fingerprints...")
print()

audio_dir = Path('results/audio_clips_enhanced')
species_fingerprints = {}

for species in multi_example_species[:15]:  # Top 15 species
    species_df = top3_df[top3_df[species_col] == species]

    fingerprints = []
    metadata = []

    for idx, row in species_df.iterrows():
        filename_stem = Path(row['filename']).stem
        start_s = row['start_s']
        species_name = row[species_col].replace(' ', '_').replace('/', '-')

        # Files are named: {filestem}_{species}_{start}s_conf{conf}.wav
        pattern = f"{filename_stem}_{species_name}_{int(start_s)}s_*.wav"
        matching_files = list(audio_dir.glob(pattern))

        if not matching_files:
            continue

        audio_path = matching_files[0]
        fingerprint = extract_mfcc_fingerprint(audio_path)

        if fingerprint is not None:
            fingerprints.append(fingerprint)
            metadata.append({
                'species': species,
                'filename': row['filename'],
                'start_s': start_s,
                'confidence': row['confidence']
            })

    if len(fingerprints) >= 3:
        species_fingerprints[species] = {
            'fingerprints': np.array(fingerprints),
            'metadata': metadata
        }

print(f"✅ Extracted fingerprints for {len(species_fingerprints)} species")
print()

# ============================================================================
# CLUSTER FINGERPRINTS TO IDENTIFY INDIVIDUALS
# ============================================================================

print("=" * 80)
print("INDIVIDUAL CLUSTERING")
print("=" * 80)
print()

individual_results = []

for species, data in species_fingerprints.items():
    fingerprints = data['fingerprints']
    metadata = data['metadata']

    if len(fingerprints) < 3:
        continue

    # Normalize features
    scaler = StandardScaler()
    fingerprints_scaled = scaler.fit_transform(fingerprints)

    # DBSCAN clustering (density-based, no need to specify k)
    clustering = DBSCAN(eps=2.0, min_samples=1).fit(fingerprints_scaled)
    labels = clustering.labels_

    n_individuals = len(set(labels)) - (1 if -1 in labels else 0)

    # Only report if multiple individuals detected
    if n_individuals > 1:
        individual_results.append({
            'species': species,
            'n_calls': len(fingerprints),
            'n_individuals': n_individuals,
            'labels': labels.tolist(),
            'metadata': metadata
        })

        # Calculate within-cluster and between-cluster distances
        from scipy.spatial.distance import pdist, squareform
        dist_matrix = squareform(pdist(fingerprints_scaled))

        within_cluster_dists = []
        between_cluster_dists = []

        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                if labels[i] == labels[j] and labels[i] != -1:
                    within_cluster_dists.append(dist_matrix[i, j])
                elif labels[i] != labels[j] and labels[i] != -1 and labels[j] != -1:
                    between_cluster_dists.append(dist_matrix[i, j])

        separation_score = (np.mean(between_cluster_dists) / (np.mean(within_cluster_dists) + 0.1)
                           if within_cluster_dists and between_cluster_dists else 0)

        print(f"{species}:")
        print(f"  Calls analyzed:      {len(fingerprints)}")
        print(f"  Individuals detected: {n_individuals}")
        print(f"  Separation score:    {separation_score:.2f}")

        # Show cluster assignments
        for cluster_id in set(labels):
            if cluster_id == -1:
                continue
            cluster_calls = [i for i, l in enumerate(labels) if l == cluster_id]
            print(f"  Individual {cluster_id + 1}:        {len(cluster_calls)} calls")

        print()

# ============================================================================
# VOICE SIMILARITY MATRIX
# ============================================================================

print("=" * 80)
print("VOICE SIMILARITY ANALYSIS")
print("=" * 80)
print()

for result in individual_results[:5]:  # Top 5 species
    species = result['species']
    data = species_fingerprints[species]
    fingerprints = data['fingerprints']
    labels = np.array(result['labels'])

    print(f"{species} - Pairwise Voice Similarity:")
    print("-" * 80)

    # Calculate cosine similarity
    from sklearn.metrics.pairwise import cosine_similarity
    similarity_matrix = cosine_similarity(fingerprints)

    # Show most similar and most different pairs
    n = len(fingerprints)
    similarities = []
    for i in range(n):
        for j in range(i + 1, n):
            similarities.append((i, j, similarity_matrix[i, j], labels[i], labels[j]))

    similarities.sort(key=lambda x: x[2], reverse=True)

    print("  Most similar calls (likely same individual):")
    for i, j, sim, label_i, label_j in similarities[:3]:
        same_cluster = "✓" if label_i == label_j else "✗"
        print(f"    Call {i+1} ↔ Call {j+1}: {sim:.3f} {same_cluster}")

    print()
    print("  Most different calls (likely different individuals):")
    for i, j, sim, label_i, label_j in similarities[-3:]:
        same_cluster = "✓" if label_i == label_j else "✗"
        print(f"    Call {i+1} ↔ Call {j+1}: {sim:.3f} {same_cluster}")

    print()

# ============================================================================
# SAVE RESULTS
# ============================================================================

print("=" * 80)
print("💾 SAVING RESULTS")
print("=" * 80)
print()

if individual_results:
    # Flatten results for CSV
    rows = []
    for result in individual_results:
        for i, meta in enumerate(result['metadata']):
            rows.append({
                'species': result['species'],
                'filename': meta['filename'],
                'start_s': meta['start_s'],
                'confidence': meta['confidence'],
                'individual_id': result['labels'][i] + 1,
                'total_individuals': result['n_individuals']
            })

    results_df = pd.DataFrame(rows)
    results_df.to_csv('results/individual_recognition.csv', index=False)
    print("✅ Saved individual assignments: results/individual_recognition.csv")

    # Summary by species
    summary_df = pd.DataFrame([
        {
            'species': r['species'],
            'n_calls': r['n_calls'],
            'n_individuals': r['n_individuals']
        }
        for r in individual_results
    ])
    summary_df.to_csv('results/individual_recognition_summary.csv', index=False)
    print("✅ Saved summary: results/individual_recognition_summary.csv")
else:
    print("❌ No clear individual patterns detected")

print()
print("=" * 80)
print("✅ ACOUSTIC FINGERPRINTING COMPLETE")
print("=" * 80)
print()
