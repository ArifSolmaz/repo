---
layout: post
title: "Privacy-first research assistant that achieves 95% SimpleQA accuracy while keeping everything local and encrypted. Searches arXiv, PubMed, and your private docs without sending data to the cloud."

repo_url: "https://github.com/LearningCircuit/local-deep-research"
tags: ["LocalLLM", "ResearchTools", "Privacy", "Python"]
date: 2026-02-07 10:01:09 +0300
---

Research is broken when your most sensitive queries get logged by corporate APIs. Local Deep Research flips the script: run GPT-4 level research entirely on your hardware, with encrypted storage and zero data leakage. It's hitting ~95% on SimpleQA benchmarks while your queries never leave your machine.

This isn't just another RAG wrapper. It orchestrates searches across 10+ sources simultaneously - arXiv papers, PubMed articles, web results, and your private document collections - then synthesizes findings with whichever LLM you prefer (Ollama, Anthropic, OpenAI, or fully local models). Everything runs in Docker, stores data in SQLCipher encryption, and supports both academic researchers paranoid about IP theft and home lab enthusiasts who want serious research capabilities.

Perfect for academics, patent researchers, and anyone doing deep knowledge work who refuses to feed their questions to Big Tech's training datasets. The 4K stars and active Discord suggest this scratches a real itch in the privacy-conscious dev community.

---

⭐ **Stars:** 3966  
💻 **Language:** Python  
🔗 **Repository:** [LearningCircuit/local-deep-research](https://github.com/LearningCircuit/local-deep-research)
