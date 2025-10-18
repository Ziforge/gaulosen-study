#!/usr/bin/env python3
"""
Analyze background noise levels in bird call detections
Identify the cleanest recordings with highest signal-to-noise ratio
"""

import pandas as pd
import soundfile as sf
import librosa
import numpy as np
import os
from scipy import signal
from tqdm import tqdm

print("=" * 80)
print("🔍 NOISE LEVEL ANALYSIS")
print("=" * 80)
print()

# Configuration
AUDIO_DIR = "/Users/georgeredpath/Dev/Gaulossen-recordings/audio_files"
ALL_DETECTIONS = "results/all_detections_with_weather.csv"
SAMPLE_RATE = 22050

def estimate_snr(audio_segment, sr):
    """
    Estimate Signal-to-Noise Ratio for a bird call segment
    Higher SNR = cleaner recording
    """
    # Bandpass filter to bird frequency range
    sos_high = signal.butter(4, 500, 'highpass', fs=sr, output='sos')
    sos_low = signal.butter(4, 10000, 'lowpass', fs=sr, output='sos')

    filtered = signal.sosfilt(sos_high, audio_segment.astype(np.float32))
    filtered = signal.sosfilt(sos_low, filtered)

    # Calculate short-time energy
    frame_length = int(0.02 * sr)  # 20ms frames
    hop_length = int(0.01 * sr)    # 10ms hop

    frames = librosa.util.frame(filtered, frame_length=frame_length, hop_length=hop_length)
    energy = np.sum(frames**2, axis=0)

    # Signal energy: top 30% of frames (bird call)
    signal_threshold = np.percentile(energy, 70)
    signal_energy = np.mean(energy[energy >= signal_threshold])

    # Noise energy: bottom 30% of frames (background)
    noise_threshold = np.percentile(energy, 30)
    noise_energy = np.mean(energy[energy <= noise_threshold])

    # SNR in dB
    if noise_energy > 0:
        snr_db = 10 * np.log10(signal_energy / noise_energy)
    else:
        snr_db = 100  # Perfect signal

    return snr_db

def calculate_spectral_flatness(audio_segment, sr):
    """
    Calculate spectral flatness (tonality measure)
    Lower values = more tonal (bird calls)
    Higher values = more noise-like
    """
    # STFT
    D = librosa.stft(audio_segment, n_fft=2048, hop_length=512)
    mag = np.abs(D)

    # Spectral flatness
    flatness = librosa.feature.spectral_flatness(S=mag)

    # Lower flatness = more tonal = cleaner bird call
    return np.mean(flatness)

# Load detections
print("📥 Loading detections...")
df = pd.read_csv(ALL_DETECTIONS)

# Focus on high-confidence detections (more likely to be clean)
high_conf = df[df['confidence'] >= 0.70]
print(f"   High-confidence detections (≥0.70): {len(high_conf)}")
print()

# Sample subset for analysis (analyze top 500 detections)
sample_size = min(500, len(high_conf))
sample_df = high_conf.nlargest(sample_size, 'confidence')

print(f"🔬 Analyzing noise levels for {sample_size} detections...")
print("-" * 80)

snr_results = []

# Group by audio file to minimize file loading
grouped = sample_df.groupby('filename')

