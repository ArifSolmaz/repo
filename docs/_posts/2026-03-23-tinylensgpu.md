---
layout: post
title: "GPU-accelerated gravitational lensing analysis that turns consumer hardware into a cosmic magnifying glass, modeling galaxy-galaxy lenses 100x faster for the next generation of space telescopes"

repo_url: "https://github.com/caoxiaoyue/TinyLensGpu"
tags: ["GravitationalLensing", "Astrophysics", "GPUComputing", "Python"]
date: 2026-03-23 08:01:39 +0300
---

When massive galaxies bend spacetime, they create natural telescopes that magnify distant objects—a phenomenon called strong gravitational lensing. As space missions like Euclid, CSST, and Roman prepare to flood us with unprecedented lensing data, astronomers need tools that can keep pace with this cosmic avalanche. Traditional analysis methods simply won't scale to process thousands of these warped light signatures efficiently.

TinyLensGpu transforms gravitational lens modeling from a supercomputer luxury into desktop reality. Built on JAX, this software achieves remarkable efficiency: what once required four H100 super GPUs now runs on a consumer RTX 4060 Ti, modeling 200×200-pixel lensing images in just 2-3 minutes. The toolkit supports both parametric models (Sérsic, Gaussian, multi-Gaussian expansion) and cutting-edge pixelized source reconstruction with Gaussian Process regularization, all wrapped in a programmatic API that vectorizes likelihood calculations for 10-100x throughput gains.

With a 90-95% success rate on automated lens analysis and proven performance on 1,000 mock lenses plus 63 real Hubble observations, TinyLensGpu democratizes advanced gravitational lensing research. Whether you're mapping dark matter distributions, measuring cosmic distances, or hunting for the most distant galaxies, this tool puts the universe's natural magnifiers at your fingertips—no supercomputer required.

---

⭐ **Stars:** 6  
💻 **Language:** Python  
🔗 **Repository:** [caoxiaoyue/TinyLensGpu](https://github.com/caoxiaoyue/TinyLensGpu)
