# 🏆 AI 前沿模型综合排名 — 第一梯队精选榜

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

基于**多个公开、行业认可的第三方基准**，对**国际 + 国内第一梯队**（约 40 个主流前沿模型）按自定义权重重算综合能力分。数据源全部公开、可机器抓取、抗污染，不再依赖单一聚合站。

**核心特性**：
- 🎯 **多源聚合**：LiveBench（抗污染通用）、DeepSWE（长程工程 agent）、EQ-Bench（创意写作）、Artificial Analysis（长上下文 / 事实性 / 知识）
- 🧮 **缺值可解释**：交叉岭回归填补缺失指标，`Imputed` 列标注可信度
- 🎯 **第一梯队精选**：只收国际 + 国内真正可用的前沿模型（约 40 个），不做几百个模型的长尾堆砌
- 🔧 **全参数可调**：权重、模型池、别名映射全部在 [`config.json`](config.json) 与 [`model_registry.json`](scripts/model_registry.json)，无需改代码

## 三个榜单

| 榜单 | 定位 | 核心维度 | 排序依据 |
|---|---|---|---|
| **通用榜 General** | 编程 / 智能体 / 日常混合使用 | 编码 30% / Agent 25% / 指令遵循 15% / 长上下文 10% / 事实 10% / 知识 10% | 综合分 |
| **文本榜 Text** | 写小说、日常问答 | 创意写作 25% / 事实 20% / 指令遵循 20% / 知识 20% / 长上下文 15% | 综合分 |
| **性价比榜 Value** | 真实使用成本下的性价比 | 同通用榜权重 | 综合分 ÷ Effective $/1M |

权重与评分细节见 [METHODOLOGY.md](METHODOLOGY.md)。

## 📊 通用榜 Top 15

> 面向**编程 / 智能体 / 日常混合使用**。

<!--SNAPSHOT_GENERAL_START-->
> 2026-08-13 抓取（41 第一梯队模型 -> 41 行）。
> 填补验证：LiveBench Coding MAE=2.24 (>10%: 5.1%/39) ; DeepSWE MAE=9.01 (>10%: 54.5%/22) ; LiveBench Agentic Coding MAE=3.15 (>10%: 20.5%/39) ; LiveBench Instruction Following MAE=3.78 (>10%: 17.9%/39) ; LCR MAE=0.02 (>10%: 0.0%/34) ; Omniscience Index MAE=6.09 (>10%: 76.5%/34) ; GPQA Diamond MAE=0.01 (>10%: 0.0%/34) ; HLE MAE=0.02 (>10%: 17.6%/34)
<!--SNAPSHOT_GENERAL_END-->

<!--TOP15_GENERAL_START-->
| # | Model | Creator | Score | Imputed |
|---|---|---|---|---|
| 1 | claude-fable-5 | Anthropic | 75.6 | - |
| 2 | gpt-5.6-sol | OpenAI | 73.5 | - |
| 3 | claude-opus-5 | Anthropic | 72.9 | - |
| 4 | kimi-k3 | Moonshot AI | 72.5 | - |
| 5 | gpt-5.5 | OpenAI | 71.5 | - |
| 6 | claude-opus-4.8 | Anthropic | 69.7 | - |
| 7 | gpt-5.6-terra | OpenAI | 68.8 | - |
| 8 | claude-opus-4.7 | Anthropic | 68.3 | DeepSWE(reg) |
| 9 | claude-sonnet-5 | Anthropic | 67.7 | - |
| 10 | muse-spark-1.2 | Meta | 67.7 | LCR(reg), Omniscience Index(reg), GPQA Diamond(reg), HLE(reg) |
| 11 | gpt-5.6-luna | OpenAI | 67.6 | - |
| 12 | qwen3.8-max | Alibaba | 67.5 | LCR(reg), Omniscience Index(reg), GPQA Diamond(reg), HLE(reg) |
| 13 | gpt-5.4 | OpenAI | 66.8 | - |
| 14 | grok-4.6 | xAI | 66.8 | LCR(reg), Omniscience Index(reg), GPQA Diamond(reg), HLE(reg) |
| 15 | muse-spark-1.1 | Meta | 66.8 | - |
<!--TOP15_GENERAL_END-->

