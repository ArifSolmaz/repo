---
layout: post
title: "The battle-tested NGINX Ingress Controller that powered millions of Kubernetes clusters - now entering retirement mode with maintenance until March 2026."

repo_url: "https://github.com/kubernetes/ingress-nginx"
tags: ["Kubernetes", "NGINX", "IngressController", "Go"]
date: 2026-02-06 10:02:32 +0300
---

If you've ever deployed a web service to Kubernetes, chances are you've used ingress-nginx. With nearly 20k stars, this project has been the go-to solution for HTTP/HTTPS routing in Kubernetes clusters for years, acting as the reliable bridge between your services and the outside world using NGINX's proven reverse proxy capabilities.

Here's the reality check: ingress-nginx is officially retiring, with best-effort maintenance continuing only until March 2026. While existing deployments won't break and artifacts remain available, new projects should look toward Gateway API implementations instead. This makes the repo a fascinating piece of Kubernetes history - a reference implementation that defined how millions of developers think about ingress controllers.

For those maintaining existing deployments, this codebase remains a goldmine of production-hardened patterns. For newcomers, it's an educational treasure trove showing how mature infrastructure projects handle complex networking challenges. Either way, it's worth a star as a monument to one of Kubernetes' most influential projects.

---

⭐ **Stars:** 19428  
💻 **Language:** Go  
🔗 **Repository:** [kubernetes/ingress-nginx](https://github.com/kubernetes/ingress-nginx)
