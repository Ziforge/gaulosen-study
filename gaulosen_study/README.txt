================================================================================
GAULOSEN NATURE RESERVE ACOUSTIC MONITORING STUDY
================================================================================

Author: George Redpath
Institution: Norwegian University of Science and Technology (NTNU)
Study Period: October 13-15, 2025
Date: October 22, 2025

================================================================================
PACKAGE CONTENTS
================================================================================

This package contains materials for the paper:

"Baseline Acoustic Biodiversity Assessment of Gaulosen Nature Reserve:
Monitoring 77 Bird Species Along the East Atlantic Flyway"

================================================================================
DIRECTORY STRUCTURE
================================================================================

gaulosen_study/
├── paper/
│   ├── gaulossen_paper.pdf          [MAIN SUBMISSION - 19 pages]
│   ├── gaulossen_paper.tex          [LaTeX source]
│   └── references.bib               [Bibliography (15 references)]
│
├── figures/
│   ├── [All figures embedded in paper]
│   ├── [6 field deployment photos]
│   └── [Spectrograms and diagrams]
│
├── data/
│   ├── species_data.json            [74 verified species metadata]
│   └── species_files.json           [Audio/spectrogram file paths]
│
├── supplementary/
│   ├── [74 species spectrograms]    [High-resolution PNG files]
│   └── [74 audio samples]           [Enhanced MP3 clips]
│
├── rejected_species/                [Rejection transparency]
│   ├── data/                        [3 rejection CSV files]
│   ├── spectrograms/                [132 spectrogram images]
│   ├── audio/                       [1,648 WAV files]
│   └── REJECTION_SUMMARY.txt        [Detailed rejection analysis]
│
├── raw_data/                        [Analysis pipeline data]
│   ├── birdnet_output/              [BirdNET v2.4 raw CSV files - 4 files]
│   ├── weather_data/                [Meteorological context - 2 files]
│   ├── analysis_csvs/               [Detection databases - 3 files]
│   ├── raven_tables/                [Raven Pro selection tables - 4 files]
│   └── RAW_DATA_README.txt          [Pipeline documentation]
│
├── Gaulosen_2025-10-13_Day1_11h37.WAV  [Day 1: Oct 13, 11:37-midnight - 4.0 GB]
├── Gaulosen_2025-10-14_Day2_00h00.WAV  [Day 2: Oct 14, 00:00-12:00 - 4.0 GB]
├── Gaulosen_2025-10-14_Day2_12h25.WAV  [Day 2: Oct 14, 12:25-midnight - 3.7 GB]
├── Gaulosen_2025-10-15_Day3_00h00.WAV  [Day 3: Oct 15, 00:00-12:25 - 4.0 GB]
│
└── README.txt                       [This file]

================================================================================
MAIN PAPER DETAILS
================================================================================

FILE: paper/gaulossen_paper.pdf

Title: Baseline Acoustic Biodiversity Assessment of Gaulosen Nature Reserve:
       Monitoring 77 Bird Species Along the East Atlantic Flyway

Pages: 19 pages (double-column format)

Sections:
- Abstract
- Introduction (Conservation context for Important Bird Area)
- Methods (Field deployment, BirdNET analysis, two-stage verification)
- Results (77 species, 4,085 detections, behavioral findings)
- Discussion (Methodological validation, conservation implications)
- Conclusions
- References (15 citations)
- Appendix (Complete species list with detection counts)

Key Findings:
- 77 verified bird species from 90 initially detected (85.6% pass rate)
- Two-stage verification: Audio quality (90→82) → Biological screening (82→77)
- 4,085 verified detections from 6,805 initial detections (60.0% pass rate)
- Great Snipe migration stopover documented (189 detections, 69% dusk)
- Nocturnal migration flight calls (47 detections, 01:00-06:00)
- Weather-resilient monitoring (77 species despite 80% rain/fog coverage)

================================================================================
METHODOLOGY HIGHLIGHTS
================================================================================

Equipment:
- AudioMoth v1.2 autonomous recorder
- 48 kHz sampling, 48.8 hours continuous recording
- Deployed October 13-15, 2025 at Gaulosen IBA (63.341°N, 10.215°E)

Analysis Pipeline:
1. BirdNET v2.4 automated detection → 90 species, 6,805 detections
2. Audio enhancement (Wiener filtering + HPSS) for rain noise reduction
3. Stage 1 verification: Audio quality & spectrogram screening → 82 species
4. Stage 2 verification: Biological plausibility screening → 77 species
5. Final dataset: 77 species, 4,085 verified detections

Tool Development:
- Praven Pro toolkit created for this study
- GitHub: https://github.com/Ziforge/praven-pro
- Enables efficient BirdNET→Raven Pro verification workflow

================================================================================
DATA FILES
================================================================================

data/species_data.json:
- Complete metadata for all 77 verified species
- Scientific names, descriptions, call characteristics
- Conservation status information

data/species_files.json:
- File paths for audio samples and spectrograms
- Maps each species to best quality examples
- Used for website generation

================================================================================
SUPPLEMENTARY MATERIALS
================================================================================

supplementary/ directory contains:
- 77 high-resolution spectrograms (one per verified species)
- 77 enhanced audio clips (MP3 format, noise-reduced)
- These support the verification protocol described in Methods

Note: Full raw audio dataset (48.8 hours WAV files) available on request
      GitHub repository: https://github.com/Ziforge/gaulosen-study

================================================================================
COMPILATION INSTRUCTIONS (for LaTeX source)
================================================================================

To recompile the paper from source:

1. Required LaTeX packages:
   - article (document class)
   - natbib (bibliography)
   - graphicx (figures)
   - multicol (two-column layout)
   - tikz (diagrams)
   - amsmath (equations)

2. Compilation commands:
   pdflatex gaulossen_paper.tex
   bibtex gaulossen_paper
   pdflatex gaulossen_paper.tex
   pdflatex gaulossen_paper.tex

3. Output: gaulossen_paper.pdf (19 pages)

================================================================================
VERIFICATION SUMMARY
================================================================================

Two-Stage Verification Protocol:

BirdNET Initial Output:        90 species, 6,805 detections
After Stage 1 (Audio Quality): 82 species, 4,108 detections (8 rejected)
After Stage 2 (Biological):    77 species, 4,085 detections (5 rejected)

Overall Pass Rates:
- Species-level: 85.6% (77/90)
- Detection-level: 60.0% (4,085/6,805)

Stage 2 Pass Rates:
- Species-level: 93.9% (77/82, 95% CI: [86.5%, 97.9%])
- Detection-level: 99.4% (4,085/4,108)

Rejected Species (Stage 2 - Biological Impossibilities):
1. Lesser Spotted Woodpecker (14 detections) - Nocturnal impossibility
2. European Storm-Petrel (4 detections) - Oceanic species inland
3. Manx Shearwater (3 detections) - Pelagic species inland
4. Bar-headed Goose (1 detection) - Non-native escaped bird
5. Western Capercaillie (1 detection) - Habitat mismatch

================================================================================
RAW DATA ARCHIVE
================================================================================

The raw_data/ directory contains the analysis pipeline data from BirdNET
output to final results.

Contents:
- 4 BirdNET CSV files (raw automated classification output)
- 2 weather data files (meteorological context + rain correlation)
- 3 analysis CSV files (detection databases)
- 4 Raven Pro selection tables (verification workflow files)
- Pipeline documentation (RAW_DATA_README.txt)

Original Recordings:
- 4 continuous WAV files (48.8 hours @ 48 kHz, 15.7 GB total)
- Located in package root directory
- Unedited field recordings

================================================================================
REJECTED SPECIES DOCUMENTATION
================================================================================

The rejected_species/ directory contains documentation for all species
removed during the two-stage verification protocol.

Contents:
- 3 CSV files documenting rejection decisions and borderline cases
- 132 spectrograms of rejected/borderline detections
- 1,648 enhanced audio clips (WAV format)
- Rejection analysis (REJECTION_SUMMARY.txt)

Key Rejections:
1. Great Bittern (75 detections) - Rain drops on AudioMoth (false positive)
2. Common Grasshopper-Warbler (59) - Migration timing impossible (too late)
3. Lesser Spotted Woodpecker (14) - Nocturnal impossibility
4. European Storm-Petrel (4) - Oceanic species inland
5. Manx Shearwater (3) - Pelagic species inland
6. Black Woodpecker (2) - Nocturnal impossibility
7. Corn Crake (1) - Migration timing impossible
8. Bar-headed Goose (1) - Non-native escaped bird
9. Western Capercaillie (1) - Habitat mismatch

Borderline Species (7 species documented):
- Spotted Crake, Tawny Owl, Eurasian Pygmy-Owl, Common Loon, Common Scoter

================================================================================
ONLINE RESOURCES
================================================================================

Interactive Website:
https://ziforge.github.io/gaulosen-study/

- Species gallery with audio samples and spectrograms
- Behavioral findings (Great Snipe, Graylag Goose flock dynamics)
- Field report with deployment photos
- Complete methodology documentation

GitHub Repository:
https://github.com/Ziforge/gaulosen-study

- Full dataset (species data, audio clips, spectrograms)
- LaTeX source code
- Website source files
- Analysis scripts

Praven Pro Toolkit:
https://github.com/Ziforge/praven-pro

- Open-source Python toolkit for BirdNET verification
- Enables the two-stage verification workflow used in this study
- Available for broader bioacoustics research community

================================================================================
CONTACT INFORMATION
================================================================================

For questions regarding this submission:

Author: George Redpath
Institution: Norwegian University of Science and Technology (NTNU)
Email: [Available via GitHub profile]

Study conducted: October 13-15, 2025
Paper submitted: October 22, 2025

================================================================================
ACKNOWLEDGMENTS
================================================================================

Equipment: NTNU Department of Acoustics
Site Access: Gaulosen Nature Reserve management
Software: BirdNET development team (Cornell Lab & Chemnitz University)
AI Assistance: Claude (Anthropic) via Claude Code for analysis workflows

================================================================================
LICENSE & USAGE
================================================================================

This research is made available for academic and conservation purposes.

Data: Creative Commons Attribution 4.0 International (CC BY 4.0)
Code: MIT License (Praven Pro toolkit)
Paper: Academic submission - citation required for reuse

Suggested Citation:
Redpath, G. (2025). Baseline Acoustic Biodiversity Assessment of Gaulosen
Nature Reserve: Monitoring 77 Bird Species Along the East Atlantic Flyway.
Norwegian University of Science and Technology (NTNU), Trondheim, Norway.

================================================================================
FILE CHECKSUMS (for verification)
================================================================================

Main paper PDF: gaulossen_paper.pdf
Size: 9.7 MB
Pages: 19

LaTeX source: gaulossen_paper.tex
Lines: 1,071

Bibliography: references.bib
Entries: 16 (15 cited + 1 unused)

Figures: 15+ embedded images (spectrograms, diagrams, field photos)

Data files: 2 JSON files (species_data.json, species_files.json)

Supplementary: 77 spectrograms + 77 audio clips

================================================================================
END OF README
================================================================================
