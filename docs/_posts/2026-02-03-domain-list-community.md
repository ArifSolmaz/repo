---
layout: post
title: "The internet's most comprehensive domain classification database - 7K+ stars, community-maintained geo-routing rules for V2Ray that automatically categorize domains by country, content type, and purpose"

repo_url: "https://github.com/v2fly/domain-list-community"
tags: ["V2Ray", "Networking", "GeoRouting", "Go"]
date: 2026-02-03 10:01:25 +0300
---

Ever tried to set up intelligent network routing only to spend hours manually categorizing thousands of domains? This community-driven project has already done the heavy lifting for you. With over 7,400 stars and active maintenance, it's become the de facto standard for domain classification in the V2Ray ecosystem, providing pre-built lists that categorize domains by geography (China vs non-China), content type (ads, media, development tools), and service categories.

What sets this apart is its neutral, data-driven approach and impressive granularity. Want to route all ads through a blocking service? Use `geosite:category-ads-all`. Need to send Chinese domains direct while proxying international traffic? There's `geosite:cn` and `geosite:geolocation-!cn`. The project maintains dozens of carefully curated categories including anti-censorship tools, VPN services, streaming media, and developer resources. It generates both binary (.dat) and human-readable YAML formats, with automated releases and checksums for integrity.

Network administrators, privacy-conscious users, and anyone running V2Ray will find this invaluable. Instead of maintaining your own domain lists or writing complex routing rules, you can leverage the collective knowledge of thousands of contributors. The setup is straightforward - just reference the pre-built categories in your V2Ray config and you're routing traffic intelligently within minutes.

---

⭐ **Stars:** 7436  
💻 **Language:** Go  
🔗 **Repository:** [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)
