# Automated Verification Guide for Gaulosen Bird Recordings

This guide explains the automated quality assessment and verification workflow for the Gaulosen bird recording analysis.

## Overview

The automated verification system analyzes all 6,805 detections and flags potentially problematic ones for manual review in Raven Pro. Instead of reviewing all detections, you only need to verify **48 high-priority detections** (~35 minutes of work).

## Quick Start

```bash
cd /Users/georgeredpath/Dev/mcp-pipeline/shared/gaulosen

# Run automated quality assessment (generates reports)
python3 automated_verification.py

# Open high-priority detections in Raven Pro
./open_verification_files.sh
```

## What Gets Flagged for Review?

The system uses multiple quality checks:

### 1. High Priority (21 detections)
**Rare species with low confidence** - Most likely to be false positives
- Single detection in the dataset
- Confidence score < 0.50
- **Examples:** River Warbler (0.25), Common Raven (0.26), Western Capercaillie (0.27)

### 2. Rare Species (27 detections)
**Single detections** - Could be rare visitors or false positives
- Only detected once across 48.8 hours
- **Examples:** Black-legged Kittiwake, Great Black-backed Gull, Boreal Owl, Fieldfare

### 3. Medium Confidence (4,113 detections)
**Common species with lower confidence** (0.25-0.50)
- Likely correct but worth spot-checking
- Lower priority than rare species

### 4. Temporal Clustering (249 detections)
**Detections within 3 seconds of each other**
- Potential duplicates
- Overlapping calls from multiple birds

## Quality Metrics

### Confidence Distribution
- **High confidence (≥0.50):** 2,692 detections (39.6%)
- **Medium confidence (0.25-0.50):** 4,113 detections (60.4%)
- **Low confidence (<0.25):** 0 detections (0.0%)

### Duration Analysis
- **Mean duration:** 3.00s
- **Median duration:** 3.00s
- **Too short (<0.5s):** 0 detections
- **Too long (>10.0s):** 0 detections

All detections have normal durations - no duration-based flags.

## Verification Reports

### CSV Reports (in `results/verification_reports/`)

1. **high_priority_review.csv** (21 detections)
   - **START HERE** - Most critical detections
   - Rare species + low confidence
   - Sorted by confidence (lowest first)

2. **rare_species_review.csv** (27 detections)
   - All single-detection species
   - Includes both high and low confidence
   - Worth verifying all of these

3. **master_verification_checklist.csv** (all 6,805 detections)
   - Complete dataset with quality flags
   - Columns:
     - `flag_low_confidence` - Confidence < 0.50
     - `flag_rare_species` - Single detection
     - `flag_short_duration` - Duration < 0.5s (none found)
     - `flag_long_duration` - Duration > 10s (none found)
     - `total_flags` - Sum of all flags
     - `priority_score` - Weighted priority (0-6, higher = more urgent)

4. **species_confidence_summary.csv** (90 species)
   - Per-species statistics
   - Columns: count, mean confidence, std dev, min, max, mean duration
   - Useful for identifying species with consistently low confidence

5. **duration_anomalies.csv** (0 detections)
   - Currently empty (no anomalies found)
   - Would contain calls that are too short or too long

### Raven Pro Selection Tables (in `results/verification_reports/`)

Pre-filtered Raven tables for focused verification:

**High Priority Tables** (21 total detections across 4 files):
- `245AAA0563ED3DA7_20251013_113753_high_priority_raven.txt` (3 selections)
- `245AAA0563ED3DA7_20251014_000000_high_priority_raven.txt` (7 selections)
- `245AAA0563ED3DA7_20251014_122526_high_priority_raven.txt` (4 selections)
- `245AAA0563ED3DA7_20251015_000000_high_priority_raven.txt` (7 selections)

**Rare Species Tables** (27 total detections across 4 files):
- `245AAA0563ED3DA7_20251013_113753_rare_species_raven.txt` (4 selections)
- `245AAA0563ED3DA7_20251014_000000_rare_species_raven.txt` (10 selections)
- `245AAA0563ED3DA7_20251014_122526_rare_species_raven.txt` (5 selections)
- `245AAA0563ED3DA7_20251015_000000_rare_species_raven.txt` (8 selections)

## Verification Workflow

### Step 1: Review High Priority Detections (~15 minutes)

```bash
./open_verification_files.sh
# Choose option 1: High priority only
```

For each detection in Raven Pro:
1. **Visual inspection** - Look at the spectrogram
   - Does it match expected frequency range for the species?
   - Is the pattern consistent with known call structure?
   - Any background noise or interference?

2. **Audio verification** - Listen to the call
   - Does it sound like the identified species?
   - Is it clearly audible or muffled?
   - Any overlapping calls?

3. **Decision**
   - ✅ **Keep** - Looks and sounds correct
   - ❌ **Delete** - False positive (noise, wrong species, artifact)
   - ⚠️ **Flag** - Unsure, needs expert review

### Step 2: Review Rare Species (~20 minutes)

```bash
./open_verification_files.sh
# Choose option 2: Rare species only
```

Same verification process as Step 1, but focus on:
- Are these genuinely rare species?
- Or misidentifications of common species?
- Cross-reference with known species ranges and habitats

### Step 3: Spot-Check Medium Confidence (Optional)

For thoroughness, review a random sample of medium-confidence detections:
1. Open `master_verification_checklist.csv`
2. Filter to `flag_low_confidence == True` AND `flag_rare_species == False`
3. Pick 20-30 random detections from different species
4. Verify in Raven Pro using main selection tables

### Step 4: Export Verified Results

After verification in Raven Pro:
1. File → Export Selections...
2. Choose output format (CSV or selection table)
3. Save as `*_verified.txt` or `*_verified.csv`
4. Document any changes made in verification log

