# 🏆 AI Model Provider Rankings - AI 模型供应商综合排名

[![Monthly Update](https://img.shields.io/badge/update-monthly-blue)](https://github.com/AVA-2568/AA-AI-Benchmark/actions)
[![Last data update](https://img.shields.io/github/last-commit/AVA-2568/AA-AI-Benchmark?label=last+data+update&style=flat)](https://github.com/AVA-2568/AA-AI-Benchmark/commits/main)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

基于 [Artificial Analysis](https://artificialanalysis.ai/leaderboards/providers) 的公开基准测试数据，按自定义权重重算综合能力总分。每月自动更新。

## 这是什么

本仓库使用 [Artificial Analysis](https://artificialanalysis.ai/leaderboards/providers) 的公开基准数据，**按自定义权重**计算综合分，而非沿用 AA 的合成 Intelligence Index。权重设计偏重实际使用场景（编程 / 通用 / 智能体各 20-40%、知识 20%），详见 [`config.json`](config.json) 与 [METHODOLOGY.md](METHODOLOGY.md)。

**与原始榜单的差异**：
- 9 个评分指标交叉岭回归预测，处理缺失值
- 权重完全可自定义——见 [METHODOLOGY.md](METHODOLOGY.md#指标选取与权重)
- 填补字段在 CSV `Imputed` 列标注
- 流水线开源可本地复现——见下方"一键复现"

<!--SNAPSHOT_START-->
> 2026-07-24 抓取（1068 模型 x 服务商 -> 去重 391 -> >=70 分 53 行）。
> 填补验证：IFBench MAE=0.06 (>10%: 47.4%/331) ; Terminal-Bench Hard MAE=0.03 (>10%: 51.1%/323) ; Terminal-Bench v2.1 MAE=0.05 (>10%: 48.0%/150) ; HLE MAE=0.03 (>10%: 73.0%/378) ; GPQA Diamond MAE=0.05 (>10%: 27.2%/379)
<!--SNAPSHOT_END-->

## 📊 Top 15 排名

<!--TOP15_START-->
| # | Model | Creator | Score | $/1M | Imputed |
|---|---|---|---|---|---|
| 1 | GPT-5.6 Sol (max) | OpenAI | 93.2 | 10.925 | - |
| 2 | Claude Fable 5 (with fallback) | Anthropic | 93.1 | 18.85 | - |
| 3 | GPT-5.6 Sol (xhigh) | OpenAI | 90.2 | 10.925 | - |
| 4 | GPT-5.5 (xhigh) | OpenAI | 88.2 | 12.018 | - |
| 5 | GPT-5.6 Sol (high) | OpenAI | 88.1 | 10.925 | - |
| 6 | Kimi K3 | Kimi | 87.5 | 5.655 | Terminal-Bench Hard(reg), IFBench(reg) |
| 7 | GPT-5.6 Sol (medium) | OpenAI | 86.0 | 10.925 | - |
| 8 | Claude Opus 4.8 (max) | Anthropic | 85.8 | 9.425 | - |
| 9 | GPT-5.5 (high) | OpenAI | 85.7 | 12.018 | - |
| 10 | GPT-5.6 Terra (max) | OpenAI | 85.5 | 5.463 | - |
| 11 | Grok 4.5 (high) | SpaceXAI | 83.2 | 2.675 | Terminal-Bench Hard(reg), IFBench(reg) |
| 12 | GPT-5.4 (xhigh) | OpenAI | 83.1 | 6.009 | - |
| 13 | GPT-5.6 Terra (xhigh) | OpenAI | 82.9 | 5.463 | - |
| 14 | Muse Spark 1.1 (xhigh) | Meta | 82.9 | 1.765 | Terminal-Bench Hard(reg), IFBench(reg) |
| 15 | Claude Sonnet 5 (max) | Anthropic | 82.8 | 5.655 | Terminal-Bench Hard(reg), IFBench(reg) |
<!--TOP15_END-->

> Imputed 列说明：`-` 表示该模型所有 9 个指标均有真实值；`指标名(reg)` 表示该指标为岭回归预测值；`指标名(reg,low)` 表示预测可信度低（训练样本 < 50）。

👉 [查看完整排名（CSV）](results/aa_providers_scored.csv)

## 怎么算的

**总分 = 指标得分 × 权重**，满分 100 分。仅收录 ≥70 分的模型（绝对门槛，不随池子大小变化）。

| 大类 | 权重 | 主要指标 |
|---|---|---|
| Agentic - 智能体 | 20% | GDPval-AA |
| Coding - 编程 | 20% | Terminal-Bench Hard / v2.1 / SciCode |
| General - 通用 | 40% | LCR / Omniscience / IFBench |
| Knowledge - 知识 | 20% | GPQA Diamond / HLE |

### 关键步骤

- **min-max 归一化**：各指标按全量样本缩放到 0-100 分
- **缺失值填补**：9 个评分指标交叉岭回归预测，α=0.1（z-score 空间）
- **特征标准化**：岭回归输入先 z-score 处理，避免 Omniscience Index（量纲 -12~100）主导其他 7 个 0-1 指标——见 [METHODOLOGY 特征标准化](METHODOLOGY.md#特征标准化岭回归输入)
- **成本估算**：70% 输入 + 30% 输出，50% 输入 token 命中缓存；缓存命中价缺失时按 input 价的 0.1× 回退（Anthropic / DeepSeek 行业下限，对 OpenAI 偏高）
- **权重与参数在 [`config.json`](config.json) 中自定义**，无需修改源码
- **每次运行输出留一验证结果与 R²**——见 [validation.json](results/validation.json)

[完整方法论 →](METHODOLOGY.md)

## 一键复现

```bash
pip install -r requirements.txt
python scripts/build.py
```

## 自动化

由 GitHub Actions 驱动，**每月 1 号**自动抓取、重算排名并推送更新（UTC 6:00 / 北京时间 14:00）。Actions 页面可手动触发。失败自动开 Issue（`monthly-update-failure` label 去重，CI retry 不重复开）。

## 仓库结构

```
├── config.json             # 评分权重与参数
├── requirements.txt        # numpy / pandas / scikit-learn
├── METHODOLOGY.md          # 完整方法论
├── scripts/                # 数据流水线
│   ├── build.py            # 一键入口（fetch -> parse -> dedup -> score -> README）
│   ├── parse_aa.py         # AA HTML -> CSV
│   ├── dedup_aa.py         # Model Slug 去重
│   └── score_aa.py         # 标准化 + 岭回归填补 + 评分
├── results/                # CSV 排名 + validation
│   ├── aa_providers_scored.csv
│   └── validation.json     # 留一验证 + R²
├── .github/                # CI 自动化
└── README.md
```

## 注意事项

- 分数代表在当前样本中相对靠前，**非理论能力满分**
- CSV 中 `*` 表示回归预测填补，`**` 表示低可信填补（训练样本 < 50）
- **价格是抓取时快照**，随服务商调价变动
- **原始数据版权归 Artificial Analysis 所有**，按原站条款使用
- 排名每月刷新；标准化 / α / 阈值变更可能引入 4-10 位的 ±2 互调

## License

评分脚本与整理结果：MIT License  
原始数据：(c) Artificial Analysis，按原站条款使用
