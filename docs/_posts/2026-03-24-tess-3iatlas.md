---
layout: post
title: "Track interstellar comet 3I/ATLAS through TESS observations with specialized data reduction pipelines that separate comet signals from stellar background contamination."
image: "/assets/images/tess-3iatlas-hero.gif"
repo_url: "https://github.com/jorgemarpa/tess-3iatlas"
tags: ["InterstellarComet", "TESSMission", "AstronomyData", "Jupyter Notebook"]
date: 2026-03-24 08:01:19 +0300
---

When the third known interstellar visitor, comet 3I/ATLAS, graced our solar system, astronomers faced a unique challenge: how do you extract clean photometric data from a moving comet against a field of stars using space telescope observations? This repository tackles that exact problem, providing the complete data reduction pipeline for TESS observations of 3I/ATLAS during its 2025-2026 passage.

The toolkit leverages the tess-asteroids package to create object-centered moving Target Pixel Files (mTPFs) from TESS full-frame images, implementing sophisticated background modeling to separate scattered light and stellar contamination from the comet's true signal. The pipeline offers multiple photometric extraction methods: aperture photometry for both the comet core and extended tail, plus PSF photometry focused specifically on the nucleus. The processed data reveals the comet's brightness variations with remarkable precision, complete with animated visualizations showing raw versus background-corrected observations.

This represents more than just another data reduction script—it's a complete framework for studying transient solar system objects with TESS. The methodology could be adapted for asteroids, other comets, or any moving target observed by space-based surveys. With data products archived on Zenodo and continuous updates as new observations become available, this repository serves both as a scientific resource and a template for future moving object studies with precision photometry missions.

---

⭐ **Stars:** 3  
💻 **Language:** Jupyter Notebook  
🔗 **Repository:** [jorgemarpa/tess-3iatlas](https://github.com/jorgemarpa/tess-3iatlas)