👉 [通用榜完整排名（CSV）](results/general_scored.csv)

## 📝 文本榜 Top 15

> 面向**写小说、日常问答**：创意写作 25%、事实性 20%、指令遵循 20%、知识 20%、长上下文 15%。

<!--SNAPSHOT_TEXT_START-->
> 2026-08-13 抓取（41 第一梯队模型 -> 41 行）。
> 填补验证：EQ-Bench Creative Writing MAE=98.10 (>10%: 19.2%/26) ; LiveBench Language MAE=3.54 (>10%: 7.7%/39) ; Omniscience Index MAE=6.09 (>10%: 76.5%/34) ; LiveBench Instruction Following MAE=3.78 (>10%: 17.9%/39) ; GPQA Diamond MAE=0.01 (>10%: 0.0%/34) ; HLE MAE=0.02 (>10%: 17.6%/34) ; LCR MAE=0.02 (>10%: 0.0%/34)
<!--SNAPSHOT_TEXT_END-->

<!--TOP15_TEXT_START-->
| # | Model | Creator | Score | Imputed |
|---|---|---|---|---|
| 1 | claude-fable-5 | Anthropic | 76.0 | - |
| 2 | claude-opus-5 | Anthropic | 74.7 | - |
| 3 | kimi-k3 | Moonshot AI | 74.2 | - |
| 4 | gpt-5.6-sol | OpenAI | 73.7 | - |
| 5 | gpt-5.5 | OpenAI | 71.6 | - |
| 6 | claude-opus-4.8 | Anthropic | 70.9 | - |
| 7 | claude-opus-4.7 | Anthropic | 70.3 | - |
| 8 | gemini-3.1-pro | Google | 69.9 | - |
| 9 | qwen3.8-max | Alibaba | 69.7 | Omniscience Index(reg), GPQA Diamond(reg), HLE(reg), LCR(reg) |
| 10 | gpt-5.4 | OpenAI | 69.2 | - |
| 11 | muse-spark-1.1 | Meta | 69.0 | - |
| 12 | gemini-3.5-flash | Google | 68.8 | EQ-Bench Creative Writing(reg) |
| 13 | gemini-3.6-flash | Google | 68.4 | - |
| 14 | muse-spark-1.2 | Meta | 68.1 | EQ-Bench Creative Writing(reg), Omniscience Index(reg), GPQA Diamond(reg), HLE(reg), LCR(reg) |
| 15 | gpt-5.6-terra | OpenAI | 67.7 | - |
<!--TOP15_TEXT_END-->

👉 [文本榜完整排名（CSV）](results/text_scored.csv)

## 💰 性价比榜 Top 15

> 面向**真实使用成本**：`Value` = 综合分 ÷ `Effective $/1M`（每美元买到多少分）。`Effective $/1M` 在标准单价基础上考虑两个降本因素——**订阅折扣**（Copilot 官方额度折合 ×0.50–0.67；ChatGPT/Claude 等按 SemiAnalysis 实测隐含价值折合）与**分厂商缓存命中率**（主流厂商 90%）。同通用榜权重，仅收录有成本数据的模型。

<!--SNAPSHOT_VALUE_START-->
> 2026-08-13 抓取（41 第一梯队模型 -> 34 行）。
> 填补验证：LiveBench Coding MAE=2.24 (>10%: 5.1%/39) ; DeepSWE MAE=9.01 (>10%: 54.5%/22) ; LiveBench Agentic Coding MAE=3.15 (>10%: 20.5%/39) ; LiveBench Instruction Following MAE=3.78 (>10%: 17.9%/39) ; LCR MAE=0.02 (>10%: 0.0%/34) ; Omniscience Index MAE=6.09 (>10%: 76.5%/34) ; GPQA Diamond MAE=0.01 (>10%: 0.0%/34) ; HLE MAE=0.02 (>10%: 17.6%/34)
<!--SNAPSHOT_VALUE_END-->

