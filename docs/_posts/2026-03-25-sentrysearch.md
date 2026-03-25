---
layout: post
title: "Find specific moments in hours of dashcam footage by typing what you're looking for - 'red truck running stop sign' instantly returns the exact clip"

repo_url: "https://github.com/ssrajadh/sentrysearch"
tags: ["ComputerVision", "SemanticSearch", "VideoAnalysis", "Python"]
date: 2026-03-25 06:01:09 +0300
---

Ever tried finding that one incident in 50GB of dashcam footage? SentrySearch turns natural language into precise video timestamps. Instead of scrubbing through hours of road footage, just type 'white sedan cutting me off' or 'pedestrian jaywalking' and get the exact clip back in seconds.

Under the hood, it's surprisingly elegant: videos get chunked into overlapping segments, each embedded directly as video (not screenshots) using Google's Gemini Vision model, then stored in ChromaDB for lightning-fast semantic search. The preprocessing is smart too - it skips static chunks where nothing happens and optimizes video quality for better embedding accuracy. When you search, it doesn't just find matches; it auto-trims the original high-quality footage and saves the clip.

Perfect for fleet managers, insurance investigators, or anyone dealing with surveillance footage. The CLI is dead simple, setup takes 2 minutes, and it works offline once indexed. At 354 stars and growing fast, developers are clearly hungry for practical AI tools that solve real problems without the hype.

---

⭐ **Stars:** 354  
💻 **Language:** Python  
🔗 **Repository:** [ssrajadh/sentrysearch](https://github.com/ssrajadh/sentrysearch)
