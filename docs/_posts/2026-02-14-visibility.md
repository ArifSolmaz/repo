---
layout: post
title: "Unlock the cosmos with precision timing! Compute CHEOPS and JWST visibility windows for any astronomical target throughout the year with simple Python commands."

repo_url: "https://github.com/alphapsa/visibility"
tags: ["SpaceTelescopes", "Exoplanets", "ObservationalAstronomy", "Python"]
date: 2026-02-14 16:01:09 +0300
---

Planning observations with premier space telescopes like CHEOPS and JWST requires navigating complex orbital mechanics and solar avoidance constraints. Every astronomer knows the frustration of proposing observations only to discover their target star lies in a telescope's blind spot during critical observation windows. This repository tackles that fundamental challenge by providing instant visibility predictions for any celestial target.

The `visibility` tool computes observation windows by modeling each telescope's sun avoidance zones throughout the year, delivering accuracy within ±1 day for CHEOPS targets. With just a few lines of Python, researchers can query specific dates ('Is 55 Cnc visible to JWST on 2022-11-21?') or map entire annual visibility windows for targets like WASP-12 across both telescopes simultaneously. The tool handles target resolution automatically, accepting common star names and catalog identifiers.

Whether you're a postdoc planning your next exoplanet transit observation or a mission planner coordinating multi-telescope campaigns, this utility transforms complex orbital calculations into simple function calls. While it focuses on sun avoidance rather than detailed orbital mechanics, it provides the essential first-pass visibility assessment that every space-based observation program requires.

---

⭐ **Stars:** 3  
💻 **Language:** Python  
🔗 **Repository:** [alphapsa/visibility](https://github.com/alphapsa/visibility)