<!--TOP15_VALUE_START-->
| # | Model | Creator | Score | $/1M | Effective $/1M | Value | Imputed |
|---|---|---|---|---|---|---|---|
| 1 | minimax-m3 | MiniMax | 56.6 | 0.389 | 0.008 | 7078.21 | DeepSWE(reg) |
| 2 | gpt-5.4-mini | OpenAI | 56.9 | 1.639 | 0.02 | 2844.87 | DeepSWE(reg) |
| 3 | gpt-5.6-luna | OpenAI | 67.6 | 2.265 | 0.029 | 2329.95 | - |
| 4 | gpt-5.2-codex | OpenAI | 66.7 | 4.874 | 0.062 | 1075.61 | DeepSWE(reg) |
| 5 | gpt-5.2 | OpenAI | 63.3 | 4.874 | 0.062 | 1020.77 | DeepSWE(reg) |
| 6 | gpt-5.4 | OpenAI | 66.8 | 5.463 | 0.068 | 982.77 | - |
| 7 | gpt-5.6-terra | OpenAI | 68.8 | 5.664 | 0.073 | 941.82 | - |
| 8 | deepseek-v4-flash | DeepSeek | 61.8 | 0.134 | 0.096 | 643.29 | - |
| 9 | gpt-5.5 | OpenAI | 71.5 | 10.925 | 0.135 | 529.67 | - |
| 10 | claude-sonnet-5 | Anthropic | 67.7 | 5.896 | 0.133 | 509.15 | - |
| 11 | gpt-5.6-sol | OpenAI | 73.5 | 11.328 | 0.145 | 506.88 | - |
| 12 | claude-sonnet-4.6 | Anthropic | 61.2 | 5.896 | 0.133 | 459.87 | - |
| 13 | claude-opus-5 | Anthropic | 72.9 | 9.828 | 0.222 | 328.25 | - |
| 14 | claude-opus-4.8 | Anthropic | 69.7 | 9.828 | 0.222 | 314.09 | - |
| 15 | claude-opus-4.7 | Anthropic | 68.3 | 9.828 | 0.222 | 307.45 | DeepSWE(reg) |
<!--TOP15_VALUE_END-->

👉 [性价比榜完整排名（CSV）](results/value_scored.csv)

> Imputed 列说明：`-` 表示所有评分指标均为真实值；`指标名(reg)` 表示岭回归预测值；`指标名(reg,low)` 表示预测可信度低（训练样本 < 门槛）。

## 怎么算的

**总分 = 指标得分 × 权重**，满分 100 分。模型池为**国际 + 国内第一梯队**（约 40 个模型，见 [`model_registry.json`](scripts/model_registry.json)）。

### 通用榜权重（六维）

| 大类 | 权重 | 指标 |
|---|---|---|
| 编码 Coding | 30% | LiveBench Coding |
| Agent 能力 | 25% | DeepSWE 60% / LiveBench Agentic Coding 40% |
| 指令遵循 | 15% | LiveBench Instruction Following |
| 长上下文 | 10% | LCR |
| 事实准确性 | 10% | Omniscience Index |
| 知识领域 | 10% | GPQA Diamond 60% / HLE 40% |

### 文本榜权重（五维）

| 大类 | 权重 | 指标 |
|---|---|---|
| 创意写作 | 25% | EQ-Bench Creative Writing 70% / LiveBench Language 30% |
| 事实准确性 | 20% | Omniscience Index |
| 指令遵循 | 20% | LiveBench Instruction Following |
| 知识领域 | 20% | GPQA Diamond 60% / HLE 40% |
| 长上下文 | 15% | LCR |

### 关键步骤

- **多源采集**：`fetch_sources.py` 抓取 LiveBench / DeepSWE / SWE-bench / EQ-Bench，`parse_aa.py` 解析 AA
- **跨源合并**：`merge.py` 按 `model_registry.json` 的别名映射，把 5 个源的分数合并成统一宽表
- **固定锚点归一化**：各指标按理论范围（`metric_scales`）缩放到 0-100 分，保留绝对难度（DeepSWE 最高 74% 就是 74 分，不是 100）
- **缺失值填补**：10 个评分指标共享一个交叉岭回归填补池，α=0.1（z-score 空间）
- **权重与参数在 [`config.json`](config.json) 中自定义**，无需修改源码
- **每次运行输出留一验证结果与 R²**——见 [validation_general.json](results/validation_general.json) / [validation_text.json](results/validation_text.json)

