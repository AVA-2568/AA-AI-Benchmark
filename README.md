# 🏆 AI Model Provider Rankings · AI 模型供应商综合排名

[![Monthly Update](https://img.shields.io/badge/update-monthly-blue)](https://github.com/AVA-2568/AA-AI-Benchmark/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

基于 [Artificial Analysis](https://artificialanalysis.ai/leaderboards/providers) 的公开基准测试数据，按自定义权重重算综合能力总分。每月自动更新，帮你一眼看清「哪个 AI 模型最值得用」。

<!--SNAPSHOT_START-->
> 数据快照：2026-07-24 抓取（1068 模型×服务商 → 去重 391 → 取前 15% = 59 行）。
<!--SNAPSHOT_END-->

## 📊 Top 15 排名

<!--TOP15_START-->
| # | Model | Creator | Score | $/1M | Imputed |
|---|---|---|---|---|---|
| 1 | GPT-5.6 Sol (max) | OpenAI | 93.2 | 10.925 | — |
| 2 | Claude Fable 5 (with fallback) | Anthropic | 93.1 | 18.85 | — |
| 3 | Kimi K3 | Kimi | 90.7 | 5.655 | Terminal-Bench Hard(reg), IFBench(reg) |
| 4 | GPT-5.6 Sol (xhigh) | OpenAI | 90.2 | 10.925 | — |
| 5 | GPT-5.5 (xhigh) | OpenAI | 88.2 | 12.018 | — |
| 6 | GPT-5.6 Sol (high) | OpenAI | 88.1 | 10.925 | — |
| 7 | GPT-5.6 Sol (medium) | OpenAI | 86 | 10.925 | — |
| 8 | Claude Opus 4.8 (max) | Anthropic | 85.8 | 9.425 | — |
| 9 | GPT-5.5 (high) | OpenAI | 85.7 | 12.018 | — |
| 10 | GPT-5.6 Terra (max) | OpenAI | 85.5 | 5.463 | — |
| 11 | Claude Sonnet 5 (max) | Anthropic | 85.5 | 5.655 | Terminal-Bench Hard(reg), IFBench(reg) |
| 12 | Grok 4.5 (high) | SpaceXAI | 85.3 | 2.675 | Terminal-Bench Hard(reg), IFBench(reg) |
| 13 | GPT-5.4 (xhigh) | OpenAI | 83.1 | 6.009 | — |
| 14 | GPT-5.6 Terra (xhigh) | OpenAI | 82.9 | 5.463 | — |
| 15 | GPT-5.6 Luna (max) | OpenAI | 82.8 | 2.185 | Terminal-Bench Hard(reg), IFBench(reg) |
<!--TOP15_END-->

👉 [查看完整排名（CSV）](results/aa_providers_scored.csv)

## 🧭 怎么算的

**总分 = Σ（指标得分 × 权重）**，满分 100 分。

| 大类 | 权重 | 主要指标 |
|---|---|---|
| 🧠 Agentic · 智能体 | 20% | GDPval-AA |
| 💻 Coding · 编程 | 20% | Terminal-Bench Hard / v2.1 / SciCode |
| 🌐 General · 通用 | 40% | LCR / Omniscience / IFBench |
| 📚 Knowledge · 知识 | 20% | GPQA Diamond / HLE |

- 各指标按全量样本 **min-max 归一化** 到 0–100 分
- 缺失值用**多变量岭回归**填补，标注 `(reg)`
- 成本按 `70% 输入 + 30% 输出，50% 输入命中缓存` 估算

📖 [完整方法论（含公式推导与 R² 拟合质量）](METHODOLOGY.md)

## 🚀 一键复现

```bash
pip install -r requirements.txt
python scripts/build.py
```

分步跑：`python scripts/parse_aa.py && python scripts/dedup_aa.py && python scripts/score_aa.py`

## 🤖 自动化

由 GitHub Actions 驱动，**每月 1 号**自动抓取最新榜单、重算排名并推送更新。也可以随时在仓库 [Actions](https://github.com/AVA-2568/AA-AI-Benchmark/actions) 页面手动触发。

## 📁 仓库结构

```
├── scripts/          # 数据流水线（抓取 → 解析 → 去重 → 评分）
├── results/          # 最终排名（CSV）
├── .github/          # CI 自动化
└── README.md
```

## ⚠️ 注意事项

- 分数代表**在当前样本中相对靠前**，非理论能力满分
- 标注 `(reg)` 的指标由回归预测填补，参考时可优先看无标注行
- 价格为抓取时快照，随服务商调价变动
- 原始数据版权归 [Artificial Analysis](https://artificialanalysis.ai/) 所有

## 📄 License

评分脚本与整理结果：[MIT License](LICENSE)  
原始数据：© [Artificial Analysis](https://artificialanalysis.ai/)，按原站条款使用
