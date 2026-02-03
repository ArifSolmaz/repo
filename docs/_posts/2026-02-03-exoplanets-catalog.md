---
layout: post
title: "A blazingly fast Rust-powered exoplanet catalog that transforms NASA's archive into an interactive web interface with SQL querying capabilities - bringing thousands of distant worlds to your fingertips."
image: "/assets/images/exoplanets-catalog-hero.png"
repo_url: "https://github.com/oiwn/exoplanets-catalog"
tags: ["Exoplanets", "Rust", "Astronomy", "Rust"]
date: 2026-02-03 20:00:59 +0300
---

Every confirmed exoplanet represents humanity's triumph over cosmic distances—worlds orbiting alien suns, detected through the subtle dance of stellar light. Yet NASA's treasure trove of exoplanet data often remains locked in static archives, challenging researchers who need dynamic access to explore relationships between planetary characteristics, stellar properties, and discovery methods across thousands of confirmed worlds.

This Rust-powered catalog transforms that challenge into opportunity. Built with Leptos and Axum, it serves NASA Exoplanet Archive data through both an interactive web interface and a robust REST API. Researchers can sort through stellar hosts by effective temperature, query planets by discovery method, or execute complex SQL joins linking stellar properties to planetary characteristics. The Polars-powered backend ensures rapid data processing, while Swagger documentation makes the API accessible to astronomers and developers alike. Whether you're tracking transit photometry patterns or analyzing the metallicity-planet correlation, the toolkit handles everything from simple column sorting to sophisticated cross-dataset queries.

The live deployment at exodata.space democratizes access to exoplanet research, while the open-source codebase enables custom deployments for specialized research workflows. As our catalog of confirmed exoplanets approaches 6,000 worlds, tools like this become essential infrastructure for the next generation of comparative planetology and astrobiology research.

---

⭐ **Stars:** 5  
💻 **Language:** Rust  
🔗 **Repository:** [oiwn/exoplanets-catalog](https://github.com/oiwn/exoplanets-catalog)
