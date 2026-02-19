---
layout: post
title: "Hand-rolled CUDA compiler targeting AMD GPUs. 15K lines of C99, zero LLVM dependency. Compiles .cu files straight to GFX11 machine code because someone looked at NVIDIA's walled garden and said 'how hard can it be?'"

repo_url: "https://github.com/Zaneham/BarraCUDA"
tags: ["CUDA", "AMD", "Compiler", "C"]
date: 2026-02-19 06:02:01 +0300
---

Ever wanted to run your CUDA kernels on AMD hardware without jumping through HIP translation hoops? BarraCUDA is what happens when someone decides to write a complete CUDA compiler from scratch - lexer, parser, IR, instruction selection, the works. No LLVM, no translation layers, just pure C99 taking your .cu files and spitting out ELF binaries that AMD RDNA 3 GPUs can execute directly.

The audacity is impressive: 15,000 lines of hand-written compiler code with 1,700 lines of instruction selection that the author admits would 'make a compiler textbook weep.' Every encoding has been validated against llvm-objdump with zero decode failures. The build process? Just 'make' - no CMake, no autoconf, no dependency hell. It supports the full CUDA compilation pipeline from preprocessor to binary emission, complete with SSA form IR and proper register allocation.

This is clearly a labor of love from someone who understands both GPU architectures and compiler internals. With AMD gaining ground in the ML space and CUDA's vendor lock-in becoming more problematic, projects like this could be genuinely important. The fact that it actually works and produces validated machine code makes it worth watching, even if you're not ready to bet your production workloads on it yet.

---

⭐ **Stars:** 874  
💻 **Language:** C  
🔗 **Repository:** [Zaneham/BarraCUDA](https://github.com/Zaneham/BarraCUDA)
