# 🏆 AI Model Provider Rankings - AI 模型供应商综合排名

[![Monthly Update](https://img.shields.io/badge/update-monthly-blue)](https://github.com/AVA-2568/AA-AI-Benchmark/actions)
[![Last data update](https://img.shields.io/github/last-commit/AVA-2568/AA-AI-Benchmark?label=last+data+update&style=flat)](https://github.com/AVA-2568/AA-AI-Benchmark/commits/main)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

基于 [Artificial Analysis](https://artificialanalysis.ai/leaderboards/providers) 公开基准数据，按**自定义权重**重算模型综合能力分（而非沿用 AA 的合成 Intelligence Index），并额外给出**真实使用成本**视角。三个榜单，每月自动更新。

**核心特性**：
- 🎯 **能力评分**：11 个基准指标 × 自定义权重，覆盖编程 / 智能体 / 通用 / 知识 / 对话场景
- 🧮 **缺值可解释**：交叉岭回归填补缺失指标，`Imputed` 列标注可信度
- 💰 **成本双口径**：`$/1M` 纯单价 vs `Effective $/1M` 真实成本（订阅折扣 + 90% 缓存命中）
- 🔧 **全参数可调**：权重、成本假设、订阅计划全部在 [`config.json`](config.json)，无需改代码

## 三个榜单

| 榜单 | 定位 | 核心指标 | 排序依据 |
|---|---|---|---|
| **通用榜 General** | 编程 / 智能体 / 日常混合使用 | Agentic 20% / Coding 20% / General 40% / Knowledge 20% | 综合分 |
| **文本榜 Text** | 日常对话、查资料、事实问答 | Factuality 40% / Interaction 35% / Knowledge 25% | 综合分 |
| **性价比榜 Value** | 真实使用成本下的性价比 | 同通用榜权重 | 综合分 ÷ Effective $/1M |

权重与评分细节见 [METHODOLOGY.md](METHODOLOGY.md)。

## 📊 通用榜 Top 15

> 面向**编程 / 智能体 / 日常混合使用**。表中 `$/1M` 为标准 API 单价（70% 输入 + 30% 输出，50% 缓存命中）。

<!--SNAPSHOT_GENERAL_START-->
> 2026-08-07 抓取（1059 模型 x 服务商 -> 去重 404 -> >=70 分 58 行）。
> 填补验证：GDPval-AA MAE=0.04 (>10%: 44.0%/168) ; Terminal-Bench Hard MAE=0.03 (>10%: 49.1%/322) ; Terminal-Bench v2.1 MAE=0.04 (>10%: 44.0%/166) ; SciCode MAE=0.03 (>10%: 36.8%/391) ; LCR MAE=0.08 (>10%: 44.1%/365) ; Omniscience Index MAE=1.82 (>10%: 29.0%/359) ; IFBench MAE=0.05 (>10%: 38.8%/330) ; GPQA Diamond MAE=0.05 (>10%: 25.3%/392) ; HLE MAE=0.03 (>10%: 66.7%/390)
<!--SNAPSHOT_GENERAL_END-->

<!--TOP15_GENERAL_START-->
| # | Model | Creator | Score | $/1M | Imputed |
|---|---|---|---|---|---|
| 1 | Claude Fable 5 (with fallback) | Anthropic | 91.5 | 48.85 | - |
| 2 | GPT-5.6 Sol (max) | OpenAI | 91.0 | 61.518 | - |
| 3 | Claude Opus 5 (max) | Anthropic | 88.7 | 46.925 | Terminal-Bench Hard(reg), IFBench(reg) |
| 4 | Claude Opus 5 (xhigh) | Anthropic | 88.5 | 39.425 | Terminal-Bench Hard(reg), IFBench(reg) |
| 5 | GPT-5.6 Sol (xhigh) | OpenAI | 88.4 | 46.925 | - |
| 6 | Claude Opus 5 (high) | Anthropic | 87.3 | 31.925 | Terminal-Bench Hard(reg), IFBench(reg) |
| 7 | GPT-5.6 Sol (high) | OpenAI | 86.6 | 37.925 | - |
| 8 | GPT-5.5 (xhigh) | OpenAI | 86.4 | 51.617 | - |
| 9 | Kimi K3 (max) | Kimi | 86.0 | 28.155 | Terminal-Bench Hard(reg), IFBench(reg) |
| 10 | Claude Opus 5 (medium) | Anthropic | 85.8 | 24.425 | Terminal-Bench Hard(reg), IFBench(reg) |
| 11 | Muse Spark 1.2 (xhigh) | Meta | 85.2 | 6.865 | Terminal-Bench Hard(reg), IFBench(reg) |
| 12 | GPT-5.6 Sol (medium) | OpenAI | 84.6 | 28.925 | - |
| 13 | Claude Opus 4.8 (max) | Anthropic | 84.3 | 46.925 | - |
| 14 | GPT-5.5 (high) | OpenAI | 84.2 | 41.718 | - |
| 15 | Muse Spark 1.1 (xhigh) | Meta | 83.8 | 6.865 | Terminal-Bench Hard(reg), IFBench(reg) |
<!--TOP15_GENERAL_END-->

👉 [通用榜完整排名（CSV）](results/aa_general_scored.csv)

## 📝 文本榜 Top 15

> 面向**日常对话、查资料、事实问答**场景：事实性（不幻觉 + 答对）40%、交互（指令遵循 + 长上下文）35%、知识深度 25%。不含编程与智能体指标。

<!--SNAPSHOT_TEXT_START-->
> 2026-08-07 抓取（1059 模型 x 服务商 -> 去重 404 -> >=70 分 35 行）。
> 填补验证：Omniscience Non-Halluc. MAE=0.02 (>10%: 40.7%/359) ; Omniscience Accuracy MAE=0.01 (>10%: 8.6%/359) ; IFBench MAE=0.05 (>10%: 38.8%/330) ; LCR MAE=0.08 (>10%: 44.1%/365) ; HLE MAE=0.03 (>10%: 66.7%/390) ; GPQA Diamond MAE=0.05 (>10%: 25.3%/392)
<!--SNAPSHOT_TEXT_END-->

<!--TOP15_TEXT_START-->
| # | Model | Creator | Score | $/1M | Imputed |
|---|---|---|---|---|---|
| 1 | Gemini 3.1 Pro Preview (AI Studio) | Google | 81.1 | 11.57 | - |
| 2 | Qwen3.7 Max | Alibaba | 80.7 | 7.8 | - |
| 3 | MiniMax-M3 (MXFP8) | MiniMax | 80.2 | 1.206 | - |
| 4 | Grok 4.3 (high) | SpaceXAI | 79.6 | 3.507 | - |
| 5 | Grok 4.3 (medium) | SpaceXAI | 79.4 | 2.757 | - |
| 6 | Muse Spark 1.1 (xhigh) | Meta | 79.4 | 6.865 | IFBench(reg) |
| 7 | Grok 4.20 0309 v2 | SpaceXAI | 78.9 | 2.757 | - |
| 8 | Muse Spark 1.2 (xhigh) | Meta | 78.4 | 6.865 | IFBench(reg) |
| 9 | Grok 4.20 0309 | SpaceXAI | 77.4 | 6.17 | - |
| 10 | Claude Fable 5 (with fallback) | Anthropic | 76.9 | 48.85 | - |
| 11 | MiMo-V2.5-Pro | Xiaomi | 76.7 | 1.124 | - |
| 12 | Claude Opus 4.8 (max) | Anthropic | 76.4 | 46.925 | - |
| 13 | GLM-5.2 (max) | Z AI | 76.0 | 7.87 | - |
| 14 | Gemini 3.5 Flash AI Studio | Google | 75.5 | 8.678 | - |
| 15 | Qwen3.7 Plus | Alibaba | 74.5 | 1.594 | - |
<!--TOP15_TEXT_END-->

👉 [文本榜完整排名（CSV）](results/aa_text_scored.csv)

## 💰 性价比榜 Top 15

> 面向**真实使用成本**：`Value` = 综合分 ÷ `Effective $/1M`（每美元买到多少分）。`Effective $/1M` 在标准单价基础上考虑两个降本因素——**订阅折扣**（Copilot 官方额度折合 ×0.50–0.67；ChatGPT Plus / Claude Pro 等按 SemiAnalysis 实测隐含价值折合 ×0.014–0.05，见 FAQ）与 **90% 缓存命中率**。`AA Cost/Task` 为 AA 官方每任务成本估算（仅部分模型有）。同通用榜权重，仅收录 ≥70 分模型。

<!--SNAPSHOT_VALUE_START-->
<!--SNAPSHOT_VALUE_END-->

<!--TOP15_VALUE_START-->
<!--TOP15_VALUE_END-->

👉 [性价比榜完整排名（CSV）](results/aa_value_scored.csv)

> Imputed 列说明（各榜通用）：`-` 表示所有评分指标均为真实值；`指标名(reg)` 表示岭回归预测值；`指标名(reg,low)` 表示预测可信度低（训练样本 < 50）。

## 怎么算的

**总分 = 指标得分 × 权重**，满分 100 分。三榜均仅收录 ≥70 分的模型（绝对门槛，不随池子大小变化）。

### 通用榜权重

| 大类 | 权重 | 主要指标 |
|---|---|---|
| Agentic - 智能体 | 20% | GDPval-AA |
| Coding - 编程 | 20% | Terminal-Bench Hard / v2.1 / SciCode |
| General - 通用 | 40% | LCR / Omniscience / IFBench |
| Knowledge - 知识 | 20% | GPQA Diamond / HLE |

### 文本榜权重

| 大类 | 权重 | 主要指标 |
|---|---|---|
| Factuality - 事实性 | 40% | Omniscience Non-Hallucination（60%）/ Omniscience Accuracy（40%） |
| Interaction - 交互 | 35% | IFBench（70%）/ LCR（30%） |
| Knowledge - 知识 | 25% | HLE（60%）/ GPQA Diamond（40%） |

### 关键步骤

- **min-max 归一化**：各指标按全量样本缩放到 0-100 分
- **缺失值填补**：11 个评分指标共享一个交叉岭回归填补池，α=0.1（z-score 空间）
- **特征标准化**：岭回归输入先 z-score 处理，避免大量纲指标主导——见 [METHODOLOGY 特征标准化](METHODOLOGY.md#特征标准化岭回归输入)
- **成本估算（标准口径 `$/1M`）**：70% 输入 + 30% 输出，50% 输入 token 命中缓存；缓存命中价缺失时按 input 价的 0.1× 回退
- **成本估算（真实口径 `Effective $/1M`）**：主流厂商按 **90% 缓存命中率**（`provider_cache_rates`）+ 真实缓存命中价（缺失按同厂商均值回退），再乘订阅计划折扣（`plans`：Copilot 官方额度 ×0.50–0.67；ChatGPT Plus / Claude Pro 等社区实测隐含价值 ×0.014–0.05）
- **权重与参数在 [`config.json`](config.json) 中自定义**，无需修改源码
- **每次运行输出留一验证结果与 R²**——见 [validation_general.json](results/validation_general.json) / [validation_text.json](results/validation_text.json) / [validation_value.json](results/validation_value.json)

[完整方法论 →](METHODOLOGY.md)

## FAQ

**Q: 文本榜为什么不评"写小说 / 创意写作"？**
A: AA 的公开基准里没有可靠的创意写作评测（写作质量本质是主观偏好，AA 未提供该维度数据）。与其用不相关指标伪装成"写作分"，不如明确不评。需要写作能力参考请结合人工盲测类榜单自行判断。

**Q: 文本榜的 IFBench 分数可信吗？**
A: IFBench 是文本榜权重最大的单一指标（24.5%），且填补可靠性中等（留一验证误差 >10% 的样本约 40%，精确值见各榜快照行）。真实值没问题；但标注 `IFBench(reg)` 的填补值请谨慎对待。Top 段模型 IFBench 实测覆盖率 ~77%，多数头部模型无需填补。

**Q: 为什么高 Non-Hallucination、低 Accuracy 也能排很前？**
A: 文本榜事实性 40% 内 **Non-Halluc 60% > Acc 40%**——设计目标是「查资料时少胡说」优先于「答对得多」。高 NonHalluc + 低 Acc 通常表示**更爱拒答 / 少编造**，**不代表更博学**，也**不是写作榜**。例如 Top 段可能出现 NonHalluc 很高而 Acc 偏低仍进前几名；若你更看重「答对率」，应自行调高 Accuracy 子权重或改读 Accuracy 单列。

**Q: 缓存命中率为什么设 90%？真实命中率是多少？**
A: AA 不公布命中率——它取决于你的使用模式（prompt 可缓存前缀占比、复用频率），不是模型属性。2026 年 prompt caching 已成主流厂商标配，agentic / 长上下文 / 重复前缀工作负载下实测普遍可达 ~90%（DeepSeek 官方定价页即按 90% 命中估算有效费率）。榜单对 Anthropic / OpenAI / Google / DeepSeek 统一按 0.90，其余中小厂商按 0.30 保守假设；认为不符合你的场景可在 `config.json` 的 `provider_cache_rates` 调整后重新构建。

**Q: 订阅折扣怎么算的？ChatGPT / Claude 订阅不是不含 API 额度吗？**
A: 两类口径：① **官方额度制**（GitHub Copilot）——月费买到等值 API 用量（$10/$39/$100 → $15/$70/$200），折扣确定（×0.667/×0.557/×0.50）；② **社区实测隐含价值**——OpenAI/Anthropic 订阅虽不含 API 额度，但**跑满每周限额**时按 API 牌价折算价值远超月费：SemiAnalysis（2026-06）实测 ChatGPT Plus $20 ≈ $700（35x）、Claude Pro $20 ≈ $400（20x）、ChatGPT Pro 20x $200 ≈ $14,000（70x）。榜单按 `monthly ÷ 隐含价值` 折合单价系数，多个计划命中取最低折扣。**注意**：② 类是用满额度上限（重度订阅用户）的成本下界，普通用户达不到；且行业正收窄该窗口（Anthropic 2026-06 起 agent 调用移出订阅池）。不符你的使用强度可在 `config.json` 调整。

**Q: 旧文件 `aa_providers_scored.csv` / `validation.json` 去哪了？**
A: 三榜改版后已更名：`aa_providers_scored.csv` → [`aa_general_scored.csv`](results/aa_general_scored.csv)，`validation.json` → [`validation_general.json`](results/validation_general.json)。通用榜口径与权重不变，仅文件名变化；外部引用请更新链接。

## 一键复现

```bash
pip install -r requirements.txt
python scripts/build.py
```

## 自动化

由 GitHub Actions 驱动，**每月 1 号**自动抓取、重算排名并推送更新（UTC 6:00 / 北京时间 14:00）。Actions 页面可手动触发。流水线**首次 attempt 失败**时用 `dacbd/create-issue-action` 开 Issue；**同一次 run 的 retry 不会重复开**，但**跨月 / 跨 run 无 title 去重**（每月失败仍可能各开一条）。

## 仓库结构

```
├── config.json             # 三榜权重、成本口径、订阅计划与评分参数
├── requirements.txt        # numpy / scikit-learn / pytest
├── METHODOLOGY.md          # 完整方法论
├── scripts/                # 数据流水线
│   ├── build.py            # 一键入口（fetch -> parse -> dedup -> score -> README）
│   ├── parse_aa.py         # AA RSC 流 / HTML -> CSV（三级解析链 + 数据哨兵）
│   ├── dedup_aa.py         # Model Slug 去重
│   └── score_aa.py         # 标准化 + 共享岭回归填补 + 评分
├── results/                # CSV 排名 + validation
│   ├── aa_general_scored.csv     # 通用榜
│   ├── aa_text_scored.csv        # 文本榜
│   ├── aa_value_scored.csv       # 性价比榜（真实成本视角）
│   ├── validation_general.json   # 通用榜留一验证
│   ├── validation_text.json      # 文本榜留一验证
│   └── validation_value.json     # 性价比榜留一验证
├── tests/                  # 单元测试（helpers / config / marker）
├── .github/workflows/      # 月度更新 + push 时 pytest
└── README.md
```

## 注意事项

- 分数代表在当前样本中相对靠前，**非理论能力满分**
- CSV 中 `*` 表示回归预测填补，`**` 表示低可信填补（训练样本 < 50）
- 文本榜与通用榜共用同一次抓取、去重与填补，**同一模型两榜分数不可直接互比**（归一化基准不同类）
- 性价比榜的 `Effective $/1M` 依赖**订阅折扣与缓存命中率假设**（非 AA 公布字段）：Copilot 折扣按现行额度折算，命中率按厂商使用模式设定——均可在 `config.json` 调整
- **价格是抓取时快照**，随服务商调价变动
- **原始数据版权归 Artificial Analysis 所有**，按原站条款使用
- 排名每月刷新；标准化 / α / 阈值变更可能引入 4-10 位的 ±2 互调

## License

评分脚本与整理结果：MIT License  
原始数据：(c) Artificial Analysis，按原站条款使用
