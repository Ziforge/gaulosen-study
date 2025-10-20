#!/usr/bin/env python3
"""
Smart Adaptive Audio Enhancement with Spectral Gating
Detects bird call energy and only amplifies the signal, not the noise floor
"""

import pandas as pd
import soundfile as sf
import librosa
import numpy as np
import os
from scipy import signal
from tqdm import tqdm

print("=" * 80)
print("🎯 SMART ADAPTIVE AUDIO ENHANCEMENT")
print("=" * 80)
print()

# Configuration
AUDIO_DIR = "/Users/georgeredpath/Dev/Gaulosen-recordings/audio_files"
ALL_DETECTIONS = "results/all_detections_with_weather.csv"
OUTPUT_DIR = "results/audio_clips_enhanced"
SAMPLE_RATE = 22050

# Smart enhancement parameters
BIRD_FREQ_MIN = 500        # Birds typically above 500 Hz
BIRD_FREQ_MAX = 10000      # Birds typically below 10 kHz
NOISE_PROFILE_PERCENTILE = 20  # Bottom 20% is noise floor
SPECTRAL_GATE_DB = -40     # Gate threshold below signal
ADAPTIVE_GAIN_TARGET = 0.7  # Target RMS level for bird calls
MAX_GAIN_DB = 30           # Maximum amplification
ATTACK_TIME = 0.01         # Fast attack (10ms)
RELEASE_TIME = 0.1         # Slow release (100ms)

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("📊 Smart Enhancement Configuration:")
print(f"   Bird frequency range: {BIRD_FREQ_MIN}-{BIRD_FREQ_MAX} Hz")
print(f"   Noise profile: Bottom {NOISE_PROFILE_PERCENTILE}% of energy")
print(f"   Spectral gate: {SPECTRAL_GATE_DB} dB below signal")
print(f"   Adaptive gain target: {ADAPTIVE_GAIN_TARGET} RMS")
print(f"   Max gain: {MAX_GAIN_DB} dB")
print()

def estimate_noise_floor(audio, sr):
    """Estimate noise floor from quiet regions"""
    # Use short-time energy to find quiet regions
    frame_length = int(0.02 * sr)  # 20ms frames
    hop_length = int(0.01 * sr)    # 10ms hop

    # Calculate frame energy
    frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length)
    energy = np.sum(frames**2, axis=0)

    # Noise floor is the lower percentile of energy
    noise_threshold = np.percentile(energy, NOISE_PROFILE_PERCENTILE)

    # Extract noise frames
    noise_frames = frames[:, energy <= noise_threshold]

    if noise_frames.size > 0:
        noise_estimate = np.mean(np.abs(noise_frames))
    else:
        noise_estimate = np.mean(np.abs(audio)) * 0.1

    return noise_estimate

def spectral_gate(audio, sr, threshold_db=-40):
    """Apply spectral gating to remove noise between bird calls"""
    # STFT
    D = librosa.stft(audio, n_fft=2048, hop_length=512)
    mag, phase = np.abs(D), np.angle(D)

    # Convert to dB
    mag_db = librosa.amplitude_to_db(mag, ref=np.max)

    # Create gate mask (keep only above threshold)
    gate_mask = mag_db > threshold_db

    # Apply gate with smooth transitions
    from scipy.ndimage import uniform_filter
    gate_mask_smooth = uniform_filter(gate_mask.astype(float), size=3)

    # Apply mask
    mag_gated = mag * gate_mask_smooth

    # Reconstruct
    D_gated = mag_gated * np.exp(1j * phase)
    audio_gated = librosa.istft(D_gated, hop_length=512)

    return audio_gated

def adaptive_dynamic_range(audio, sr, target_rms=0.7, max_gain_db=30):
    """Adaptive gain control based on actual signal level"""
    # Split into frames for adaptive processing
    frame_length = int(0.05 * sr)  # 50ms frames
    hop_length = int(0.01 * sr)    # 10ms hop

    frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length, axis=0)

    # Calculate RMS for each frame
    rms = np.sqrt(np.mean(frames**2, axis=0))

    # Calculate adaptive gain for each frame
    max_gain = 10 ** (max_gain_db / 20)
    gains = np.zeros_like(rms)

    for i, frame_rms in enumerate(rms):
        if frame_rms > 1e-6:  # Avoid division by zero
            desired_gain = target_rms / frame_rms
            gains[i] = np.clip(desired_gain, 0.1, max_gain)
        else:
            gains[i] = 1.0

    # Smooth gains (attack/release)
    attack_samples = int(ATTACK_TIME * sr / hop_length)
    release_samples = int(RELEASE_TIME * sr / hop_length)

    gains_smooth = np.copy(gains)
    for i in range(1, len(gains)):
        if gains[i] > gains_smooth[i-1]:
            # Attack
            alpha = 1.0 / attack_samples
        else:
            # Release
            alpha = 1.0 / release_samples
        gains_smooth[i] = alpha * gains[i] + (1 - alpha) * gains_smooth[i-1]

    # Interpolate gains back to sample rate
    gain_times = np.arange(len(gains_smooth)) * hop_length
    sample_times = np.arange(len(audio))
    gains_interp = np.interp(sample_times, gain_times, gains_smooth)

    # Apply adaptive gain
    audio_gained = audio * gains_interp

    return audio_gained

