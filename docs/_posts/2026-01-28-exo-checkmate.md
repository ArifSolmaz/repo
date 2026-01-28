---
layout: post
title: "A chess-inspired AI engine that hunts exoplanets in TESS data by combining physics-informed filtering with dual-view neural networks to distinguish real planets from eclipsing binaries."

repo_url: "https://github.com/r-baruah/Exo-Checkmate"
tags: ["ExoplanetHunting", "TESS", "AstronomyAI", "Python"]
date: 2026-01-28 12:00:58 +0300
---

Planet hunting in the age of TESS is like finding needles in a cosmic haystack—except some needles are actually just bent paperclips. The primary challenge plaguing automated exoplanet discovery is the notorious confusion between genuine planetary transits and eclipsing binary stars, which can produce deceptively similar light curve signatures when observed at low resolution. Current AI models treat these time-series signals as static images, missing crucial temporal patterns that separate true planets from stellar impostors.

EXO-CHECKMATE approaches this problem with the strategic thinking of a chess grandmaster, implementing a four-layer physics-informed pipeline that processes TESS photometry data. The system begins with astrophysical filtering (rejecting oversized or noisy stars), progresses through Box Least Squares periodicity analysis, then deploys its 'Hypersonic Dual-View Engine'—a hybrid neural architecture combining 1D-CNN spatial analysis, bidirectional LSTM temporal modeling, and physics-prior integration. The final layer validates candidates using Hill Stability mechanics to ensure orbital viability. This multi-headed approach can distinguish the U-shaped signatures of planetary transits from V-shaped binary eclipses while detecting transit timing variations that reveal false positives.

Built with PyTorch and designed for researchers working with large-scale survey data, this hackathon-winning tool represents a significant step toward automated, reliable exoplanet validation. As space missions like TESS continue generating terabytes of photometric data, tools like EXO-CHECKMATE become essential for efficiently sifting through millions of light curves to identify the most promising planetary candidates for follow-up observations.

---

⭐ **Stars:** 3  
💻 **Language:** Python  
🔗 **Repository:** [r-baruah/Exo-Checkmate](https://github.com/r-baruah/Exo-Checkmate)
