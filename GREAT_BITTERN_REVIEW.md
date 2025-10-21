# Great Bittern Spectrogram Review

## Overview

**Species:** Great Bittern (*Botaurus stellaris*)
**Total BirdNET Detections:** 129
**Enhanced Audio/Spectrograms Available:** 75
**Review Status:** IN PROGRESS

## Previous Review History

1. **First Review (Best Example #1)**
   - Confidence: 91.3%
   - Result: ❌ REJECTED
   - Reason: Noise/unclear signal

2. **Second Review (Examples #2 and #3)**
   - Example #2 (90.4%): ❌ REJECTED
   - Example #3 (87.3%): ✅ VERIFIED
   - **Current Status:** Great Bittern VERIFIED (added to verified_species_list.csv)

3. **Current Review (All 75 Spectrograms)**
   - User request: "i want more great bittern. because i am not 100% convinced"
   - Purpose: Comprehensive review to confirm which detections are valid

## What to Look For

### Great Bittern "Boom" Call

**Acoustic Characteristics:**
- **Frequency:** 80-300 Hz (very low, infrasonic component)
- **Duration:** 2-3 second pulses
- **Pattern:** Usually 2-5 booms in succession, spaced 2-3 seconds apart
- **Sound:** Deep resonant "boom" like blowing across a bottle top
- **Amplitude:** Very loud, can travel 5km

### Spectrogram Features

**Valid Great Bittern Call:**
- Horizontal low-frequency band (80-300 Hz)
- Clear harmonic structure
- Consistent amplitude through the pulse
- May show fundamental + overtones

**Reject (Not Great Bittern):**
- Broadband noise (rain)
- High-frequency sounds (wind, birds)
- Irregular/mechanical sounds
- No clear low-frequency structure

## Files Generated

1. **Spectrograms (75 files)**
   - Location: `results/spectrograms_great_bittern/`
   - Format: PNG, 1400x600px, Raven Pro style
   - Colormap: Hot (black background)

2. **Enhanced Audio (75 files)**
   - Location: `results/audio_clips_enhanced/`
   - Format: WAV, 44.1kHz
   - Processing: Wiener filtering + HPSS

3. **Review Interface**
   - File: `website/review_great_bittern_all.html`
   - Features:
     - All 75 spectrograms + audio
     - Pass/Fail buttons
     - Keyboard shortcuts (P=pass, F=fail, N=next)
     - Auto-save to localStorage
     - Export results to CSV
     - Progress tracking

## Confidence Distribution

Based on filename analysis:
- **90%+:** 2 files
- **80-89%:** 1 file
- **40-49%:** ~20 files
- **30-39%:** ~25 files
- **25-29%:** ~27 files

## Review Process

1. Open `website/review_great_bittern_all.html` in browser
2. For each detection:
   - View spectrogram
   - Listen to audio
   - Look for low-frequency boom pattern
   - Press P (pass) or F (fail)
3. Export results when complete
4. Update verified_detections.csv based on results

## Expected Outcomes

Given the high noise levels and weather conditions:
- **Pass rate estimate:** 10-30% (valid Great Bittern calls)
- **Most failures:** Rain noise, wind, unclear signals
- **Valid calls:** Likely clustered in time (booming sessions)

## Next Steps After Review

1. Count passed detections
2. If pass rate < 20%: Consider removing Great Bittern from verified list
3. If pass rate > 30%: Great Bittern confirmed, update detection count
4. Document findings in verification_report.md
5. Update website with accurate Great Bittern detection count

## References

- **BirdNET Confidence Range:** 25.0% - 91.3%
- **Human Verification Standard:** Visual + auditory confirmation required
- **Previous User Decision:** Verified based on example #3 (87.3%)
- **Current User Concern:** "i am not 100% convinced"

---

**Generated:** 2025-10-17
**Script:** `generate_great_bittern_spectrograms.py`
**Review Interface:** `website/review_great_bittern_all.html`