[完整方法论 →](METHODOLOGY.md)

## 数据源

| 源 | 维度 | 维护方 | 抗污染 |
|---|---|---|---|
| [LiveBench](https://livebench.ai) | 编码 / Agentic Coding / 指令遵循 / 语言 | Abacus.AI + 学界 | ✅ 半年刷新 |
| [DeepSWE](https://deepswe.datacurve.ai) | 长程软件工程 agent | Datacurve | ✅ 原创任务 |
| [EQ-Bench](https://eqbench.com) | 创意写作 | 独立（LLM-judge） | ⚠️ 主观维度 |
| [Artificial Analysis](https://artificialanalysis.ai) | LCR / Omniscience / GPQA / HLE | 独立评测机构 | ✅ 第三方统一跑分 |

## FAQ

**Q: 为什么模型池只有 40 个左右？**
A: 榜单定位是「前沿可用模型精选」，不是「全量长尾堆砌」。AA 的 1000+ 模型里 90% 是重复变体 / 长尾 / 已弃用，实际被使用的就这几十个。精选池让覆盖率更高、填补更少、分数更「实」。

**Q: 为什么不用 SWE-bench？**
A: SWE-bench Verified 已饱和 + 被前沿厂商弃用（OpenAI 因污染停止报告），其 leaderboard 停留在旧模型（最高 Claude 4.5 Opus / GPT 5.2），对 2026 前沿模型覆盖近乎为零。真实 repo 工程能力由 DeepSWE（抗污染、长程）+ LiveBench Agentic Coding 覆盖。

**Q: 为什么创意写作用 EQ-Bench 这种 LLM-judge？**
A: 写作质量本质是主观偏好，没有客观解。EQ-Bench 是当前最专门的创意写作基准（用 Judgemark 校验裁判与人类偏好相关性），是「主观维度」能做到的最可信折中。

**Q: 填补值可信吗？**
A: 填补值已标注 `(reg)` / `(reg,low)`，且留一验证给出每指标的 MAE。填补只在「部分缺失」时补充，不用于「几乎全缺」的模型（覆盖率门槛保证）。Top 段模型多数无填补。

## 一键复现

```bash
pip install -r requirements.txt
python scripts/build.py
```

离线复算现有缓存（本地测试用）：
```bash
python scripts/build.py --offline
```

## 自动化

由 GitHub Actions 驱动，**每月 1 号**自动抓取、重算排名并推送更新（UTC 6:00 / 北京时间 14:00）。Actions 页面可手动触发。

## 仓库结构

```
├── config.json             # 两榜权重 + 填补参数
├── requirements.txt        # numpy / scikit-learn / pytest
├── METHODOLOGY.md          # 完整方法论
├── scripts/                # 数据流水线
│   ├── build.py            # 一键入口（fetch -> parse -> merge -> score -> README）
│   ├── parse_aa.py         # AA RSC 流 / HTML -> CSV
│   ├── fetch_sources.py    # LiveBench / DeepSWE / SWE-bench / EQ-Bench 抓取
│   ├── merge.py            # 跨源合并成统一宽表
│   ├── score_aa.py         # 评分 CLI
│   ├── model_registry.json # 第一梯队模型池 + 别名映射
│   └── pipeline/           # 评分算法（配置/填补/评分/溯源）
├── results/                # CSV 排名 + validation
├── tests/                  # 单元测试 + e2e
├── .github/workflows/      # 月度更新 + push 时 pytest
└── README.md
```

## 注意事项

- 分数代表在当前第一梯队样本中的相对位置，**非理论能力满分**
- CSV 中 `*` 表示回归预测填补，`**` 表示低可信填补（训练样本 < 门槛）
- 两榜共用同一次抓取、合并与填补，**同一模型两榜分数不可直接互比**（归一化基准不同类）
- 各源模型命名不一致，跨源对齐依赖 [`model_registry.json`](scripts/model_registry.json) 的手动别名映射，新增模型需同步维护
- **原始数据版权归各基准所有**，按原站条款使用

## License

评分脚本与整理结果：MIT License  
原始数据：(c) 各基准维护方，按原站条款使用