for file_idx, (audio_filename, detections) in enumerate(grouped, 1):
    # Find audio file
    audio_path = None
    for date_dir in os.listdir(AUDIO_DIR):
        potential_path = os.path.join(AUDIO_DIR, date_dir, audio_filename)
        if os.path.exists(potential_path):
            audio_path = potential_path
            break

    if not audio_path:
        continue

    print(f"\n[{file_idx}/{len(grouped)}] 📄 {audio_filename}")

    try:
        # Load audio file
        y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)
        duration = len(y) / sr

        # Analyze each detection
        for idx, row in tqdm(detections.iterrows(), total=len(detections),
                            desc="   Analyzing", leave=False):
            start_time = row['start_s']
            end_time = row['end_s']

            # Extract segment
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            segment = y[start_sample:end_sample]

            if len(segment) < sr * 0.1:  # Skip very short segments
                continue

            # Calculate noise metrics
            snr = estimate_snr(segment, sr)
            flatness = calculate_spectral_flatness(segment, sr)

            snr_results.append({
                'filename': audio_filename,
                'file_stem': row['file_stem'],
                'species': row['common_name'],
                'confidence': row['confidence'],
                'start_s': start_time,
                'end_s': end_time,
                'snr_db': snr,
                'spectral_flatness': flatness,
                'duration_s': end_time - start_time,
                'weather': row['weather_summary'],
                'absolute_timestamp': row['absolute_timestamp']
            })

        print(f"   ✅ Analyzed {len(detections)} detections")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        continue

print()
print("=" * 80)
print("📊 ANALYSIS RESULTS")
print("=" * 80)
print()

# Convert to DataFrame
results_df = pd.DataFrame(snr_results)

if len(results_df) > 0:
    # Save full results
    results_df.to_csv('results/noise_analysis.csv', index=False)
    print(f"✅ Saved noise analysis: results/noise_analysis.csv")
    print()

    # Statistics
    print("📈 Overall Statistics:")
    print(f"   Mean SNR: {results_df['snr_db'].mean():.1f} dB")
    print(f"   Median SNR: {results_df['snr_db'].median():.1f} dB")
    print(f"   Std Dev: {results_df['snr_db'].std():.1f} dB")
    print()

    # Categorize by SNR
    excellent = results_df[results_df['snr_db'] >= 20]
    good = results_df[(results_df['snr_db'] >= 15) & (results_df['snr_db'] < 20)]
    fair = results_df[(results_df['snr_db'] >= 10) & (results_df['snr_db'] < 15)]
    poor = results_df[results_df['snr_db'] < 10]

    print("🎯 Quality Categories:")
    print(f"   Excellent (SNR ≥ 20 dB): {len(excellent)} detections ({len(excellent)/len(results_df)*100:.1f}%)")
    print(f"   Good (SNR 15-20 dB): {len(good)} detections ({len(good)/len(results_df)*100:.1f}%)")
    print(f"   Fair (SNR 10-15 dB): {len(fair)} detections ({len(fair)/len(results_df)*100:.1f}%)")
    print(f"   Poor (SNR < 10 dB): {len(poor)} detections ({len(poor)/len(results_df)*100:.1f}%)")
    print()

    # Top cleanest recordings
    print("🏆 Top 20 Cleanest Recordings:")
    print("-" * 80)
    cleanest = results_df.nlargest(20, 'snr_db')
    for idx, row in cleanest.iterrows():
        print(f"   {row['species']:30s} | SNR: {row['snr_db']:5.1f} dB | "
              f"Conf: {row['confidence']:.3f} | {row['weather']}")
    print()

    # Save cleanest recordings list
    cleanest_full = results_df[results_df['snr_db'] >= 15]  # Good or excellent
    cleanest_full.to_csv('results/cleanest_detections.csv', index=False)
    print(f"✅ Saved {len(cleanest_full)} clean detections to: results/cleanest_detections.csv")
    print()

    # Species with cleanest recordings
    print("🐦 Species with Best Average SNR:")
    species_snr = results_df.groupby('species')['snr_db'].agg(['mean', 'count'])
    species_snr = species_snr[species_snr['count'] >= 3]  # At least 3 detections
    species_snr = species_snr.sort_values('mean', ascending=False).head(10)
    for species, row in species_snr.iterrows():
        print(f"   {species:30s} | Avg SNR: {row['mean']:5.1f} dB | Count: {int(row['count'])}")
    print()

else:
    print("❌ No results to analyze")

print("=" * 80)
print("✅ ANALYSIS COMPLETE")
print("=" * 80)
print()
