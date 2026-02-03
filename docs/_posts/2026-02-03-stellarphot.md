---
layout: post
title: "Transform stellar observations into scientific discoveries with stellarphot - a Python toolkit that extracts precise photometry from astronomical images, powering variable star studies and exoplanet transit detection."
image: "/assets/images/stellarphot-hero.png"
repo_url: "https://github.com/feder-observatory/stellarphot"
tags: ["StellarPhotometry", "ExoplanetHunting", "AstroPython", "Python"]
date: 2026-02-03 16:00:58 +0300
---

Every night, telescopes around the world capture countless photons from distant stars, but those raw images are just the beginning of the story. Hidden within each FITS file are the brightness variations that reveal pulsating variables, eclipsing binaries, and planets transiting their host stars. The challenge? Extracting meaningful photometric measurements from noisy astronomical data with the precision needed for serious science.

Stellarphot bridges this gap with a comprehensive Python toolkit built on the robust AstroPy ecosystem. It performs aperture photometry on your reduced images, intelligently selects comparison stars from catalogs like APASS DR9, and transforms relative measurements into calibrated magnitudes. Whether you're tracking the 11-minute period of a delta Scuti variable or hunting for the subtle 0.01-magnitude dip of an exoplanet transit, stellarphot handles the complex mathematics of differential photometry while you focus on the science. The package seamlessly integrates with Jupyter notebooks, offering an intuitive workflow from raw photons to publication-ready light curves.

Designed with both professional observatories and citizen scientists in mind, stellarphot is already enabling discoveries at facilities like the Feder Observatory. Its exoplanet transit capabilities, powered by the batman package, make it particularly valuable for follow-up observations of TESS candidates and ground-based transit surveys. With just 6 stars on GitHub, this hidden gem deserves wider recognition in the astronomical community.

---

⭐ **Stars:** 6  
💻 **Language:** Python  
🔗 **Repository:** [feder-observatory/stellarphot](https://github.com/feder-observatory/stellarphot)
