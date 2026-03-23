---
layout: post
title: "Bayesian spectral analysis toolkit that simultaneously decomposes quasar light into AGN powerhouse emission and host galaxy starlight using modern probabilistic programming"
image: "/assets/images/jaxqsofit-hero.png"
repo_url: "https://github.com/burke86/jaxqsofit"
tags: ["Quasars", "BayesianAstronomy", "SpectralAnalysis", "Jupyter Notebook"]
date: 2026-03-23 20:01:02 +0300
---

Quasars present one of astronomy's most challenging spectral decomposition problems: how do you separate the blazing light from a supermassive black hole's accretion disk from the subtle stellar populations of its host galaxy? Traditional methods tackle these components sequentially, but this approach often struggles when cosmic giants blend their signatures into complex, overlapping features that fool conventional fitting algorithms.

JAXQSOFit revolutionizes this challenge through joint Bayesian modeling, simultaneously fitting AGN continua, host galaxy stellar populations, iron emission templates, and Balmer continuum components in a single probabilistic framework. Built on JAX and NumPyro, it leverages modern automatic differentiation and Hamiltonian Monte Carlo sampling to produce full posterior distributions rather than point estimates. The toolkit handles real-world complexities like spectrophotometric calibration errors, outlier-robust Student-t likelihoods, and flexible basis functions for edge corrections—all while allowing custom components for specialized research needs.

This joint approach proves especially powerful for high-redshift surveys and complex spectra where AGN-host degeneracies have historically plagued measurements. By treating the entire system as a unified physical model, JAXQSOFit delivers more stable parameters and realistic uncertainties, making it invaluable for next-generation spectroscopic surveys like DESI and Roman Space Telescope investigations of cosmic dawn.

---

⭐ **Stars:** 3  
💻 **Language:** Jupyter Notebook  
🔗 **Repository:** [burke86/jaxqsofit](https://github.com/burke86/jaxqsofit)
