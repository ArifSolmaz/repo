---
layout: post
title: "Turn your MacBook trackpad into a precision weighing scale using Force Touch sensors - no external hardware needed, just clever exploitation of existing pressure detection"

repo_url: "https://github.com/KrishKrosh/TrackWeight"
tags: ["Swift", "macOS", "Hardware", "Swift"]
date: 2026-02-28 02:01:11 +0300
---

Ever needed to weigh something small but couldn't find a scale? This brilliant hack transforms your MacBook's Force Touch trackpad into an actual weighing scale by tapping into the same pressure sensors Apple uses for trackpad gestures. It's the kind of creative hardware exploitation that makes you think "why didn't I think of that?"

The implementation is surprisingly sophisticated - it uses a custom fork of OpenMultitouchSupport to access private trackpad APIs, requires maintaining finger contact for capacitance detection, and has been calibrated against real digital scales. The developer discovered that macOS already reports pressure data in grams, making the conversion straightforward. With 8,700+ stars and a simple three-step process (finger on trackpad, place object, maintain light contact), it's clearly struck a chord.

Perfect for developers, makers, or anyone curious about creative hardware hacking. Available as a ready-to-use DMG or build from source - just remember you'll need a 2015+ MacBook with Force Touch and to disable App Sandbox for the low-level trackpad access.

---

⭐ **Stars:** 8705  
💻 **Language:** Swift  
🔗 **Repository:** [KrishKrosh/TrackWeight](https://github.com/KrishKrosh/TrackWeight)
