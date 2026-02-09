---
layout: post
title: "TESSreduce transforms NASA's TESS spacecraft data into pristine lightcurves while preserving transient signals like supernovae - complete with PSF photometry, flux calibration, and automated event detection."
image: "/assets/images/TESSreduce-hero.png"
repo_url: "https://github.com/CheerfulUser/TESSreduce"
tags: ["TESS", "Transients", "Photometry", "Jupyter Notebook"]
date: 2026-02-09 16:01:13 +0300
---

When a star explodes in a distant galaxy or a stellar flare erupts across light-years of space, these cosmic fireworks create brief, brilliant signals that can easily be lost in the noise of telescope data. TESSreduce tackles this challenge head-on, designed specifically to preserve transient astronomical events in NASA's Transiting Exoplanet Survey Satellite (TESS) observations while eliminating the background noise that typically obscures these fleeting phenomena.

Built as an elegant extension of the popular lightkurve package, TESSreduce offers a complete pipeline for TESS data reduction. It performs sophisticated background subtraction that accounts for both smooth galactic backgrounds and detector artifacts, aligns images across observation sequences, and conducts difference imaging to highlight temporal changes. The package supports both aperture and Point Spread Function (PSF) photometry methods, with PSF generally proving more robust for faint transient detection. Perhaps most impressively, it can automatically flux-calibrate your photometry using Pan-STARRS 1 and SkyMapper catalog data, transforming raw detector counts into physical flux units or AB magnitudes.

Whether you're hunting supernovae, studying stellar flares, or tracking any other time-variable astronomical phenomenon, TESSreduce streamlines the journey from raw TESS pixels to publication-ready lightcurves. The package even includes a supernova lookup function and can seamlessly link multi-sector observations, making it an essential tool for time-domain astronomy researchers working with one of the most productive space telescopes ever launched.

---

⭐ **Stars:** 27  
💻 **Language:** Jupyter Notebook  
🔗 **Repository:** [CheerfulUser/TESSreduce](https://github.com/CheerfulUser/TESSreduce)
