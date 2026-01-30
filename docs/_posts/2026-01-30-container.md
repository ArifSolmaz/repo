---
layout: post
title: "Apple's official tool for running Linux containers as lightweight VMs on Mac - Swift-native, Apple Silicon optimized, OCI-compatible, and surprisingly it actually exists"
image: "/assets/images/container-hero.gif"
repo_url: "https://github.com/apple/container"
tags: ["Swift", "Containers", "AppleSilicon", "Swift"]
date: 2026-01-30 20:01:21 +0300
---

Wait, Apple built their own container runtime? In Swift? For Mac? Yes, and it's not what you'd expect. Instead of fighting macOS to run Linux containers natively, `container` embraces virtualization - each container runs in its own lightweight VM, giving you true Linux compatibility without the usual macOS Docker headaches. It's like Docker Desktop, but designed specifically for Apple Silicon from day one.

What makes this fascinating is the engineering approach: pure Swift implementation that leverages macOS 14's latest virtualization APIs, full OCI compatibility so your existing images work unchanged, and direct integration with Apple's hardware acceleration. You can pull from any registry, push back to them, and the containers you build run anywhere else. The 23K+ stars suggest developers are hungry for a native Mac solution that doesn't feel like a Windows tool ported over.

If you're tired of Docker Desktop's resource usage or want containers that feel native to your Mac workflow, this is worth exploring. Apple's actually maintaining it actively, there's proper documentation with tutorials, and the Swift source means you can see exactly what's happening under the hood.

---

⭐ **Stars:** 23775  
💻 **Language:** Swift  
🔗 **Repository:** [apple/container](https://github.com/apple/container)
