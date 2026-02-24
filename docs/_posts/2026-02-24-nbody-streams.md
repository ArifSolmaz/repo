---
layout: post
title: "Simulate stellar streams and galaxy collisions with GPU-accelerated N-body physics - watch 100,000 stars dance through spacetime with CUDA kernels and Kahan precision corrections"
image: "/assets/images/Nbody_streams-hero.png"
repo_url: "https://github.com/appy2806/Nbody_streams"
tags: ["Nbody", "StellarStreams", "ComputationalAstronomy", "Python"]
date: 2026-02-24 12:01:14 +0300
---

When globular clusters get torn apart by galactic tides or dwarf galaxies collide in cosmic ballet, the resulting stellar streams stretch across millions of light-years like ghostly ribbons in the night sky. These ephemeral structures hold secrets about dark matter, galactic archaeology, and the violent history of our universe - but simulating their formation requires tracking every single star's gravitational dance with its neighbors.

Nbody_streams delivers exactly this capability through a sleek Python framework that harnesses both CPU and GPU power for direct N-body simulations. The tool shines with custom CUDA kernels using Kahan summation for float32 precision, handling up to 100,000 particles while maintaining the numerical accuracy crucial for long-term stellar dynamics. Beyond raw computation, it integrates with AGAMA for realistic galactic potentials and pyfalcON for tree-based algorithms, plus includes specialized stream generation methods like 'particle spray' techniques.

Whether you're modeling the disruption of the Sagittarius dwarf galaxy, investigating gaps in stellar streams as dark matter signatures, or prototyping new theories of galactic evolution, this repository transforms complex gravitational physics into accessible Python APIs. With built-in visualization tools for mollweide projections and stream analysis utilities, researchers can go from initial conditions to publication-ready results in the same computational environment.

---

⭐ **Stars:** 4  
💻 **Language:** Python  
🔗 **Repository:** [appy2806/Nbody_streams](https://github.com/appy2806/Nbody_streams)
