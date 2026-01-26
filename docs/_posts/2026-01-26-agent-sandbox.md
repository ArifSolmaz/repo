---
layout: post
title: "Kubernetes üzerinde AI agent'ları ve stateful singleton workload'ları için özel olarak tasarlanmış izole sandbox ortamları oluşturan Go tabanlı controller."

repo_url: "https://github.com/kubernetes-sigs/agent-sandbox"
tags: ["Kubernetes", "ArtificialIntelligence", "DevOps", "Go"]
date: 2026-01-26 15:31:09 +0300
---

Modern uygulamalarda AI agent'ları ve uzun süre çalışan stateful uygulamalar için Kubernetes'in standart Deployment veya StatefulSet modellerinin yetersiz kaldığı durumlar vardır. agent-sandbox tam da bu sorunu çözerek, tek container'lı VM benzeri deneyim sunan, kararlı kimliği olan ve kalıcı depolama alanına sahip sandbox ortamları oluşturmanızı sağlar.

Sandbox CRD'si ile stable hostname, persistent storage ve lifecycle management özelliklerine sahip izole ortamlar yaratabilirsiniz. Ek olarak SandboxTemplate ile yeniden kullanılabilir şablonlar, SandboxClaim ile kullanıcı dostu arayüz ve SandboxWarmPool ile önceden hazırlanmış sandbox havuzları sunarak AI runtime'ları ve benzer use case'ler için ideal bir çözüm haline gelir. Python SDK desteği ile programatik yönetim de mümkündür.

---

⭐ **Stars:** 793  
💻 **Language:** Go  
🔗 **Repository:** [kubernetes-sigs/agent-sandbox](https://github.com/kubernetes-sigs/agent-sandbox)
