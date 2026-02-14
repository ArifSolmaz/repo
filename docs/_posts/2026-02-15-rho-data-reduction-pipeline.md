---
layout: post
title: "Transform raw photons into scientific discoveries with RETRHO's automated observatory pipeline - from messy CCD frames to publication-ready exoplanet transits and variable star analysis"

repo_url: "https://github.com/explorerjs32/rho_data_reduction_pipeline"
tags: ["Exoplanet", "Observatory", "Photometry", "Jupyter Notebook"]
date: 2026-02-15 00:01:07 +0300
---

Every night, observatories collect thousands of raw astronomical images - bias frames, darks, flats, and precious light frames containing signals from distant worlds and variable stars. The RETRHO Data Reduction Pipeline tackles the tedious but critical challenge of transforming these raw CCD frames into calibrated, science-ready data that can reveal exoplanet transits, stellar variability, and transient phenomena.

Built for the Rosemary Hill Observatory at the University of Florida, this automated pipeline intelligently sorts FITS files by header metadata, creates master calibration frames, and performs comprehensive image reduction including hot pixel removal, sky subtraction, and precise image alignment. The real magic happens in the PSF photometry module - an interactive tool that lets researchers select target and reference stars, then automatically extracts high-precision time-series photometry with proper Barycentric Julian Date corrections and instrumental magnitude calculations.

Whether you're hunting for exoplanet transits, monitoring variable stars, or tracking transients, this pipeline bridges the gap between raw observatory data and publishable science. The interactive Jupyter notebook environment makes it accessible to both seasoned astronomers and Python developers entering the field, while the detailed logging ensures reproducible results for peer review.

---

⭐ **Stars:** 4  
💻 **Language:** Jupyter Notebook  
🔗 **Repository:** [explorerjs32/rho_data_reduction_pipeline](https://github.com/explorerjs32/rho_data_reduction_pipeline)
