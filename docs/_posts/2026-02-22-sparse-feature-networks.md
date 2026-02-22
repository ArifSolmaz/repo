---
layout: post
title: "Peer into galaxy formation using interpretable AI that reveals which visual features predict stellar metallicity and BPT diagnostics from SDSS images"

repo_url: "https://github.com/jwuphysics/sparse-feature-networks"
tags: ["GalaxyEvolution", "ExplainableAI", "AstrophysicsML", "Jupyter Notebook"]
date: 2026-02-22 04:01:07 +0300
---

Understanding how galaxies evolve requires deciphering the complex relationships between their visual morphology and physical properties like gas metallicity and ionization states. Traditional approaches either rely on manual feature extraction or use black-box neural networks that offer little insight into which galactic structures drive their predictions. This creates a fundamental gap between astronomical intuition and machine learning capabilities.

Sparse Feature Networks (SFNets) bridge this divide by introducing a elegant top-k sparsity constraint that forces the model to activate only the most relevant features when predicting galaxy properties from SDSS imaging. Built on PyTorch and fastai, the framework can predict gas metallicity and BPT line ratios directly from galaxy cutouts while revealing exactly which morphological features influenced each decision. The interpretable activations become a new lens for studying galaxy formation physics, essentially turning the neural network into a hypothesis-generating tool for astrophysics.

With pre-trained models available on Zenodo and a streamlined workflow for SDSS data, researchers can immediately start exploring connections between galaxy appearance and evolution. The approach opens new avenues for mechanistic interpretability in astronomy, where understanding the 'why' behind predictions is as crucial as the predictions themselves.

---

⭐ **Stars:** 10  
💻 **Language:** Jupyter Notebook  
🔗 **Repository:** [jwuphysics/sparse-feature-networks](https://github.com/jwuphysics/sparse-feature-networks)
