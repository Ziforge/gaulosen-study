# Gaulosen Nature Reserve - Verification Report

**Date:** October 13-15, 2025
**Recording Duration:** 48.8 hours
**Analyst:** Human expert review + BirdNET v2.4

---

## Summary

### Human-Verified Data
- **81 species** verified by manual spectrogram/audio review (90.0% pass rate: 81/90)
- **4,067 detections** from verified species only
- **Removed:** 2,738 false positive detections (11 rejected species)

### Verification Method
Each species' best example was manually reviewed by examining:
1. **Raven Pro-style spectrograms** - Visual frequency/time analysis
2. **Enhanced audio** - Wiener filtering + HPSS noise reduction
3. **Pass/Fail decision** - Based on clear bird vocalization vs. rain/noise artifacts

---

## What Has Been Human-Verified ✅

### 1. **Species Presence** (VERIFIED)
All 79 species have been confirmed present through manual review:
- Clear vocalizations visible in spectrograms
- Distinguishable from rain/wind noise
- Enhanced audio confirms bird calls

**Status:** ✅ **COMPLETE - No further verification needed**

---

## What Still Needs Human Verification ⚠️

### 2. **Multiple Detections Per Species** (NEEDS VERIFICATION)

**Current Status:**
- Only the **best example** (highest confidence) per species was reviewed
- Many species have **dozens or hundreds** of additional detections

**Examples:**
- Graylag Goose: 2,871 detections (only 1 verified)
- Pink-footed Goose: 189 detections (only 1 verified)
- Great Snipe: 189 detections (only 1 verified)

**Recommendation:**
- Sample-based verification: Review 5-10 random examples per species
- Focus on species with >50 detections
- Verify confidence threshold (e.g., are all >80% confidence valid?)

**Priority:** 🔴 **HIGH** (affects detection counts and behavioral analysis)

---

### 3. **Temporal Patterns** (NEEDS INTERPRETATION)

**Current Status:**
- Temporal patterns detected (day/night activity, hourly patterns)
- Based on verified species only

**Needs Human Verification:**
- Are temporal patterns **real behavior** or **sampling artifacts**?
- Examples to verify:
  - Graylag Goose nocturnal activity: Real night calling or noise artifacts?
  - Great Snipe peak at 20:00-21:00: Real behavior or detection bias?
  - Common Crane dawn/dusk peaks: Expected migration behavior?

**Recommendation:**
- Manually review 5-10 detections from unusual time periods
- Compare with known species behavior literature
- Check if temporal patterns correlate with weather changes

**Priority:** 🟡 **MEDIUM** (important for behavioral claims)

---

### 4. **Weather Correlations** (CANNOT VERIFY - SAMPLING BIAS)

**Current Status:**
- Most recording occurred during rain/fog
- Weather correlations detected but unreliable

**Issue:**
- **Sampling bias:** We recorded 80%+ during bad weather
- Cannot distinguish "species prefers rain" from "we only recorded during rain"

**Recommendation:**
- **Do not make weather-based behavioral claims**
- State clearly: "Sampling bias prevents weather correlation analysis"

**Priority:** 🟢 **RESOLVED** (do not analyze - acknowledge limitation)

---

### 5. **Species Co-occurrence** (NEEDS VERIFICATION)

**Current Status:**
- Co-occurrence patterns calculated from verified species
- Based on temporal overlap of detections

**Needs Human Verification:**
- Are co-occurrences **real ecological relationships** or **coincidence**?
- Examples to verify:
  - Graylag Goose + Pink-footed Goose: Mixed flocks?
  - Crow species co-occurrence: Territorial overlap or detection confusion?

**Recommendation:**
- Manually review audio from high co-occurrence periods
- Check if multiple species audible in same recording
- Verify species identification in mixed-species contexts

**Priority:** 🟡 **MEDIUM** (interesting but not critical)

---

### 6. **Confidence Thresholds** (NEEDS CALIBRATION)

**Current Status:**
- Used BirdNET confidence scores
- Best examples reviewed, but threshold not calibrated

**Needs Human Verification:**
- What confidence threshold gives reliable detections?
- Is 80% confidence sufficient? 90%? Species-dependent?

**Recommendation:**
- Review 10-20 detections at different confidence levels per species
- Establish species-specific confidence thresholds
- Example: "Graylag Goose: >85% reliable, <70% mostly noise"

**Priority:** 🔴 **HIGH** (affects all detection counts)

---

### 7. **Rare Species** (NEEDS EXTRA VERIFICATION)

**Current Status:**
- 15 species with only 1-5 detections total
- Includes rare species: Corn Crake, River Warbler, Western Capercaillie

**Needs Human Verification:**
- Are these genuine rare sightings or misidentifications?
- Higher stakes for conservation/rare species claims

**Recommendation:**
- **Manual review ALL detections** for species with <10 total detections
- Cross-reference with known species range/habitat
- Consider seasonal migration patterns

**Priority:** 🔴 **HIGH** (rare species claims need extra scrutiny)

---

### 8. **Acoustic Similarity** (NEEDS VERIFICATION FOR CONFUSABLE SPECIES)

**Confusable Species Pairs Detected:**
- Hooded Crow vs. Carrion Crow
- Common Snipe vs. Great Snipe
- Various goose species (Graylag, Pink-footed, Greater White-fronted, Taiga Bean, Tundra Bean)
- Swan species (Whooper, Tundra)

**Needs Human Verification:**
- Are these species truly distinguishable in our noisy recordings?
- Manually review examples of confusable pairs
- May need to combine into species groups if not reliably separable

**Priority:** 🟡 **MEDIUM** (affects species count accuracy)

---

## Recommended Next Steps

### Immediate Priorities (This Week)
1. ✅ **DONE:** Verify species presence (best example per species)
2. 🔴 **TODO:** Calibrate confidence thresholds (review 10 samples per threshold)
3. 🔴 **TODO:** Verify all rare species detections (<10 detections total)

### Short-Term (This Month)
4. 🟡 **TODO:** Sample-verify multiple detections (5-10 per common species)
5. 🟡 **TODO:** Verify temporal patterns (unusual time periods)
6. 🟡 **TODO:** Check confusable species pairs

### Long-Term (Optional)
7. 🟢 **OPTIONAL:** Co-occurrence verification
8. 🟢 **DOCUMENT:** Acknowledge weather sampling bias (no behavioral claims)

---

## Scientific Rigor Notes

### What We CAN Claim (After Verification)
- ✅ Species presence inventory (79 verified species)
- ✅ Relative abundance (if confidence thresholds calibrated)
- ✅ Temporal activity patterns (if temporal verification done)

### What We CANNOT Claim
- ❌ Weather preferences (sampling bias)
- ❌ Absolute population sizes (acoustic surveys measure calling, not abundance)
- ❌ Behavioral motivations (we detect calls, not behaviors)
- ❌ Species interactions (co-occurrence ≠ interaction)

---

## Current Data Quality Assessment

**Strengths:**
- 79 human-verified species
- DSP-enhanced audio (Wiener + HPSS)
- Raven Pro-quality spectrograms
- Honest about limitations

**Limitations:**
- Heavy rain/noise contamination
- Sampling bias (mostly bad weather)
- Single location, single season
- Only best examples verified (not full dataset)

**Overall Quality:** 🟡 **MODERATE**
- Suitable for species inventory
- Not suitable for detailed behavioral ecology without further verification
- Excellent demonstration of acoustic monitoring challenges in adverse conditions
