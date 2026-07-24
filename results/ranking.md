# AI 模型综合排名（≥70 分）

> 2026-07-24 更��  |  * 表示回归预测填补  |  ** 表示低可信填补（训练样本 < 50）

| # | Model | Creator | Score | $/1M | Agent | Coding | General | Knowledge | Imputed |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GPT-5.6 Sol (max) | OpenAI | 93.2 | 10.925 | 0.618 | 0.659 | 0.737 | 0.472 | — |
| 2 | Claude Fable 5 (with fallback) | Anthropic | 93.1 | 18.85 | 0.623 | 0.629 | 0.7 | 0.533 | — |
| 3 | GPT-5.6 Sol (xhigh) | OpenAI | 90.2 | 10.925 | 0.595 | 0.614 | 0.71 | 0.447 | — |
| 4 | Kimi K3 | Kimi | 89.7 | 5.655 | 0.593 | 0.53* | 0.747 | 0.443 | Terminal-Bench Hard(reg), IFBench(reg) |
| 5 | GPT-5.5 (xhigh) | OpenAI | 88.2 | 12.018 | 0.496 | 0.606 | 0.743 | 0.443 | — |
| 6 | GPT-5.6 Sol (high) | OpenAI | 88.1 | 10.925 | 0.563 | 0.621 | 0.683 | 0.441 | — |
| 7 | GPT-5.6 Sol (medium) | OpenAI | 86.0 | 10.925 | 0.527 | 0.629 | 0.687 | 0.397 | — |
| 8 | Claude Opus 4.8 (max) | Anthropic | 85.8 | 9.425 | 0.546 | 0.583 | 0.677 | 0.457 | — |
| 9 | GPT-5.5 (high) | OpenAI | 85.7 | 12.018 | 0.484 | 0.598 | 0.733 | 0.43 | — |
| 10 | GPT-5.6 Terra (max) | OpenAI | 85.5 | 5.463 | 0.541 | 0.576 | 0.74 | 0.418 | — |
| 11 | Claude Sonnet 5 (max) | Anthropic | 84.6 | 5.655 | 0.552 | 0.53* | 0.707 | 0.396 | Terminal-Bench Hard(reg), IFBench(reg) |
| 12 | Grok 4.5 (high) | SpaceXAI | 84.5 | 2.675 | 0.514 | 0.53* | 0.677 | 0.403 | Terminal-Bench Hard(reg), IFBench(reg) |
| 13 | GPT-5.4 (xhigh) | OpenAI | 83.1 | 6.009 | 0.446 | 0.576 | 0.74 | 0.416 | — |
| 14 | GPT-5.6 Terra (xhigh) | OpenAI | 82.9 | 5.463 | 0.537 | 0.629 | 0.713 | 0.4 | — |
| 15 | GPT-5.5 (medium) | OpenAI | 82.7 | 12.018 | 0.436 | 0.576 | 0.723 | 0.406 | — |
| 16 | GLM-5.2 (max) | Z AI | 82.2 | 1.72 | 0.505 | 0.508 | 0.713 | 0.401 | — |
| 17 | Gemini 3.6 Flash AI Studio | Google | 82.2 | 2.827 | 0.462 | 0.53* | 0.697 | 0.383 | Terminal-Bench Hard(reg), IFBench(reg) |
| 18 | GPT-5.3 Codex (xhigh) | OpenAI | 82.1 | 4.874 | 0.444* | 0.53 | 0.74 | 0.399 | GDPval-AA(reg), Terminal-Bench v2.1(reg) |
| 19 | Muse Spark 1.1 (xhigh) | Meta | 81.8 | 1.765 | 0.438 | 0.53* | 0.633 | 0.451 | Terminal-Bench Hard(reg), IFBench(reg) |
| 20 | GPT-5.6 Luna (max) | OpenAI | 81.6 | 2.185 | 0.541 | 0.53* | 0.74 | 0.372 | Terminal-Bench Hard(reg), IFBench(reg) |
| 21 | GPT-5.6 Sol (low) | OpenAI | 81.1 | 10.925 | 0.471 | 0.606 | 0.677 | 0.366 | — |
| 22 | Claude Opus 4.7 (max) | Anthropic | 81.0 | 9.425 | 0.497 | 0.515 | 0.703 | 0.396 | — |
| 23 | Gemini 3.5 Flash AI Studio | Google | 81.0 | 3.277 | 0.422 | 0.409 | 0.693 | 0.41 | — |
| 24 | Claude Sonnet 5 (xhigh) | Anthropic | 80.8 | 3.77 | 0.504 | 0.529* | 0.723* | 0.335* | Terminal-Bench Hard(reg), Terminal-Bench v2.1(reg), SciCode(reg), LCR(reg), Omniscience Index(reg), IFBench(reg), GPQA Diamond(reg), HLE(reg) |
| 25 | Qwen3.7 Max | Alibaba | 80.2 | 3.212 | 0.386 | 0.508 | 0.69 | 0.381 | — |
| 26 | MiniMax-M3 (MXFP8) | MiniMax | 80.0 | 0.486 | 0.445 | 0.424 | 0.74 | 0.371 | — |
| 27 | Gemini 3.1 Pro Preview (AI Studio) | Google | 79.7 | 4.37 | 0.232 | 0.538 | 0.727 | 0.447 | — |
| 28 | GPT-5.6 Terra (high) | OpenAI | 79.4 | 5.463 | 0.505 | 0.576 | 0.723 | 0.367 | — |
| 29 | Gemini 3.5 Flash (medium) | Google | 79.1 | 3.277 | 0.414* | 0.394 | 0.71 | 0.399 | GDPval-AA(reg), Terminal-Bench v2.1(reg) |
| 30 | GPT-5.6 Luna (xhigh) | OpenAI | 78.7 | 2.185 | 0.515 | 0.53* | 0.697 | 0.356 | Terminal-Bench Hard(reg), IFBench(reg) |
| 31 | Gemini 3 Pro Preview (high) | Google | 77.1 | 4.387 | 0.409* | 0.417 | 0.707 | 0.372 | GDPval-AA(reg), Terminal-Bench v2.1(reg) |
| 32 | Claude Sonnet 5 (high) | Anthropic | 76.7 | 3.77 | 0.45 | 0.492* | 0.715* | 0.311* | Terminal-Bench Hard(reg), Terminal-Bench v2.1(reg), SciCode(reg), LCR(reg), Omniscience Index(reg), IFBench(reg), GPQA Diamond(reg), HLE(reg) |
| 33 | GPT-5.2 (xhigh) | OpenAI | 76.4 | 4.874 | 0.387* | 0.47 | 0.727 | 0.354 | GDPval-AA(reg), Terminal-Bench v2.1(reg) |
| 34 | MiMo-V2.5-Pro | Xiaomi | 76.3 | 0.497 | 0.383 | 0.432 | 0.733 | 0.338 | — |
| 35 | Kimi K2.6 | Kimi | 75.2 | 1.865 | 0.344 | 0.439 | 0.697 | 0.359 | — |
| 36 | GPT-5.6 Luna (high) | OpenAI | 75.1 | 2.185 | 0.484 | 0.49* | 0.69 | 0.316 | Terminal-Bench Hard(reg), IFBench(reg) |
| 37 | DeepSeek V4 Pro (max) (FP4) | DeepSeek | 74.8 | 1.27 | 0.403 | 0.462 | 0.663 | 0.359 | — |
| 38 | Gemini 3 Flash (AI Studio) | Google | 74.8 | 1.092 | 0.371* | 0.386 | 0.663 | 0.347 | GDPval-AA(reg), Terminal-Bench v2.1(reg) |
| 39 | Qwen3.6 Max Preview | Alibaba | 74.2 | 2.84 | 0.377* | 0.439 | 0.697 | 0.289 | GDPval-AA(reg), Terminal-Bench v2.1(reg) |
| 40 | Claude Opus 4.6 (max) | Anthropic | 73.7 | 9.425 | 0.433* | 0.462 | 0.707 | 0.367 | GDPval-AA(reg), Terminal-Bench v2.1(reg) |
| 41 | Claude Sonnet 4.6 (max) | Anthropic | 73.5 | 5.655 | 0.439 | 0.53 | 0.707 | 0.3 | — |
| 42 | GPT-5.2 Codex (xhigh) | OpenAI | 73.5 | 4.874 | 0.341* | 0.371 | 0.757 | 0.335 | GDPval-AA(reg), Terminal-Bench v2.1(reg) |
| 43 | GPT-5.6 Terra (medium) | OpenAI | 73.3 | 5.463 | 0.451 | 0.49* | 0.68 | 0.316 | Terminal-Bench Hard(reg) |
| 44 | GPT-5.5 (low) | OpenAI | 73.3 | 12.018 | 0.343 | 0.523 | 0.72 | 0.31 | — |
| 45 | Grok 4.20 0309 v2 | SpaceXAI | 73.3 | 2.57 | 0.362* | 0.379 | 0.58 | 0.322 | GDPval-AA(reg), Terminal-Bench v2.1(reg) |
| 46 | Grok 4.20 0309 | SpaceXAI | 73.3 | 2.57 | 0.362* | 0.409 | 0.59 | 0.3 | GDPval-AA(reg), Terminal-Bench v2.1(reg) |
| 47 | Claude Opus 4.5 Vertex | Anthropic | 72.2 | 9.425 | 0.411* | 0.47 | 0.74 | 0.284 | GDPval-AA(reg), Terminal-Bench v2.1(reg) |
| 48 | DeepSeek V4 Pro (high) (FP4) | DeepSeek | 72.0 | 1.27 | 0.4 | 0.417 | 0.65 | 0.335 | — |
| 49 | Grok 4.3 (high) | SpaceXAI | 71.7 | 1.257 | 0.292 | 0.379 | 0.643 | 0.35 | — |
| 50 | Claude Opus 4.7 (Non-reasoning, high) | Anthropic | 71.6 | 9.425 | 0.459* | 0.545 | 0.67 | 0.312 | GDPval-AA(reg), Terminal-Bench v2.1(reg) |
| 51 | Grok Build 0.1 0616 | SpaceXAI | 71.5 | 1.02 | 0.357 | 0.405* | 0.647 | 0.36 | Terminal-Bench Hard(reg), IFBench(reg) |
| 52 | GLM-5.1 (FP8) | Z AI | 71.4 | 1.874 | 0.378 | 0.432 | 0.623 | 0.28 | — |
| 53 | Grok 4.3 (medium) | SpaceXAI | 71.2 | 1.257 | 0.326* | 0.303 | 0.65 | 0.281 | GDPval-AA(reg), Terminal-Bench v2.1(reg) |
| 54 | Claude Sonnet 5 (medium) | Anthropic | 70.9 | 3.77 | 0.401 | 0.447* | 0.669* | 0.284* | Terminal-Bench Hard(reg), Terminal-Bench v2.1(reg), SciCode(reg), LCR(reg), Omniscience Index(reg), IFBench(reg), GPQA Diamond(reg), HLE(reg) |
| 55 | GPT-5.4 (low) | OpenAI | 70.3 | 6.009 | 0.371* | 0.432 | 0.673 | 0.289 | GDPval-AA(reg), Terminal-Bench v2.1(reg) |
