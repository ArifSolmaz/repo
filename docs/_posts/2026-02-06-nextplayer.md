---
layout: post
title: "A beautiful native Android video player built with Jetpack Compose, Media3, and FFmpeg that actually handles all your weird video formats without the bloat of mainstream players"
image: "/assets/images/nextplayer-hero.png"
repo_url: "https://github.com/anilbeesetti/nextplayer"
tags: ["Android", "VideoPlayer", "JetpackCompose", "Kotlin"]
date: 2026-02-06 02:01:09 +0300
---

Tired of Android's default video player choking on your MKV files? Or dealing with VLC's clunky mobile interface? Next Player is what happens when someone builds a video player from scratch using modern Android development practices. It's native Kotlin with Jetpack Compose UI, powered by Google's Media3 library and FFmpeg for format support that just works.

This isn't another MediaPlayer wrapper. The developer integrated FFmpeg through JNI for serious codec support, uses Room database for proper media indexing, and built the entire UI in Compose for that smooth, Material You experience. It scans your device intelligently, handles subtitles gracefully, and maintains playback state like a proper modern app should. With 3,500+ stars and active F-Droid distribution, it's already gaining traction among users fed up with bloated alternatives.

Perfect for Android developers looking to study a well-architected media app, or anyone wanting a clean video player that respects your device's resources. The codebase showcases proper coroutine usage, clean MVVM patterns, and real-world JNI integration. Still in active development, so expect some rough edges but also rapid improvements.

---

⭐ **Stars:** 3538  
💻 **Language:** Kotlin  
🔗 **Repository:** [anilbeesetti/nextplayer](https://github.com/anilbeesetti/nextplayer)
