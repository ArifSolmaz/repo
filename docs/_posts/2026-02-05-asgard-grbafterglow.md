---
layout: post
title: "ASGARD decodes the afterglow signatures of gamma-ray bursts—the most violent explosions in the universe—with state-of-the-art Fortran simulations covering radio to VHE radiation."

repo_url: "https://github.com/mikuru1096/ASGARD_GRBAfterglow"
tags: ["GammaRayBursts", "Astrophysics", "Fortran", "Fortran"]
date: 2026-02-05 04:01:09 +0300
---

When a massive star collapses or two neutron stars merge, the resulting gamma-ray burst unleashes more energy in seconds than our Sun will produce in its entire lifetime. But the initial flash is just the beginning—what follows is an afterglow that can shine across the electromagnetic spectrum for months, carrying crucial information about the physics of these cosmic cataclysms. ASGARD (A Standard Gamma-ray burst Afterglow Radiation Diagnoser) tackles one of the most computationally demanding challenges in high-energy astrophysics: accurately modeling this complex afterglow emission.

Built entirely in Fortran with OpenMP parallelization, ASGARD employs sophisticated numerical methods including WENO5 schemes for fifth-order accuracy and composite Simpson's integration to solve electron continuity equations and compute synchrotron and synchrotron self-Compton radiation. The code handles extreme conditions that would break simpler models—magnetic fields approaching equipartition and ambient densities exceeding 10^6 particles per cubic centimeter—while covering the complete electromagnetic spectrum from radio waves to very high-energy gamma rays. It includes critical physical processes like synchrotron self-absorption, gamma-gamma annihilation, and even energy injection from black hole accretion.

With its recent updates supporting density jumps and cavity modeling around progenitor stars, ASGARD enables researchers to probe the environments where these cosmic explosions occur. The code's exceptional efficiency means that million-sample parameter studies that once required supercomputers can now run on workstations in hours, making cutting-edge GRB afterglow analysis accessible to research groups worldwide.

---

⭐ **Stars:** 11  
💻 **Language:** Fortran  
🔗 **Repository:** [mikuru1096/ASGARD_GRBAfterglow](https://github.com/mikuru1096/ASGARD_GRBAfterglow)
