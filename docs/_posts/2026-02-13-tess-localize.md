---
layout: post
title: "Hunt down the cosmic culprits behind stellar variability! TESS-Localize pinpoints exactly which star in crowded fields is creating those mysterious frequency signals in your photometry data."
image: "/assets/images/TESS-Localize-hero.png"
repo_url: "https://github.com/Higgins00/TESS-Localize"
tags: ["VariableStars", "TESS", "StellarAstronomy", "Python"]
date: 2026-02-13 16:01:12 +0300
---

In the crowded stellar neighborhoods captured by NASA's TESS mission, identifying which star is responsible for periodic brightness variations can feel like solving a cosmic whodunit. When your aperture photometry reveals intriguing frequency signatures, you know something interesting is pulsating, eclipsing, or rotating—but which star among dozens of candidates is the true source? TESS-Localize transforms this detective work into precise science, using sophisticated signal analysis to pinpoint the exact pixel location of variability sources within Target Pixel Files. The tool employs principal component analysis to strip away systematic trends, then maps signal-to-noise ratios across the entire field to reveal where your frequencies originate. Simply feed it a list of related frequencies and specify how many principal components to remove, and watch as it generates beautiful heatmaps showing the smoking gun location marked with a black X. Cross-referenced with Gaia catalog data, you'll get not just coordinates but stellar context—magnitudes, proper motions, and distances that help confirm your detection. Whether you're studying pulsating stars, hunting for new variables, or validating exoplanet candidates, this Python package brings CSI-level precision to stellar photometry analysis.

---

⭐ **Stars:** 21  
💻 **Language:** Python  
🔗 **Repository:** [Higgins00/TESS-Localize](https://github.com/Higgins00/TESS-Localize)
