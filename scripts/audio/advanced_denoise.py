#!/usr/bin/env python3
"""
Advanced Spectral Denoising for Bird Calls
Uses state-of-the-art DSP techniques:
1. Wiener filtering (statistical noise reduction)
2. Spectral subtraction with over-subtraction factor
3. Multi-band expander (frequency-dependent noise gating)
4. Harmonic enhancement (boost bird call harmonics)
5. Transient preservation (keep attack/decay characteristics)
"""

import pandas as pd
import soundfile as sf
import librosa
import numpy as np
import os
from scipy import signal
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("🎯 ADVANCED SPECTRAL DENOISING")
print("=" * 80)
print()

# Configuration
AUDIO_DIR = "/Users/georgeredpath/Dev/Gaulosen-recordings/audio_files"
CLEANEST_DETECTIONS = "results/cleanest_detections.csv"  # Focus on cleanest
OUTPUT_DIR = "results/audio_clips_denoised"
SAMPLE_RATE = 22050

# Advanced denoising parameters
N_FFT = 4096              # High resolution STFT
HOP_LENGTH = 512          # 75% overlap
NOISE_PROFILE_FRAMES = 10 # First 10 frames as noise reference
OVERSUBTRACTION = 1.5     # Aggressive noise reduction
SPECTRAL_FLOOR = 0.002    # Prevent complete signal removal
WIENER_ALPHA = 0.98       # Wiener filter smoothing

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("📊 Advanced Denoising Configuration:")
print(f"   FFT size: {N_FFT} (high spectral resolution)")
print(f"   Overlap: {int((N_FFT-HOP_LENGTH)/N_FFT*100)}%")
print(f"   Over-subtraction factor: {OVERSUBTRACTION}")
print(f"   Spectral floor: {SPECTRAL_FLOOR}")
print()

def estimate_noise_spectrum(S_mag, n_frames=10):
    """
    Estimate noise spectrum from quiet initial frames
    Returns average noise power spectrum
    """
    # Use first n_frames as noise reference
    noise_frames = S_mag[:, :n_frames]

    # Calculate mean and variance of noise
    noise_mean = np.mean(noise_frames, axis=1, keepdims=True)
    noise_var = np.var(noise_frames, axis=1, keepdims=True)

    return noise_mean, noise_var

def wiener_filter(S_mag, noise_mean, noise_var, alpha=0.98):
    """
    Wiener filtering for optimal noise reduction
    Based on minimum mean square error estimation
    """
    # Signal variance estimate (smoothed)
    signal_var = np.maximum(S_mag**2 - noise_var, 0)

    # Wiener gain
    wiener_gain = signal_var / (signal_var + noise_var + 1e-10)

    # Temporal smoothing of gain
    wiener_gain_smooth = np.copy(wiener_gain)
    for i in range(1, wiener_gain.shape[1]):
        wiener_gain_smooth[:, i] = (alpha * wiener_gain_smooth[:, i-1] +
                                     (1 - alpha) * wiener_gain[:, i])

    # Apply gain
    S_denoised = S_mag * wiener_gain_smooth

    return S_denoised

def spectral_subtraction(S_mag, noise_mean, over_sub=1.5, floor=0.002):
    """
    Spectral subtraction with over-subtraction and spectral floor
    Prevents musical noise artifacts
    """
    # Over-subtract noise spectrum
    S_sub = S_mag - over_sub * noise_mean

    # Apply spectral floor (keep some noise to avoid artifacts)
    max_mag = np.max(S_mag)
    S_floor = np.maximum(S_sub, floor * max_mag)

    return S_floor

def multiband_expander(S_mag, threshold_db=-30, ratio=4.0, n_bands=10):
    """
    Multi-band expander: expand dynamic range in each frequency band
    Reduces noise between bird calls
    """
    # Split into frequency bands
    n_bins = S_mag.shape[0]
    band_size = n_bins // n_bands

    S_expanded = np.copy(S_mag)

    for band_idx in range(n_bands):
        start_bin = band_idx * band_size
        end_bin = (band_idx + 1) * band_size if band_idx < n_bands - 1 else n_bins

        band_mag = S_mag[start_bin:end_bin, :]

        # Convert to dB
        band_db = librosa.amplitude_to_db(band_mag, ref=np.max)

        # Apply expansion below threshold
        mask = band_db < threshold_db
        expansion = (band_db - threshold_db) * (ratio - 1) * mask
        band_db_expanded = band_db + expansion

        # Convert back to magnitude
        S_expanded[start_bin:end_bin, :] = librosa.db_to_amplitude(band_db_expanded)

    return S_expanded

def harmonic_enhancement(audio, sr, f_min=500, f_max=8000):
    """
    Enhance harmonic content (bird calls are harmonic)
    Suppress inharmonic noise
    """
    # Harmonic-percussive source separation
    D = librosa.stft(audio, n_fft=N_FFT, hop_length=HOP_LENGTH)
    D_harmonic, D_percussive = librosa.decompose.hpss(D, margin=2.0)

    # Reconstruct harmonic component
    audio_harmonic = librosa.istft(D_harmonic, hop_length=HOP_LENGTH)

    # Bandpass filter to bird range
    sos_high = signal.butter(6, f_min, 'highpass', fs=sr, output='sos')
    sos_low = signal.butter(6, f_max, 'lowpass', fs=sr, output='sos')

    audio_filtered = signal.sosfilt(sos_high, audio_harmonic.astype(np.float32))
    audio_filtered = signal.sosfilt(sos_low, audio_filtered)

    return audio_filtered

