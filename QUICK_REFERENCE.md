# Quick Reference Guide - Gaulossen Analysis

## 📁 File Locations

### Main Project Directory
```bash
cd /Users/georgeredpath/Dev/mcp-pipeline/shared/gaulossen
```

### Audio Files
```bash
cd /Users/georgeredpath/Dev/Gaulossen-recordings/audio_files
```

## 🚀 Quick Commands

### Open Results in Raven Pro

```bash
# From the gaulossen directory:
cd /Users/georgeredpath/Dev/mcp-pipeline/shared/gaulossen

# Open high priority (21 detections)
open -a "/Applications/Raven Pro 1.6/Raven Pro.app" results/python_raven_automated/high_priority_enhanced.txt

# Open rare species (27 detections)
open -a "/Applications/Raven Pro 1.6/Raven Pro.app" results/python_raven_automated/rare_species_combined.txt

# Open all original files
./open_in_raven.sh

# Interactive file selector
python3 open_single_in_raven.py
```

### View Analysis Results

```bash
# View weather metadata
open results/file_metadata_with_weather.csv

# View all detections with weather
open results/all_detections_with_weather.csv

# View suspicious detections
open results/python_raven_automated/suspicious_detections.csv

# View species summary
open results/python_raven_automated/species_summary_python.csv
```

### Re-run Automation

```bash
# Run quality assessment
python3 automated_verification.py

# Run Python automation (no R needed)
python3 python_raven_automation.py

# Generate weather metadata
python3 create_weather_metadata.py

# Detailed analysis
python3 detailed_analysis.py

# Export focused subsets
python3 export_subsets.py
```

## 📊 Key Statistics

**Recordings:**
- 4 files, 48.8 hours total
- October 13-15, 2025
- Gaulossen Nature Reserve, Norway

**Weather Conditions:**
- Oct 13: Light rain, fog (7-11°C)
- Oct 14 night: Light rain (11°C)
- Oct 14 afternoon: Clearing (11°C)
- Oct 15 night: Partly cloudy (10-11°C)

**Detections:**
- Total: 6,805 bird calls
- Species: 90 unique
- High priority: 21 (need verification)
- Rare species: 27 (single detections)

**Quality:**
- High confidence (≥0.50): 2,692 (39.6%)
- Medium confidence (0.25-0.50): 4,113 (60.4%)
- All high-priority detections flagged as suspicious (wide bandwidth)

## 🔍 Important Finding

**All 21 high-priority detections have 9500 Hz bandwidth** (500-10000 Hz range)
- This is suspiciously wide for bird calls
- Likely artifacts or incorrect frequency detection
- **All need manual verification in Raven Pro**

## 📁 Directory Structure

```
gaulossen/
├── results/
│   ├── all_detections_with_weather.csv     ← Main dataset + weather
│   ├── file_metadata_with_weather.csv      ← File info + weather
│   ├── python_raven_automated/             ← Automation outputs
│   │   ├── high_priority_enhanced.txt      ← Open in Raven Pro
│   │   ├── rare_species_combined.txt       ← Open in Raven Pro
│   │   ├── suspicious_detections.csv       ← All flagged
│   │   └── species_summary_python.csv      ← Stats
│   ├── verification_reports/               ← Original filtered tables
│   ├── detailed_analysis/                  ← Statistical analysis
│   ├── focused_exports/                    ← Targeted subsets
│   └── visualizations/                     ← Publication plots
├── automated_verification.py               ← Quality assessment
├── python_raven_automation.py              ← Main automation
├── create_weather_metadata.py              ← Weather integration
├── detailed_analysis.py                    ← Statistical analysis
├── export_subsets.py                       ← Focused exports
└── QUICK_REFERENCE.md                      ← This file
```

## 🌦️ Weather-Annotated Files

**Human-readable filenames:**
- `2025-10-13_Morning_LightRain_7-11C`
- `2025-10-14_Night_LightRain_11C`
- `2025-10-14_Afternoon_BrokenClouds_11C`
- `2025-10-15_Night_PartlyCloudy_10-11C`

**Weather Impact:**
- Wet conditions (rain): 3,002 detections, confidence 0.501
- Dry conditions (clouds): 3,803 detections, confidence 0.475
- **Rain = better detection quality!**

## 🎯 Verification Workflow

### Quick Verification (~35 minutes)

1. **High Priority (15 min)**
   ```bash
   open -a "/Applications/Raven Pro 1.6/Raven Pro.app" \
     results/python_raven_automated/high_priority_enhanced.txt
   ```
   - Review 21 detections
   - All flagged as suspicious
   - Check bandwidth visually

2. **Rare Species (20 min)**
   ```bash
   open -a "/Applications/Raven Pro 1.6/Raven Pro.app" \
     results/python_raven_automated/rare_species_combined.txt
   ```
   - Review 27 single detections
   - Confirm species ID

### In Raven Pro:
- **Spacebar:** Play/pause audio
- **Delete:** Remove false positive
- **Arrow keys:** Navigate selections
- **Ctrl+S:** Save changes

## 📊 Top Species

1. Graylag Goose - 2,871 (42.2%)
2. Spotted Crake - 2,556 (37.6%)
3. Great Snipe - 189 (2.8%)
4. Pink-footed Goose - 189 (2.8%)
5. Great Bittern - 129 (1.9%)

## 🚨 Suspicious Detections

**All 21 high-priority detections flagged because:**
- Bandwidth: 9500 Hz (too wide)
- Frequency range: 500-10000 Hz (default, not species-specific)
- Duration: Exactly 3.0 seconds (BirdNET fixed window)

**Recommendation:** Manually verify all in Raven Pro

## 📖 Documentation Files

- `README.md` - Quick start guide
- `VERIFICATION_GUIDE.md` - Comprehensive manual (300+ lines)
- `COMPLETE_SUMMARY.md` - Full analysis summary
- `QUICK_REFERENCE.md` - This file

## 💡 Tips

**For terminal commands:**
Always use full paths or navigate to directory first:
```bash
# Wrong (from home directory)
open -a "Raven Pro" results/file.txt

# Right
cd /Users/georgeredpath/Dev/mcp-pipeline/shared/gaulossen
open -a "/Applications/Raven Pro 1.6/Raven Pro.app" results/file.txt
```

**For Python scripts:**
```bash
cd /Users/georgeredpath/Dev/mcp-pipeline/shared/gaulossen
python3 script_name.py
```

**For R scripts (if Rraven gets fixed):**
```bash
cd /Users/georgeredpath/Dev/mcp-pipeline/shared/gaulossen
Rscript script_name.R
```

## 🎉 What's Complete

✅ Full bioacoustic analysis (6,805 detections)
✅ Weather data integration (all 4 recordings)
✅ Automated quality assessment
✅ Raven Pro format conversion
✅ Python-based automation (no R needed)
✅ Publication-quality visualizations
✅ Comprehensive documentation

## 🔧 Next Steps

1. **Manual verification** in Raven Pro (~35 min)
2. **Export verified selections** from Raven Pro
3. **Statistical analysis** with weather variables
4. **Write methods section** with weather context
5. **Generate final species list** (verified)

---

**Last updated:** 2025-10-17
**Location:** Gaulossen Nature Reserve, Norway (63.4305°N, 10.3951°E)
**Analysis period:** October 13-15, 2025
