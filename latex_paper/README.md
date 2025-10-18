# Gaulossen Acoustic Monitoring - LaTeX Manuscript

## Academic Paper for NTNU Bioacoustics Assignment

**Title:** Automated Acoustic Monitoring of Avian Biodiversity at Gaulossen Nature Reserve: A BirdNET-Based Assessment of 82 Species During Autumn Migration

**Format:** Acta Acustica journal style
**Length:** 8 pages main content (double-column) + appendix
**Date:** October 2025

## Structure

### Main Content (Double-Column, ~8 pages)
1. **Abstract** - 250 words summarizing key findings
2. **Introduction** - Context, objectives, hypotheses
3. **Methods** - Recording protocol, BirdNET analysis, verification, behavioral analysis
4. **Results** - Species diversity, social behavior, sentinel mutualism, migration patterns
5. **Discussion** - Methodological validation, ecological findings, limitations
6. **Conclusions** - Summary and recommendations
7. **References** - 26 peer-reviewed sources

### Appendix (Single-Column)
- Complete 82-species list with detection counts
- Temporal distribution figures
- Co-occurrence network visualization
- Representative spectrograms (4 key species)
- Weather data summary
- Data availability links

## Compilation

### Requirements
- LaTeX distribution (TeXLive, MiKTeX, or MacTeX)
- Required packages: graphicx, amsmath, booktabs, natbib, hyperref, etc.

### Compile Commands
```bash
cd latex_paper
pdflatex gaulossen_paper.tex
bibtex gaulossen_paper
pdflatex gaulossen_paper.tex
pdflatex gaulossen_paper.tex
```

Or using latexmk:
```bash
latexmk -pdf gaulossen_paper.tex
```

## Key Findings Highlighted

1. **82 verified species** from 48.8 hours recording (87.8% verification rate)
2. **Extreme social behavior** - 86% of detections from flock species
3. **Sentinel mutualism** - 8,778 corvid-waterfowl co-occurrences (p < 0.001)
4. **Nocturnal migration** - 47 flight calls during 01:00-06:00 peak
5. **Great Snipe leks** - 189 detections with 61% crepuscular pattern

## Data Sources

- Interactive website: https://ziforge.github.io/gaulossen-study/
- GitHub repository: https://github.com/Ziforge/gaulossen-study
- Analysis powered by Praven Pro: https://github.com/Ziforge/praven-pro

## Figures Needed

The LaTeX document references several figures that should be placed in `figures/` directory:

- `temporal_distribution.png` - Hourly detection patterns
- `cooccurrence_network.png` - Species interaction network
- `spectrogram_graylag.png` - Graylag Goose spectrogram
- `spectrogram_snipe.png` - Great Snipe spectrogram
- `spectrogram_grasshopper.png` - Common Grasshopper-Warbler spectrogram
- `spectrogram_crow.png` - Hooded Crow spectrogram

These can be generated from existing spectrograms in `results/spectrograms_best/` directory.

## Citation

```bibtex
@article{redpath2025gaulossen,
  title={Automated Acoustic Monitoring of Avian Biodiversity at Gaulossen Nature Reserve: A BirdNET-Based Assessment of 82 Species During Autumn Migration},
  author={Redpath, George},
  journal={NTNU Bioacoustics Assignment},
  year={2025},
  month={October},
  note={Available at: https://ziforge.github.io/gaulossen-study/}
}
```

## License

This manuscript and associated data are provided for academic purposes under the same license as the Gaulossen study materials.
