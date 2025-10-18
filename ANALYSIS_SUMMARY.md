# Gaulossen Nature Reserve Bird Call Analysis
## October 13-15, 2025

---

## Recording Details

**Location:** Gaulossen Nature Reserve, Norway
**Duration:** 48.8 hours across 4 recordings
**Sample Rate:** 48 kHz (original), 22.05 kHz (analysis)
**Total Size:** 15.5 GB

### Recording Files:
1. `245AAA0563ED3DA7_20251013_113753.WAV` - 12.37 hours
2. `245AAA0563ED3DA7_20251014_000000.WAV` - 12.42 hours
3. `245AAA0563ED3DA7_20251014_122526.WAV` - 11.58 hours
4. `245AAA0563ED3DA7_20251015_000000.WAV` - 12.42 hours

---

## BirdNET AI Analysis Results

**Total Detections:** 6,805
**Unique Species:** 90
**High-Confidence Detections (≥0.70):** 1,175 (17.3%)

### Top Species Detected:
| Species | Detections | Avg Confidence |
|---------|-----------|----------------|
| Spotted Crake | 2,834 | 0.42 |
| Common Cuckoo | 551 | 0.64 |
| Graylag Goose | 478 | 0.78 |
| Great Bittern | 378 | 0.35 |
| Pink-footed Goose | 285 | 0.67 |

---

## Signal-to-Noise Ratio Analysis

### Overall Statistics (500 high-confidence detections analyzed):
- **Mean SNR:** 4.4 dB
- **Median SNR:** 3.1 dB
- **Standard Deviation:** 3.4 dB

### Quality Distribution:
- **Excellent (SNR ≥ 20 dB):** 3 detections (0.6%)
- **Good (SNR 15-20 dB):** 3 detections (0.6%)
- **Fair (SNR 10-15 dB):** 32 detections (6.4%)
- **Poor (SNR < 10 dB):** 462 detections (92.4%)

### Key Finding:
**92.4% of recordings have poor SNR (<10 dB)** due to heavy background noise from:
- Wind
- Rain
- Equipment noise
- Environmental interference

---

## Top 6 Cleanest Recordings

### 1. Yellowhammer
- **SNR:** 21.8 dB
- **Confidence:** 83.2%
- **Weather:** Light rain overnight
- **Status:** ✅ Advanced denoising applied

### 2. Graylag Goose
- **SNR:** 21.2 dB
- **Confidence:** 86.9%
- **Weather:** Partly cloudy, unsettled
- **Status:** ✅ Advanced denoising applied

### 3. Graylag Goose
- **SNR:** 20.7 dB
- **Confidence:** 84.9%
- **Weather:** Partly cloudy, unsettled
- **Status:** ✅ Advanced denoising applied

### 4-6. Additional Graylag Goose
- **SNR Range:** 16.4 - 17.9 dB
- **Confidence Range:** 92.3% - 98.3%
- **Status:** ✅ Advanced denoising applied

---

## Audio Enhancement Pipeline

### Phase 1: Smart Adaptive Enhancement (All 4,260 clips)
**Techniques Applied:**
- Noise floor estimation (bottom 20th percentile)
- Spectral gating (-40 dB threshold)
- Adaptive gain control (50ms frames, 10ms hop)
- Source detection (only enhance when signal > noise × 2)
- Bandpass filtering (500-10,000 Hz)
- Attack/release envelope (10ms attack, 100ms release)

**Output:** `results/audio_clips_enhanced/`

### Phase 2: Advanced Spectral Denoising (160 best clips)
**Selection Criteria:**
- Best 3 per species (confidence ≥ 0.70)
- Top 100 overall by confidence

**Techniques Applied:**
1. **Wiener Filtering** - Optimal MMSE noise reduction
2. **Spectral Subtraction** - Over-subtraction factor 1.5
3. **Multi-Band Expander** - 10 frequency bands, 3:1 ratio
4. **Harmonic-Percussive Source Separation** - Isolate tonal components
5. **Harmonic Enhancement** - Boost bird call harmonics (500-8000 Hz)
6. **Adaptive Gain Normalization** - Target RMS 0.15
7. **Soft Limiting** - Prevent clipping via tanh

**DSP Parameters:**
- FFT Size: 4096 (high spectral resolution)
- Overlap: 87% (75% overlap STFT)
- Noise Profile: First 10 frames
- Spectral Floor: 0.002 (prevent musical noise)
- Wiener Alpha: 0.98 (temporal smoothing)

