---
layout: post
title: "Real-time HUD for Claude Code showing context usage, active tools, running agents, and todo progress—all in your terminal statusline"
image: "/assets/images/claude-hud-hero.png"
repo_url: "https://github.com/jarrodwatts/claude-hud"
tags: ["Claude", "DevTools", "StatusLine", "JavaScript"]
date: 2026-03-22 18:01:56 +0300
---

Ever wondered what Claude is actually doing behind the scenes? This HUD plugin transforms the opaque Claude Code experience into a transparent, real-time dashboard. Instead of guessing whether you're about to hit context limits or wondering which files Claude is touching, you get live visibility into everything—context usage with color-coded bars, active tool operations, running subagents, and todo progress tracking.

What makes this brilliant is the execution: it uses Claude Code's native statusline API, so there's no separate window to manage or tmux wizardry required. The context tracking uses actual token data from Claude (not estimates), scales with the full 1M context windows, and updates every 300ms. You can watch Claude read files, see agents spin up with their runtime, and track your project progress—all in a clean 2-5 line display that stays out of your way.

With 10,970 stars and dead-simple installation via three slash commands, this is clearly solving a real pain point for Claude Code users. The configuration is thoughtfully designed too—minimal by default but expandable for power users who want full visibility into their AI pair programming sessions.

---

⭐ **Stars:** 10970  
💻 **Language:** JavaScript  
🔗 **Repository:** [jarrodwatts/claude-hud](https://github.com/jarrodwatts/claude-hud)
