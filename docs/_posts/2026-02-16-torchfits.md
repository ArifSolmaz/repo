---
layout: post
title: "TorchFits bridges the cosmic data gap, loading FITS images and catalogs directly into PyTorch tensors with 2-30x speed gains - perfect for GPU-accelerated astronomy and machine learning."

repo_url: "https://github.com/sfabbro/torchfits"
tags: ["AstronomyML", "PyTorch", "FITS", "Python"]
date: 2026-02-16 12:02:33 +0300
---

Modern astronomy generates torrents of data - from gigapixel survey images to billion-star catalogs - but getting this treasure trove into machine learning pipelines has been painfully slow. Traditional FITS readers force astronomers to choose between convenience and performance, creating bottlenecks that can turn a promising neural network experiment into an overnight data loading marathon.

TorchFits eliminates this friction with a multi-threaded C++ engine that streams FITS data directly into PyTorch tensors, bypassing costly intermediate copies. Whether you're loading 4K×4K CCD frames straight to GPU memory or filtering million-row catalogs with SQL-like predicates ("MAG_G < 20.0 AND CLASS_STAR > 0.9") at the C++ level, this library delivers 2-30x speedups over astropy and fitsio. The zero-copy architecture supports CPU, CUDA, and Apple's MPS, while smart chunking handles datasets larger than available RAM.

Perfect for training convolutional networks on galaxy morphologies, building transformer models for stellar classification, or any workflow where astronomical data meets deep learning. With full WCS support and efficient cutout reading, TorchFits transforms FITS from a compatibility headache into a high-performance data source ready for the GPU-accelerated cosmos.

---

⭐ **Stars:** 3  
💻 **Language:** Python  
🔗 **Repository:** [sfabbro/torchfits](https://github.com/sfabbro/torchfits)