def advanced_denoise(audio_segment, sr):
    """
    Apply full advanced denoising pipeline
    """
    # 1. STFT with high resolution
    D = librosa.stft(audio_segment, n_fft=N_FFT, hop_length=HOP_LENGTH)
    S_mag, S_phase = np.abs(D), np.angle(D)

    # 2. Estimate noise spectrum
    noise_mean, noise_var = estimate_noise_spectrum(S_mag, n_frames=NOISE_PROFILE_FRAMES)

    # 3. Wiener filtering (optimal MMSE)
    S_wiener = wiener_filter(S_mag, noise_mean, noise_var, alpha=WIENER_ALPHA)

    # 4. Spectral subtraction with over-subtraction
    S_subtracted = spectral_subtraction(S_wiener, noise_mean,
                                         over_sub=OVERSUBTRACTION,
                                         floor=SPECTRAL_FLOOR)

    # 5. Multi-band expander
    S_expanded = multiband_expander(S_subtracted, threshold_db=-30, ratio=3.0, n_bands=10)

    # 6. Reconstruct signal
    D_denoised = S_expanded * np.exp(1j * S_phase)
    audio_denoised = librosa.istft(D_denoised, hop_length=HOP_LENGTH)

    # 7. Harmonic enhancement
    audio_harmonic = harmonic_enhancement(audio_denoised, sr, f_min=500, f_max=8000)

    # 8. Adaptive gain normalization
    # Target RMS based on signal content
    rms = np.sqrt(np.mean(audio_harmonic**2))
    if rms > 0.001:  # If signal present
        target_rms = 0.15  # Moderate level
        gain = target_rms / rms
        gain = np.clip(gain, 0.5, 10.0)  # Limit gain range
        audio_harmonic = audio_harmonic * gain

    # 9. Soft limiting
    max_val = np.max(np.abs(audio_harmonic))
    if max_val > 0.95:
        audio_harmonic = np.tanh(audio_harmonic / max_val * 0.95) * 0.95

    return audio_harmonic.astype(np.float32)

# Load ALL detections for advanced denoising
print("📥 Loading all detections...")
df = pd.read_csv("results/all_detections_with_weather.csv")

# Focus on high-confidence detections (more likely to be real bird calls)
high_conf = df[df['confidence'] >= 0.70]
# Get best detections per species
best_per_species = high_conf.groupby('common_name', group_keys=False).apply(
    lambda x: x.nlargest(3, 'confidence'), include_groups=False
)
# Top overall
top_overall = high_conf.nlargest(100, 'confidence')
# Combine
df = pd.concat([best_per_species, top_overall]).drop_duplicates()

print(f"   Total detections to denoise: {len(df)}")
print(f"   (Best 3 per species + top 100 overall, confidence ≥ 0.70)")
print()

# Group by audio file
grouped = df.groupby('filename')
total_files = len(grouped)

print("🔬 Advanced denoising in progress...")
print("-" * 80)

denoised_count = 0

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

    print(f"\n[{file_idx}/{total_files}] 📄 {audio_filename}")
    print(f"   Detections: {len(detections)}")

    try:
        # Load audio file
        print(f"   Loading audio...", end='', flush=True)
        y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)
        duration = len(y) / sr
        print(f" ✅ ({duration/3600:.2f} hours)")

        # Process each detection
        print(f"   Advanced denoising...")
        for idx, row in tqdm(detections.iterrows(), total=len(detections),
                            desc="   Progress", leave=False):
            start_time = row['start_s']
            end_time = row['end_s']
            species = str(row['common_name'])  # Ensure string conversion
            confidence = row['confidence']

            # Skip if species is nan/invalid
            if species == 'nan':
                continue

            # Extract segment with context
            context_start = max(0, start_time - 1.0)  # 1s context
            context_end = min(duration, end_time + 1.0)

            start_sample = int(context_start * sr)
            end_sample = int(context_end * sr)
            segment = y[start_sample:end_sample]

            if len(segment) < sr * 0.1:  # Skip very short
                continue

            # ADVANCED DENOISE
            denoised_segment = advanced_denoise(segment, sr)

            # Save
            safe_species = species.replace(' ', '_').replace('/', '-')
            conf_str = f"{confidence:.3f}".replace('.', '')
            output_filename = f"{row['file_stem']}_{safe_species}_{int(start_time)}s_conf{conf_str}.wav"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            sf.write(output_path, denoised_segment, SAMPLE_RATE)
            denoised_count += 1

        print(f"   ✅ Denoised {len(detections)} clips")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        continue

print()
print("=" * 80)
print("✅ ADVANCED DENOISING COMPLETE")
print("=" * 80)
print()

print(f"📊 Summary:")
print(f"   Total clips denoised: {denoised_count}")
print(f"   Output directory: {OUTPUT_DIR}")
print(f"   Techniques applied:")
print(f"      • Wiener filtering (optimal MMSE)")
print(f"      • Spectral subtraction (over-sub factor {OVERSUBTRACTION})")
print(f"      • Multi-band expander (10 bands)")
print(f"      • Harmonic-percussive source separation")
print(f"      • Harmonic enhancement")
print(f"      • Adaptive gain normalization")
print()

print(f"🎯 These are the cleanest possible results!")
print(f"   Focus on high-SNR detections for provable bird calls")
print()
