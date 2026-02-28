---
layout: post
title: "The ultimate transformer size competition: build the smallest model that can add two 10-digit numbers with 99%+ accuracy. Current record holder uses just 36 parameters with 100% accuracy."
image: "/assets/images/AdderBoard-hero.png"
repo_url: "https://github.com/anadim/AdderBoard"
tags: ["Transformers", "MachineLearning", "ModelCompression", "Python"]
date: 2026-02-28 14:01:06 +0300
---

Think transformers are bloated? This repository hosts a fascinating competition to build the absolute smallest transformer that can reliably add two 10-digit numbers. What started as a challenge between Claude and Codex (producing 6,080 and 1,644 parameter models respectively) has evolved into a community-driven leaderboard where researchers are pushing the boundaries of model efficiency to absurd extremes.

The current champion achieves 100% accuracy with just 36 parameters using clever tricks like ALiBi slopes tuned for base-10 arithmetic, sparse embeddings, and gated ReLU networks. The leaderboard tracks both hand-coded weights (constructive proofs) and trained models, encouraging innovation in architecture design, tokenization strategies, and training algorithms. Each entry reveals ingenious techniques like factorized embeddings, rotation matrices with specific angles, and parabolic decode heads.

This isn't just academic navel-gazing—it's a masterclass in understanding what transformers actually need to solve specific problems. Whether you're interested in model compression, mathematical reasoning in neural networks, or just love seeing engineers optimize the hell out of things, this repository offers concrete examples and techniques you can apply to your own efficiency challenges.

---

⭐ **Stars:** 164  
💻 **Language:** Python  
🔗 **Repository:** [anadim/AdderBoard](https://github.com/anadim/AdderBoard)