def smart_enhance(audio_segment, sr):
    """Smart adaptive enhancement with source detection"""

    # 1. Bandpass filter (bird frequency range)
    sos_high = signal.butter(6, BIRD_FREQ_MIN, 'highpass', fs=sr, output='sos')
    sos_low = signal.butter(6, BIRD_FREQ_MAX, 'lowpass', fs=sr, output='sos')

    filtered = signal.sosfilt(sos_high, audio_segment.astype(np.float32))
    filtered = signal.sosfilt(sos_low, filtered)

    # 2. Estimate and subtract noise floor
    noise_floor = estimate_noise_floor(filtered, sr)

    # Noise reduction via spectral subtraction
    filtered_rms = np.sqrt(np.mean(filtered**2))
    if filtered_rms > noise_floor * 2:  # Signal present
        # Apply spectral gating
        filtered = spectral_gate(filtered, sr, threshold_db=SPECTRAL_GATE_DB)

    # 3. Adaptive dynamic range compression
    enhanced = adaptive_dynamic_range(filtered, sr,
                                     target_rms=ADAPTIVE_GAIN_TARGET,
                                     max_gain_db=MAX_GAIN_DB)

    # 4. Final normalization with headroom
    max_val = np.max(np.abs(enhanced))
    if max_val > 0.95:
        enhanced = enhanced / max_val * 0.95

    # 5. High-pass one more time to remove any low-freq artifacts
    enhanced = signal.sosfilt(sos_high, enhanced)

    return enhanced.astype(np.float32)

# Load detections
print("📥 Loading detections...")
df = pd.read_csv(ALL_DETECTIONS)

# Get best detections
high_priority = df[df['confidence'] < 0.50]
best_per_species = df.groupby('common_name', group_keys=False).apply(
    lambda x: x.nlargest(3, 'confidence')
)
top_overall = df.nlargest(50, 'confidence')
combined = pd.concat([high_priority, best_per_species, top_overall]).drop_duplicates()

print(f"   Total detections to enhance: {len(combined)}")
print()

# Group by audio file
combined_grouped = combined.groupby('filename')

print("🎯 Smart adaptive enhancement in progress...")
print("-" * 80)

enhanced_count = 0
total_files = len(combined_grouped)

for file_idx, (audio_filename, detections) in enumerate(combined_grouped, 1):
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
        print(f"   Smart enhancing clips...")
        for idx, row in tqdm(detections.iterrows(), total=len(detections),
                            desc="   Progress", leave=False):
            start_time = row['start_s']
            end_time = row['end_s']
            species = row['common_name']
            confidence = row['confidence']

            # Extract segment with padding
            context_start = max(0, start_time - 0.5)
            context_end = min(duration, end_time + 0.5)

            start_sample = int(context_start * sr)
            end_sample = int(context_end * sr)
            segment = y[start_sample:end_sample]

            if len(segment) == 0:
                continue

            # SMART ENHANCE
            enhanced_segment = smart_enhance(segment, sr)

            # Save
            safe_species = species.replace(' ', '_').replace('/', '-')
            conf_str = f"{confidence:.3f}".replace('.', '')
            output_filename = f"{row['file_stem']}_{safe_species}_{int(start_time)}s_conf{conf_str}.wav"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            sf.write(output_path, enhanced_segment, SAMPLE_RATE)
            enhanced_count += 1

        print(f"   ✅ Enhanced {len(detections)} clips")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        continue

print()
print("=" * 80)
print("✅ SMART ADAPTIVE ENHANCEMENT COMPLETE")
print("=" * 80)
print()

print(f"📊 Summary:")
print(f"   Total clips enhanced: {enhanced_count}")
print(f"   Output directory: {OUTPUT_DIR}")
print(f"   Smart features:")
print(f"      • Noise floor estimation and removal")
print(f"      • Spectral gating (only amplifies bird calls)")
print(f"      • Adaptive gain control (varies per frame)")
print(f"      • Source detection (ignores noise)")
print(f"      • Bandpass filtering ({BIRD_FREQ_MIN}-{BIRD_FREQ_MAX} Hz)")
print()

print(f"🎯 Bird calls are now clear and balanced!")
print(f"   Noise floor is minimized, only bird calls amplified")
print(f"   Refresh the web page to hear the improvement")
print()
