---
layout: post
title: "Hunt for exoplanets hiding in TESS lightcurves with this Python pipeline that transforms stellar brightness data into transit discoveries through automated periodogram analysis and web-friendly visualization."
image: "/assets/images/quicklook-hero.png"
repo_url: "https://github.com/jpdeleon/quicklook"
tags: ["ExoplanetHunting", "TESS", "Astronomy", "Jupyter Notebook"]
date: 2026-02-27 00:01:18 +0300
---

Every two minutes, NASA's TESS satellite captures the brightness of hundreds of thousands of stars, creating a treasure trove of data where exoplanets reveal themselves through tiny, periodic dips in starlight. But sifting through these lightcurves to spot genuine planetary transits among stellar noise and instrumental artifacts requires sophisticated analysis—a challenge that QuickLook elegantly solves with an automated detection pipeline.

This Python toolkit transforms raw TESS photometry into publication-ready transit discoveries through intelligent periodogram analysis using Generalized Lomb-Scargle and Box Least Squares algorithms. Beyond simple planet hunting, QuickLook measures stellar rotation periods, identifies eclipsing binaries, and characterizes any periodic variability lurking in the data. The tool offers multiple interfaces—from Jupyter notebooks for research workflows to a Flask-based web GUI for quick assessments, plus command-line scripts for batch processing. With support for various TESS pipelines (SPOC, TASOC, QLP) and flexible data quality controls, it adapts to different observational scenarios and science goals.

Whether you're a graduate student conducting your first exoplanet survey or a seasoned researcher processing hundreds of targets, QuickLook bridges the gap between raw space telescope data and scientific insight. Its Google Colab compatibility makes it accessible to anyone with a browser, democratizing exoplanet discovery tools that were once confined to specialized research institutions.

---

⭐ **Stars:** 18  
💻 **Language:** Jupyter Notebook  
🔗 **Repository:** [jpdeleon/quicklook](https://github.com/jpdeleon/quicklook)
