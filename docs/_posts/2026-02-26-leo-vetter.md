---
layout: post
title: "LEO-vetter automates the hunt for real exoplanets by distinguishing genuine transit signals from cosmic false alarms in TESS data - your robotic astronomer for lazy exoplanet operations"

repo_url: "https://github.com/mkunimoto/LEO-vetter"
tags: ["Exoplanet", "TESS", "Astronomy", "Jupyter Notebook"]
date: 2026-02-26 16:01:17 +0300
---

In the vast ocean of stellar light curves from NASA's TESS mission, countless potential planet signals hide among eclipsing binaries, systematic noise, and stellar variability. The challenge isn't just finding these signals - it's separating the genuine exoplanet transits from the astronomical imposters that can fool even experienced researchers.

LEO-vetter tackles this cosmic needle-in-haystack problem with automated vetting that mimics human expertise. Inspired by Kepler's Robovetter, it performs both flux-level analysis on light curves from any mission (Kepler, K2, TESS) and specialized pixel-level vetting for TESS data. The tool computes sophisticated metrics, applies customizable pass-fail thresholds, and generates detailed vetting reports - transforming hours of manual inspection into minutes of automated analysis. Its dual-layer approach catches astrophysical false positives like nearby eclipsing binaries and systematic false alarms from instrumental effects.

Currently optimized for TESS observations of FGKM dwarf stars, LEO-vetter represents the next generation of exoplanet validation tools. With its modular design allowing custom threshold tuning, it's becoming essential infrastructure for exoplanet researchers who need to process hundreds of candidates efficiently while maintaining scientific rigor.

---

⭐ **Stars:** 9  
💻 **Language:** Jupyter Notebook  
🔗 **Repository:** [mkunimoto/LEO-vetter](https://github.com/mkunimoto/LEO-vetter)
