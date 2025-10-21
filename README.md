# Gaulosen Nature Reserve - Acoustic Monitoring Study

**Location:** Gaulosen Nature Reserve, Stjørdal, Norway
**Study Period:** October 2025
**Methodology:** Passive acoustic monitoring with BirdNET-Analyzer

## Live Website

**Visit:** [https://ziforge.github.io/gaulosen-study/](https://ziforge.github.io/gaulosen-study/)

Complete automated bioacoustics analysis pipeline for Gaulosen Nature Reserve field recordings (October 13-15, 2025).

## Analysis Summary

- **Total recordings:** 4 files (48.8 hours)
- **Total detections:** 6,805 bird calls
- **Unique species:** 90 species
- **Location:** Gaulosen Nature Reserve, Norway (63.4305°N, 10.3951°E)

## Directory Structure

```
gaulosen/
├── results/
│ ├── all_detections.csv # Master CSV (all detections)
│ ├── species_summary.csv # Species counts
│ ├── file_summary.csv # Per-file statistics
│ ├── csvs/ # Individual file CSVs
│ ├── labels/ # Audacity label files
│ ├── raven_tables/ # Raven Pro selection tables (original)
│ ├── raven_mcp_converted/ # MCP-converted Raven tables
│ └── visualizations/ # Publication-quality plots
├── convert_to_raven.py # MCP conversion script
├── open_in_raven.sh # Auto-open all in Raven Pro
├── open_single_in_raven.py # Interactive Raven opener
└── README.md # This file
```

## Quick Start

### 1. View Analysis Results

```bash
# View species summary
cat results/species_summary.csv | head -20

# View overall statistics
cat results/file_summary.csv
```

### 2. Automated Verification (RECOMMENDED)

**Option A: Open only detections that need verification (RECOMMENDED)**
```bash
./open_verification_files.sh
```

This opens filtered Raven tables with:
- **21 high priority detections** (rare species + low confidence)
- **27 rare species detections** (single detections)
- Interactive menu to choose which files to review

**Option B: Open all files at once**
```bash
./open_in_raven.sh
```

**Option C: Interactive - choose which file to open**
```bash
python3 open_single_in_raven.py
```

**Option D: Manual**
1. Open Raven Pro
2. File → Import Selections → From Selection Table...
3. Select file from `results/raven_mcp_converted/` or `results/verification_reports/`

### 3. View Visualizations

```bash
open results/visualizations/
```

## Files Analyzed

| File | Date | Time | Duration | Detections | Species |
|------|------|------|----------|------------|---------|
| 245AAA...113753.WAV | 2025-10-13 | 11:37:53 | 12.37h | 1,900 | 36 |
| 245AAA...000000.WAV | 2025-10-14 | 00:00:00 | 12.42h | 1,102 | 57 |
| 245AAA...122526.WAV | 2025-10-14 | 12:25:26 | 11.58h | 1,342 | 38 |
| 245AAA...000000.WAV | 2025-10-15 | 00:00:00 | 12.42h | 2,461 | 46 |

## Top 10 Species Detected

1. Graylag Goose - 2,871 detections
2. Spotted Crake - 2,556 detections
3. Great Snipe - 189 detections
4. Pink-footed Goose - 189 detections
5. Great Bittern - 129 detections
6. Hooded Crow - 87 detections
7. Carrion Crow - 84 detections
8. Greater White-fronted Goose - 71 detections
9. Common Crane - 70 detections
10. Common Grasshopper-Warbler - 59 detections

## MCP Pipeline Integration

This analysis uses the MCP (Model Context Protocol) pipeline for automated format conversion:

- **Raven MCP Server:** Port 7085
- **Conversion Tool:** `convert_to_raven.py`
- **Output Format:** Tab-delimited Raven Pro selection tables

### Re-run Conversion

```bash
python3 convert_to_raven.py
```

## Workflow

```
Audio Files (WAV)
 ↓
BirdNET Analysis (automated_batch_analysis.py)
 ↓
Results (CSV + timestamps)
 ↓
MCP Raven Conversion (convert_to_raven.py)
 ↓
Raven Pro Selection Tables (.txt)
 ↓
Manual Verification in Raven Pro
```

## Analysis Parameters

- **BirdNET confidence threshold:** 0.25
- **Location context:** Gaulosen, Norway (63.4305°N, 10.3951°E)
- **Date range:** October 13-15, 2025
- **Species filter:** 270 Norwegian species (location-based)
- **Frequency range (Raven):** 500-10,000 Hz (default bird vocalization range)

## Output Files

### CSV Files
- `all_detections.csv` - Complete detection dataset with absolute timestamps
- `species_summary.csv` - Species occurrence counts
- `file_summary.csv` - Per-file processing statistics

### Raven Pro Selection Tables
- Located in `results/raven_mcp_converted/`
- Tab-delimited format compatible with Raven Pro
- Includes: time bounds, frequency bounds, species ID, confidence scores

### Visualizations
- Species abundance charts
- Confidence distributions
- Temporal activity patterns (24-hour)
- Daily summaries
- Per-species patterns

### Audacity Labels
- Located in `results/labels/`
- Format: `start_time\tend_time\tlabel`
- Import: File → Import → Labels in Audacity

## Audio File Locations

Original audio files:
```
/Users/georgeredpath/Dev/Gaulosen-recordings/audio_files/
```

## Tools Used

- **BirdNET** (v0.18.0) - AI-powered bird species identification
- **Praven Pro** - Python + Raven Pro integration toolkit
- **MCP Pipeline** - Automated bioacoustics workflow
- **Raven Pro 1.6** - Professional bioacoustics analysis software

## Credits

Analysis conducted for NTNU (Norwegian University of Science and Technology) acoustics research.

Powered by:
- BirdNET: Cornell Lab of Ornithology
- Praven Pro: https://github.com/Ziforge/praven-pro
- MCP Pipeline: Custom bioacoustics automation

## Automated Verification Results

The automated quality assessment identified:
- **21 high priority detections** requiring verification (rare species + low confidence)
- **27 rare species** with single detections
- **4,119 total detections flagged** for review (60.5%)
- **2,686 high-confidence detections** (39.5%) - likely correct

### Verification Reports

Located in `results/verification_reports/`:
- `high_priority_review.csv` - 21 most critical detections (START HERE)
- `rare_species_review.csv` - 27 single-detection species
- `master_verification_checklist.csv` - Complete list with priority scores
- `species_confidence_summary.csv` - Per-species statistics
- `duration_anomalies.csv` - Unusual call durations (currently empty)

### Filtered Raven Tables

Pre-filtered selection tables for focused verification:
- `*_high_priority_raven.txt` - Only high-priority detections (21 total)
- `*_rare_species_raven.txt` - Only rare species (27 total)

Use `./open_verification_files.sh` to open these automatically.

## Next Steps

1. **Run automated verification** using `./open_verification_files.sh`
2. **Verify high priority detections** (21 detections - should take ~15 minutes)
3. **Review rare species** (27 detections - additional ~20 minutes)
4. **Export verified selections** for publication
5. **Cross-reference** with field observations
6. **Statistical analysis** using R or Python with CSV exports
7. **Generate report** with verified species list

## Support

For questions about:
- **BirdNET analysis:** See Praven Pro documentation
- **Raven Pro:** Cornell Lab of Ornithology Raven manual
- **MCP Pipeline:** See `/mcp-pipeline/CLAUDE.md`

---

Last updated: 2025-10-17