## Interpreting Confidence Scores

### High Confidence (0.75-1.00)
- Very likely correct
- Strong spectral match
- Clear, unambiguous call

### Medium Confidence (0.50-0.74)
- Probably correct
- Good spectral match but some ambiguity
- May have background noise

### Low-Medium Confidence (0.25-0.49)
- Uncertain identification
- Weak spectral match or poor signal-to-noise
- **Requires verification**

### Low Confidence (<0.25)
- Very uncertain
- Poor spectral match
- High chance of false positive
- **Definitely requires verification**
- (None found in this dataset due to 0.25 threshold)

## Species of Interest

### Most Confident Detections (Likely Correct)
Based on mean confidence from `species_confidence_summary.csv`:
1. **Graylag Goose** - 2,871 detections, 0.504 mean confidence
2. **Great Bittern** - 129 detections, 0.505 mean confidence
3. **Spotted Crake** - 2,556 detections, 0.500 mean confidence

### Least Confident Detections (Review Recommended)
1. **Canada Goose** - 47 detections, 0.330 mean confidence
2. **Common Crane** - 70 detections, 0.376 mean confidence
3. **Carrion Crow** - 84 detections, 0.375 mean confidence

### Rare Species Requiring Verification
All 27 species with single detections - see `rare_species_review.csv`

## Tips for Efficient Verification

### In Raven Pro:
1. **Use keyboard shortcuts**
   - Spacebar: Play/pause
   - Arrow keys: Navigate selections
   - Delete key: Remove false positives

2. **Adjust spectrogram settings**
   - Window size: 256-512 samples (good for bird calls)
   - Hop size: 50% overlap
   - Color scale: Adjust for clarity

3. **Compare with reference calls**
   - Use BirdNET's confidence as a guide
   - Cross-reference with Xeno-Canto recordings
   - Check eBird for species occurrence in area

4. **Document decisions**
   - Keep notes on deleted selections
   - Track common false positive patterns
   - Note any interesting observations

## Re-running the Analysis

If you make changes to detections and want to re-analyze:

```bash
# Re-run verification with updated data
python3 automated_verification.py

# The script will regenerate all reports based on current CSV data
```

## Understanding Priority Scores

The `master_verification_checklist.csv` includes a `priority_score` column (0-6):

| Score | Flags | Meaning |
|-------|-------|---------|
| 6 | Rare (3) + Low Conf (2) + Duration Issue (1) | Highest priority |
| 5 | Rare (3) + Low Conf (2) | High priority (21 detections) |
| 3 | Rare (3) only | Medium priority (6 detections) |
| 2 | Low Conf (2) only | Low priority (4,092 detections) |
| 1 | Duration Issue (1) only | Very low priority (0 detections) |
| 0 | No flags | No review needed (2,686 detections) |

## Thresholds and Customization

To adjust verification thresholds, edit `automated_verification.py`:

```python
# Line 23-24: Confidence thresholds
CONFIDENCE_HIGH = 0.75  # High confidence - likely correct
CONFIDENCE_MEDIUM = 0.50  # Medium - review recommended
CONFIDENCE_LOW = 0.25  # Low - definitely review

# Line 27-28: Duration thresholds (seconds)
DURATION_TOO_SHORT = 0.5  # Suspiciously short
DURATION_TOO_LONG = 10.0  # Suspiciously long for most calls
```

Then re-run:
```bash
python3 automated_verification.py
```

## Expected Time Investment

- **High priority verification:** ~15 minutes (21 detections @ ~40 sec each)
- **Rare species verification:** ~20 minutes (27 detections @ ~45 sec each)
- **Spot-check medium confidence:** ~30 minutes (optional)
- **Export and documentation:** ~10 minutes

**Total: 35-75 minutes** (vs. 60+ hours to manually review all 6,805 detections)

## Output for Publication

After verification, you'll have:
1. ✅ **Verified species list** (27 rare species confirmed/rejected)
2. ✅ **Confidence in high-quality detections** (2,686 reviewed by thresholds)
3. ✅ **Quality metrics** (confidence distributions, per-species statistics)
4. ✅ **Temporal patterns** (24-hour activity, date ranges)
5. ✅ **Publication-ready visualizations** (already generated)

## Troubleshooting

### "No detections flagged for verification"
- All detections have high confidence - good news!
- Still recommended to spot-check rare species

### "Too many detections flagged"
- Increase `CONFIDENCE_MEDIUM` threshold (e.g., 0.40 → 0.50)
- Focus only on rare species initially

### "Raven Pro won't open files"
- Check that audio files are in the correct location
- Update audio paths in Raven selection tables if needed

### "CSV reports are empty"
- Check that `all_detections.csv` exists and has data
- Verify column names match expected format (start_s, end_s, etc.)

## Next Steps After Verification

1. **Generate final species list**
   - Count verified species
   - Note confidence in each identification

2. **Statistical analysis**
   - Use verified CSV data
   - Temporal patterns, species co-occurrence, etc.

3. **Report writing**
   - Include verification methodology
   - Report false positive rate (deletions / total reviewed)
   - Discuss confidence thresholds used

4. **Data archiving**
   - Save verified Raven tables
   - Document all changes made
   - Preserve both original and verified datasets

## Support

For questions about:
- **Automated verification**: See this guide
- **BirdNET analysis**: See Praven Pro documentation
- **Raven Pro**: Cornell Lab of Ornithology Raven manual
- **MCP Pipeline**: See `/mcp-pipeline/CLAUDE.md`

---

**Last updated:** 2025-10-17
**Analysis date:** October 13-15, 2025
**Location:** Gaulosen Nature Reserve, Norway (63.4305°N, 10.3951°E)
