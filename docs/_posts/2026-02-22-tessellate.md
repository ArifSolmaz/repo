---
layout: post
title: "TESSELLATE hunts for cosmic explosions and stellar outbursts in TESS data, turning NASA's planet-hunting telescope into a transient event discovery machine for supercomputer-scale analysis."

repo_url: "https://github.com/rhoxu/TESSELLATE"
tags: ["TESS", "Transients", "Astronomy", "Jupyter Notebook"]
date: 2026-02-22 16:01:09 +0300
---

The universe is constantly erupting with spectacular transient events—stellar flares, supernovae, and mysterious outbursts that can appear and vanish in days or hours. While NASA's TESS telescope was designed to hunt for exoplanets, its continuous monitoring of vast stellar fields makes it an inadvertent treasure trove for discovering these fleeting cosmic phenomena. The challenge? Systematically searching through terabytes of lightcurve data to find the astronomical needles in this haystack.

TESSELLATE transforms this challenge into an opportunity by creating an automated pipeline that scours TESS data archives for untargeted transient events. Built for supercomputer environments like OzStar, it leverages the MAST archive and a customized version of TESSreduce to process lightcurves at scale. The pipeline handles the heavy lifting of data access, reduction, and analysis, though the developers refreshingly acknowledge the occasional supercomputer gremlins that make jobs fail mysteriously before working perfectly on the next attempt.

This tool opens new frontiers for time-domain astronomy, enabling researchers to conduct systematic surveys for stellar variability and transient events that might otherwise be missed in targeted observations. Whether you're hunting for rare stellar explosions or studying the variability of entire stellar populations, TESSELLATE provides the computational framework to turn TESS's planetary survey into a comprehensive transient discovery engine.

---

⭐ **Stars:** 3  
💻 **Language:** Jupyter Notebook  
🔗 **Repository:** [rhoxu/TESSELLATE](https://github.com/rhoxu/TESSELLATE)
