---
layout: post
title: "Matchlock runs AI agents in sub-second microVMs with network allowlisting and secret injection - your API keys never enter the sandbox, even when the agent gets compromised"

repo_url: "https://github.com/jingkaihe/matchlock"
tags: ["SecurityTools", "AIAgents", "Virtualization", "Go"]
date: 2026-02-09 02:02:58 +0300
---

AI agents are everywhere, but letting them execute arbitrary code on your machine is terrifying. What if they get tricked into running malicious payloads? What if your OpenAI API key gets exfiltrated? Matchlock solves this with ephemeral microVMs that boot in under a second, giving agents a full Linux environment that's completely isolated from your host system.

The secret sauce is the MITM proxy that injects real credentials in-flight - the sandbox only sees placeholders, so even if compromised, your keys stay safe. Network is locked down by default with explicit allowlisting, filesystem is copy-on-write and disposable, and it works identically on Linux servers or MacBooks. The Go and Python SDKs make it dead simple to embed sandboxed execution directly into your AI applications.

At 240 stars, this is still flying under the radar but solving a critical problem as AI agents become mainstream. The fact that it boots VMs faster than Docker containers start is just the cherry on top. If you're building anything with AI code execution, this deserves a deep look.

---

⭐ **Stars:** 240  
💻 **Language:** Go  
🔗 **Repository:** [jingkaihe/matchlock](https://github.com/jingkaihe/matchlock)
