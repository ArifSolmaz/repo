---
layout: post
title: "Simulate escaping exoplanet atmospheres and predict their transit spectra with this Python toolkit combining Parker wind models, photoionization physics, and radiative transfer."
image: "/assets/images/sunbather-hero.png"
repo_url: "https://github.com/antonpannekoek/sunbather"
tags: ["Exoplanet", "Atmosphere", "TransitSpectroscopy", "Python"]
date: 2026-03-26 06:01:58 +0300
---

Imagine watching an exoplanet's atmosphere literally boil away into space, stripped by its host star's relentless radiation. This dramatic process, known as atmospheric escape, shapes planetary evolution across the galaxy—and now we can model it with unprecedented detail. Sunbather tackles one of exoplanet science's most complex challenges: predicting what these escaping atmospheres look like when they transit their stars, creating observable signatures we can detect with space telescopes like Hubble and JWST.

This Python package orchestrates a sophisticated simulation pipeline, combining 1D Parker wind profiles through the p-winds package with Cloudy's photoionization modeling to capture the intricate physics of stellar irradiation. The custom radiative transfer module then translates these physical models into synthetic transmission spectra—the actual observational signatures astronomers measure. By integrating these traditionally separate tools, Sunbather enables researchers to move seamlessly from atmospheric physics to telescope-ready predictions.

While still gaining traction in the community, this toolkit addresses a critical need in exoplanet characterization. As next-generation telescopes push the boundaries of atmospheric detection, tools like Sunbather become essential for interpreting observations of hot Jupiters, super-Earths, and other worlds losing their atmospheres to space. For the growing intersection of computational astrophysics and observational exoplanet science, it represents exactly the kind of end-to-end modeling capability the field demands.

---

⭐ **Stars:** 7  
💻 **Language:** Python  
🔗 **Repository:** [antonpannekoek/sunbather](https://github.com/antonpannekoek/sunbather)