**Output:** `results/audio_clips_denoised/`

---

## Species with Best Average SNR

| Rank | Species | Avg SNR | Sample Size |
|------|---------|---------|-------------|
| 1 | Graylag Goose | 7.3 dB | 195 detections |
| 2 | Pink-footed Goose | 6.4 dB | 8 detections |
| 3 | Great Snipe | 3.7 dB | 7 detections |
| 4 | Great Bittern | 2.4 dB | 9 detections |
| 5 | Spotted Crake | 2.3 dB | 263 detections |

---

## Weather Correlation

### Recording Conditions:
- **Oct 13:** Light rain overnight
- **Oct 14:** Partly cloudy, unsettled → Clearing, drier
- **Oct 15:** Damp, foggy, low visibility

### Impact on SNR:
Graylag Goose detections show consistent quality across all weather conditions, suggesting:
- Loud vocalizations
- Close proximity to recorder
- Resistant to weather-induced noise

---

## Files Generated

### Analysis Results:
- `results/all_detections_with_weather.csv` - Full BirdNET results with weather metadata
- `results/noise_analysis.csv` - SNR analysis for 500 detections
- `results/cleanest_detections.csv` - Top 6 cleanest recordings metadata
- `results/detection_stats.csv` - Statistical summary by species

### Audio Files:
- `results/audio_clips_enhanced/` - 4,260 clips with smart enhancement
- `results/audio_clips_denoised/` - 160 clips with advanced denoising
- `results/audio_clips/` - Original extracted clips (unprocessed)

### Visualizations:
- `results/species_detections.png` - Species distribution bar chart
- `results/confidence_distribution.png` - Confidence histogram
- `results/detections_over_time.png` - Temporal distribution
- `results/spectrograms/` - Individual waveform + spectrogram images

### Interactive Web Viewer:
- `full_spectrogram_viewer_audio.html` - Browse all detections with audio playback
- Server: `http://localhost:8000`

---

## Recommendations

### For Scientific Analysis:
**Focus on the 6 cleanest recordings** (SNR ≥ 15 dB) for provable bird presence:
- Yellowhammer (1 detection)
- Graylag Goose (5 detections)

These recordings have:
- ✅ High signal-to-noise ratio
- ✅ High AI confidence (82-98%)
- ✅ Advanced spectral denoising applied
- ✅ Minimal background interference

### For General Documentation:
The **160 advanced denoised clips** provide the best overall representation of bird activity, including:
- Best 3 examples per detected species
- Top 100 highest-confidence detections
- Full DSP denoising pipeline applied

### Limitations:
- **92.4% of recordings** have poor SNR (<10 dB)
- Heavy background noise from environmental conditions
- Many detections may be false positives in high-noise segments
- Audio equipment may have contributed to noise floor

---

## Technical Specifications

### BirdNET Model:
- **Version:** 2.4
- **Library:** birdnetlib 0.18.0
- **Sensitivity:** 1.0
- **Minimum Confidence:** 0.1 (post-filtered to ≥0.70 for quality analysis)

### Processing Environment:
- **Platform:** macOS (Apple Silicon)
- **Python:** 3.12
- **Key Libraries:** librosa, scipy, soundfile, pandas, numpy

### DSP Techniques:
All advanced denoising uses **state-of-the-art** spectral processing:
- Wiener filtering (optimal MMSE)
- Spectral subtraction with over-subtraction
- Harmonic-percussive source separation (HPSS)
- Multi-band dynamic range processing
- Phase-preserving STFT reconstruction

---

## Conclusion

This analysis processed **48.8 hours** of field recordings from Gaulossen Nature Reserve, detecting **90 bird species** across **6,805 events**.

**Key Findings:**
1. Environmental noise severely limits usable recordings (only 0.6% excellent quality)
2. Graylag Goose produces the loudest, clearest calls (avg 7.3 dB SNR)
3. Advanced DSP denoising can improve poor recordings but cannot overcome fundamental SNR limitations
4. **6 recordings** meet scientific standards for provable bird presence
5. **160 recordings** represent best examples after aggressive denoising

**Future Recommendations:**
- Use windscreens and isolation mounts to reduce noise
- Deploy multiple recorders for cross-validation
- Record during calmer weather conditions
- Consider directional microphones for target species
- Implement real-time noise monitoring

---

*Analysis completed: October 17, 2025*
*Processing time: ~4 hours*
*Tools: BirdNET AI + Custom DSP Pipeline*
