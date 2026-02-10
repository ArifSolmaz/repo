---
layout: post
title: "Real-time alert broker powered by Apache Spark that processes astronomical transients from sky surveys, enriching cosmic events with ML classifications for breakthrough discoveries."

repo_url: "https://github.com/astrolabsoftware/fink-broker"
tags: ["AlertBroker", "TransientAstronomy", "ApacheSpark", "Python"]
date: 2026-02-10 04:01:09 +0300
---

In the era of large-scale sky surveys like the Zwicky Transient Facility and the upcoming Rubin Observatory, millions of astronomical alerts flood in nightly—supernovae exploding, asteroids drifting, gamma-ray bursts blazing across distant galaxies. The challenge isn't just collecting this cosmic fire hose of data, but intelligently filtering and enriching it so researchers can focus on the most scientifically promising events before they fade into obscurity.

Fink transforms this astronomical big data challenge into actionable science through Apache Spark's distributed streaming architecture. The broker continuously ingests alert streams, applies quality cuts, and runs specialized science modules that cross-match events with catalogs, compute machine learning classification scores, and identify everything from Solar system objects to active galactic nuclei. Built on Apache Kafka for real-time ingestion and HBase for storage, Fink's modular design allows the community to deploy custom processing units that can work on single streams or combine multiple data sources for sophisticated multi-messenger astronomy.

Since 2019, Fink has been battle-tested on ZTF's alert stream, successfully identifying and classifying transients across the astronomical spectrum—from nearby young stellar objects to distant kilonovae. As the Rubin Observatory prepares to begin operations, generating 10 million alerts per night, Fink's robust infrastructure stands ready to democratize access to the dynamic universe, enabling both established researchers and citizen scientists to participate in real-time discovery of cosmic phenomena.

---

⭐ **Stars:** 78  
💻 **Language:** Python  
🔗 **Repository:** [astrolabsoftware/fink-broker](https://github.com/astrolabsoftware/fink-broker)
