# AI 前沿模型排行

聚合 LiveBench、DeepSWE、EQ-Bench、Artificial Analysis 四个独立评测源的大模型排行榜，从各厂商里挑出旗舰模型做三张榜：通用能力、写作能力、以及把订阅套餐折算成等效单价的性价比对比。价格同时给出美元与人民币（实时汇率），每月随上游数据自动更新。选型场景以 AI 编程为主，兼顾日常问答与写作；模型数量控制在四十多个旗舰，完整名单见下方快照。

## 能力-成本曲线：预算多少，买哪个模型

每个点是一个模型：横轴是实际支付价（最优订阅套餐折算后的等效价，无订阅厂商即官方按量混合价；人民币、对数刻度），纵轴是通用榜综合分。红色阶梯线是最优选择前沿——在横轴上定位你的预算，前沿在该处的高度就是这笔预算能买到的最强模型（例如预算约 ¥0.5/M 时是 gpt-5.6-sol，¥1.5/M 时已是 claude-fable-5）。

<!--FRONTIER_START-->
![能力-成本前沿：给定每 1M token 预算时的最优模型](results/value_frontier.svg)
<!--FRONTIER_END-->

## 这个榜单怎么做

大多数公开榜单要么只看一家的合成指数，要么把几百个长尾模型堆在一起凑数。这里的做法不同：

- 只收国际和国内主流厂商的旗舰（约 40 个）。长尾模型没人用，堆着只会稀释参考价值。
- 四个独立源交叉聚合：LiveBench、DeepSWE、EQ-Bench、Artificial Analysis。单一来源有偏见，交叉验证更可信。
- 固定锚点打分：按指标理论范围换算 0–100 分，不做「样本第一 = 100」的名次分。加新模型不影响已有分数，分数反映真实差距。
- 美元与人民币双币价，汇率每次构建实时抓取。

## 通用榜 Top 15

编程、智能体、日常混合使用看这张。权重：编码 25%、Agent 25%、指令遵循 15%、长上下文 10%、事实 15%、知识 10%。

<!--SNAPSHOT_GENERAL_START-->
> 2026-09-04 抓取（49 精选模型 -> 49 行）。
> 填补验证：DeepSWE MAE=8.52 (>10%: 50.0%/28) ; LiveBench Coding MAE=3.08 (>10%: 6.5%/46) ; AutomationBench MAE=0.09 (>10%: 74.1%/27) ; LiveBench Agentic Coding MAE=3.26 (>10%: 17.4%/46) ; LiveBench Instruction Following MAE=5.20 (>10%: 34.8%/46) ; LCR MAE=0.03 (>10%: 2.0%/49) ; IFBench MAE=0.08 (>10%: 44.0%/25) ; HLE MAE=0.03 (>10%: 22.4%/49) ; SciCode MAE=0.02 (>10%: 10.2%/49) ; LiveBench Reasoning MAE=3.38 (>10%: 4.3%/46) ; Omniscience Index MAE=9.27 (>10%: 87.8%/49)
<!--SNAPSHOT_GENERAL_END-->

<!--TOP15_GENERAL_START-->
| # | Model | Creator | Vision | Score | Imputed |
|---|---|---|---|---|---|
| 1 | claude-fable-5.1 | Anthropic | 👁️ | 68.8 | DeepSWE(reg), BrowseComp(reg), IFBench(reg) |
| 2 | claude-fable-5 | Anthropic | 👁️ | 66.1 | BrowseComp(reg) |
| 3 | claude-opus-5 | Anthropic | 👁️ | 65.5 | IFBench(reg) |
| 4 | gpt-6-astra | OpenAI | 👁️ | 65.2 | LiveBench Coding(reg), BrowseComp(reg), LiveBench Agentic Coding(reg), LiveBench Instruction Following(reg), IFBench(reg), LiveBench Reasoning(reg) |
| 5 | kimi-k3 | Moonshot AI | 👁️ | 62.7 | Terminal-Bench 4.0(reg), IFBench(reg) |
| 6 | gpt-5.6-sol | OpenAI | 👁️ | 62.4 | BrowseComp(reg) |
| 7 | gemini-3.8-flash | Google | 👁️ | 60.2 | BrowseComp(reg), IFBench(reg) |
| 8 | gpt-5.5 | OpenAI | 👁️ | 59.2 | Terminal-Bench 4.0(reg), BrowseComp(reg) |
| 9 | gemini-3.7-flash | Google | 👁️ | 59.1 | BrowseComp(reg), IFBench(reg) |
| 10 | glm-5.3 | Z.AI | - | 57.9 | Terminal-Bench 4.0(reg), AutomationBench(reg), BrowseComp(reg), IFBench(reg) |
| 11 | gpt-5.2-codex | OpenAI | 👁️ | 57.6 | Terminal-Bench 4.0(reg), DeepSWE(reg), AutomationBench(reg), BrowseComp(reg) |
| 12 | grok-4.6 | xAI | 👁️ | 57.4 | Terminal-Bench 4.0(reg), AutomationBench(reg), BrowseComp(reg), IFBench(reg) |
| 13 | claude-opus-4.8 | Anthropic | 👁️ | 56.5 | Terminal-Bench 4.0(reg), BrowseComp(reg) |
| 14 | muse-spark-1.2 | Meta | 👁️ | 55.9 | Terminal-Bench 4.0(reg), AutomationBench(reg), BrowseComp(reg), IFBench(reg) |
| 15 | gpt-5.6-terra | OpenAI | 👁️ | 55.7 | Terminal-Bench 4.0(reg), BrowseComp(reg) |
<!--TOP15_GENERAL_END-->

[完整排名 CSV](results/general_scored.csv)

## 文本榜 Top 15

适用于文学创作、长篇阅读、专业案头分析与日常问答。评测覆盖 5 个维度：创意文学（25%）、专业案头（20%）、指令约束（20%）、事实与长文本（20%）、人际心智（15%），不包含代码生成与数理考试指标。图表纵轴为文本榜综合分，横轴为百万 token 成本，用于按预算选型。

<!--TEXT_FRONTIER_START-->
![文本榜能力-成本前沿：给定每 1M token 预算时的最优写作模型](results/text_frontier.svg)
<!--TEXT_FRONTIER_END-->

<!--SNAPSHOT_TEXT_START-->
> 2026-09-04 抓取（49 精选模型 -> 49 行）。
> 填补验证：EQ-Bench 4 MAE=77.45 (>10%: 22.2%/18) ; LiveBench StoryGen MAE=4.75 (>10%: 26.1%/46) ; LiveBench Language MAE=3.59 (>10%: 6.5%/46) ; GDPval-AA MAE=0.04 (>10%: 35.6%/45) ; AA Briefcase MAE=63.37 (>10%: 25.0%/12) ; LiveBench Summarize MAE=6.50 (>10%: 34.8%/46) ; IFBench MAE=0.08 (>10%: 44.0%/25) ; LiveBench Instruction Following MAE=5.20 (>10%: 34.8%/46) ; LiveBench Simplify MAE=5.83 (>10%: 41.3%/46) ; Omniscience Index MAE=9.27 (>10%: 87.8%/49) ; LCR MAE=0.03 (>10%: 2.0%/49) ; BullshitBench v2 MAE=19.04 (>10%: 85.7%/35) ; LiveBench Theory of Mind MAE=2.36 (>10%: 8.7%/46) ; Harvey LAB MAE=0.03 (>10%: 11.5%/26)
<!--SNAPSHOT_TEXT_END-->

<!--TOP15_TEXT_START-->
| # | Model | Creator | Vision | Score | Imputed |
|---|---|---|---|---|---|
| 1 | claude-fable-5.1 | Anthropic | 👁️ | 76.2 | EQ-Bench 4(reg), IFBench(reg), BullshitBench v2(reg), DeepSearchQA(reg) |
| 2 | kimi-k3 | Moonshot AI | 👁️ | 75.1 | IFBench(reg) |
| 3 | grok-4.6 | xAI | 👁️ | 72.5 | EQ-Bench 4(reg), IFBench(reg), Harvey LAB(reg), DeepSearchQA(reg) |
| 4 | claude-fable-5 | Anthropic | 👁️ | 72.2 | EQ-Bench 4(reg), AA Briefcase(reg), BullshitBench v2(reg), DeepSearchQA(reg) |
| 5 | gpt-5.6-sol | OpenAI | 👁️ | 71.2 | DeepSearchQA(reg) |
| 6 | claude-opus-4.8 | Anthropic | 👁️ | 71.0 | AA Briefcase(reg) |
| 7 | claude-opus-5 | Anthropic | 👁️ | 70.7 | EQ-Bench 4(reg), IFBench(reg) |
| 8 | glm-5.3 | Z.AI | - | 69.7 | EQ-Bench 4(reg), IFBench(reg), Harvey LAB(reg), DeepSearchQA(reg) |
| 9 | gemini-3.7-flash | Google | 👁️ | 69.5 | EQ-Bench 4(reg), AA Briefcase(reg), IFBench(reg), DeepSearchQA(reg) |
| 10 | gemini-3.8-flash | Google | 👁️ | 68.6 | EQ-Bench 4(reg), IFBench(reg), BullshitBench v2(reg), Harvey LAB(reg), DeepSearchQA(reg) |
| 11 | gpt-5.5 | OpenAI | 👁️ | 68.6 | AA Briefcase(reg), DeepSearchQA(reg) |
| 12 | gpt-6-astra | OpenAI | 👁️ | 68.0 | EQ-Bench 4(reg), LiveBench StoryGen(reg), LiveBench Language(reg), LiveBench Summarize(reg), IFBench(reg), LiveBench Instruction Following(reg), LiveBench Simplify(reg), BullshitBench v2(reg), LiveBench Theory of Mind(reg), Harvey LAB(reg), DeepSearchQA(reg) |
| 13 | muse-spark-1.2 | Meta | 👁️ | 67.2 | EQ-Bench 4(reg), AA Briefcase(reg), IFBench(reg), Harvey LAB(reg), DeepSearchQA(reg) |
| 14 | grok-4.5 | xAI | 👁️ | 66.9 | EQ-Bench 4(reg), AA Briefcase(reg), IFBench(reg), DeepSearchQA(reg) |
| 15 | qwen3.8-flash-next | Alibaba | 👁️ | 66.9 | EQ-Bench 4(reg), AA Briefcase(reg), IFBench(reg), BullshitBench v2(reg), Harvey LAB(reg), DeepSearchQA(reg) |
<!--TOP15_TEXT_END-->

[完整排名 CSV](results/text_scored.csv)

## 性价比榜 Top 15

回答「买哪个套餐最划算」。行序跟通用榜一致——按性价比排会让便宜小模型霸榜，没有决策价值。各列含义：API $/1M 是官方按量混合价（含缓存命中假设）；套餐内 $/1M 是该厂商最优订阅折算后的等效价；倍率是每 1 元月费换到的 API 等价额度，70× 即 $1 月费约换 $70 额度；Value = 综合分 ÷ 套餐内 $/1M。套餐名就是官方购买链接，没有订阅制的厂商按 API 按量计费（1×）。

<!--SNAPSHOT_VALUE_START-->
> 2026-09-04 抓取（49 精选模型 -> 49 行）。
> 填补验证：DeepSWE MAE=8.52 (>10%: 50.0%/28) ; LiveBench Coding MAE=3.08 (>10%: 6.5%/46) ; AutomationBench MAE=0.09 (>10%: 74.1%/27) ; LiveBench Agentic Coding MAE=3.26 (>10%: 17.4%/46) ; LiveBench Instruction Following MAE=5.20 (>10%: 34.8%/46) ; LCR MAE=0.03 (>10%: 2.0%/49) ; IFBench MAE=0.08 (>10%: 44.0%/25) ; HLE MAE=0.03 (>10%: 22.4%/49) ; SciCode MAE=0.02 (>10%: 10.2%/49) ; LiveBench Reasoning MAE=3.38 (>10%: 4.3%/46) ; Omniscience Index MAE=9.27 (>10%: 87.8%/49)
<!--SNAPSHOT_VALUE_END-->

<!--TOP15_VALUE_START-->
| # | Model | Creator | Vision | Score | API $/1M | 套餐 | 月费 | 倍率 | 套餐内 $/1M | 套餐内 ¥/1M | Value |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | claude-fable-5.1 | Anthropic | 👁️ | 68.8 | 8.956 | [Claude Max 20x](https://claude.com/pricing) | $200 | 40× | 0.224 | 1.504 | 306.95 |
| 2 | claude-fable-5 | Anthropic | 👁️ | 66.1 | 9.059 | [Claude Max 20x](https://claude.com/pricing) | $200 | 40× | 0.226 | 1.518 | 292.36 |
| 3 | claude-opus-5 | Anthropic | 👁️ | 65.5 | 4.749 | [Claude Max 20x](https://claude.com/pricing) | $200 | 40× | 0.119 | 0.799 | 550.53 |
| 4 | gpt-6-astra | OpenAI | 👁️ | 65.2 | 9.88 | [ChatGPT Pro 20x](https://chatgpt.com/pricing) | $200 | 70× | 0.141 | 0.947 | 462.36 |
| 5 | kimi-k3 | Moonshot AI | 👁️ | 62.7 | 5.469 | [Kimi 会员 Allegretto](https://www.kimi.com/membership/pricing) | $27.6 | 4.5× | 1.203 | 8.079 | 52.12 |
| 6 | gpt-5.6-sol | OpenAI | 👁️ | 62.4 | 3.952 | [ChatGPT Pro 20x](https://chatgpt.com/pricing) | $200 | 70× | 0.057 | 0.383 | 1094.19 |
| 7 | gemini-3.8-flash | Google | 👁️ | 60.2 | 0.741 | [GitHub Copilot Max](https://github.com/features/copilot/plans) | $100 | 2× | 0.37 | 2.485 | 162.63 |
| 8 | gpt-5.5 | OpenAI | 👁️ | 59.2 | 5.69 | [ChatGPT Pro 20x](https://chatgpt.com/pricing) | $200 | 70× | 0.081 | 0.544 | 731.24 |
| 9 | gemini-3.7-flash | Google | 👁️ | 59.1 | 0.741 | [GitHub Copilot Max](https://github.com/features/copilot/plans) | $100 | 2× | 0.37 | 2.485 | 159.69 |
| 10 | glm-5.3 | Z.AI | - | 57.9 | 1.65 | [GLM Coding Plan Max](https://bigmodel.cn/glm-coding) | $149.7 | 34.4× | 0.048 | 0.322 | 1206.1 |
| 11 | gpt-5.2-codex | OpenAI | 👁️ | 57.6 | 2.517 | [ChatGPT Pro 20x](https://chatgpt.com/pricing) | $200 | 70× | 0.036 | 0.242 | 1599.64 |
| 12 | grok-4.6 | xAI | 👁️ | 57.4 | 1.771 | [SuperGrok Heavy](https://x.ai/pricing) | $300 | 5.3× | 0.332 | 2.23 | 172.84 |
| 13 | claude-opus-4.8 | Anthropic | 👁️ | 56.5 | 4.749 | [Claude Max 20x](https://claude.com/pricing) | $200 | 40× | 0.119 | 0.799 | 474.86 |
| 14 | muse-spark-1.2 | Meta | 👁️ | 55.9 | 1.139 | API 按量 | - | 1× | 1.139 | 7.649 | 49.12 |
| 15 | gpt-5.6-terra | OpenAI | 👁️ | 55.7 | 3.133 | [ChatGPT Pro 20x](https://chatgpt.com/pricing) | $200 | 70× | 0.045 | 0.302 | 1238.17 |
<!--TOP15_VALUE_END-->

[完整排名 CSV](results/value_scored.csv)

Imputed 列：`-` 表示全部真实值，`指标(reg)` 是岭回归填补，`指标(reg,low)` 是低可信填补。性价比榜完整 CSV 里还有 `Blended $/1M`（无折扣混合价）和 `Plan Monthly / Multiplier / Discount / URL` 等套餐明细列。

## 套餐购买指南

按订阅维度直接对比「买哪家最值」。每个套餐取它覆盖的厂商里通用榜最强的模型，按「套餐内 Value = 最强模型分 ÷ 该套餐下等效价」从高到低排。这个排法同时反映两件事：套餐能用到多强的模型、折算后到底多便宜，不是单纯比谁额度大。

各列口径：

- 倍率 = 每 1 元月费换到的 API 等价额度；折扣 = 套餐内单价 ÷ 官方单价
- ≈Token/月：官方公布了 token 池的直接引用（MiniMax、GLM、混元、MiMo）；没公布的按「API 等价价值 ÷ 最强模型官方混合价」估算，即额度全部用于该模型时的量，实际用便宜模型能换到更多

数据来源与时点：ChatGPT / Claude 倍率来自 SemiAnalysis 2026-06 实测，Copilot 是 GitHub 官方额度，Grok 为 agentplans.fyi 2026-06 估算，Kimi 为社区实测，国内各家为 2026-08 官方页面实查，聚合与 IDE 类（OpenCode Go、Factory、Trae、Cursor）为 awesome-coding-plan 2026-08 第三方实测。倍率一律按用满额度上限计算，轻度用户实际拿不到这么多。国内套餐标价为人民币，¥/月 按实时汇率折算。

积分制套餐没有倍率。千问 Token Plan 和 WorkBuddy 官方都没公布 Credits 换 token 的系数，社区两套口径相差 5 到 10 倍，给数字等于编数，所以只列官方积分额度；WorkBuddy 的 token 量按社区实测「1 积分 ≈ 4,100 token」折了个大概，仅供参考。

两个例外。Gemini 官方订阅不含 API 额度，不进表，编程需求可以由 GitHub Copilot 覆盖；DeepSeek 没有自有订阅制，由腾讯云 Hy Token Plan Standard 聚合池提供第三方折扣（详见 FAQ）。

<!--PLANS_GUIDE_START-->
| # | 套餐 | 月费 | ¥/月 | 倍率 | 折扣 | ≈Token/月 | 最强模型（通用榜） | 模型分 | 套餐内 $/1M | Value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [MiniMax Max Token Plan](https://platform.minimaxi.com/subscribe/token-plan) | $16.5 | ¥111 | 66.3× | 1.5% | 18亿+ | minimax-m3 (#36) | 47.7 | 0.005 | 10460.1 |
| 2 | [MiniMax Ultra Token Plan](https://platform.minimaxi.com/subscribe/token-plan) | $65.1 | ¥437 | 66.3× | 1.5% | 71亿+ | minimax-m3 (#36) | 47.7 | 0.005 | 10460.1 |
| 3 | [MiniMax Plus Token Plan](https://platform.minimaxi.com/subscribe/token-plan) | $6.8 | ¥46 | 53.7× | 1.9% | 6亿+ | minimax-m3 (#36) | 47.7 | 0.006 | 8491.8 |
| 4 | [GLM Coding Plan Max](https://bigmodel.cn/glm-coding) | $149.7 | ¥1005 | 34.4× | 2.9% | ≈29.3~58.6亿/月 | glm-5.3 (#10) | 57.9 | 0.048 | 1210.0 |
| 5 | [GLM Coding Plan Pro](https://bigmodel.cn/glm-coding) | $74.7 | ¥502 | 29.6× | 3.4% | ≈12.6~25.1亿/月 | glm-5.3 (#10) | 57.9 | 0.056 | 1032.1 |
| 6 | [GLM Coding Plan Lite](https://bigmodel.cn/glm-coding) | $16.4 | ¥110 | 22.4× | 4.5% | ≈2.1~4.2亿/月 | glm-5.3 (#10) | 57.9 | 0.074 | 779.8 |
| 7 | [Hy Token Plan Max](https://cloud.tencent.com/act/pro/tokenplan) | $65 | ¥437 | 1.4× | 73.5% | 6.5亿/月 | hy3 (#41) | 45.5 | 0.098 | 462.0 |
| 8 | [ChatGPT Pro 20x](https://chatgpt.com/pricing) | $200 | ¥1343 | 70× | 1.4% | ≈14亿 | gpt-6-astra (#4) | 65.2 | 0.141 | 461.5 |
| 9 | [Hy Token Plan Pro](https://cloud.tencent.com/act/pro/tokenplan) | $33.06 | ¥222 | 1.3× | 76.0% | 3.2亿/月 | hy3 (#41) | 45.5 | 0.102 | 446.8 |
| 10 | [Hy Token Plan Standard](https://cloud.tencent.com/act/pro/tokenplan) | $10.83 | ¥73 | 1.3× | 79.0% | 1亿/月 | hy3 (#41) | 45.5 | 0.106 | 429.8 |
| 11 | [Hy Token Plan Lite](https://cloud.tencent.com/act/pro/tokenplan) | $3.9 | ¥26 | 1.2× | 81.0% | 3500万/月 | hy3 (#41) | 45.5 | 0.109 | 419.2 |
| 12 | [Claude Max 20x](https://claude.com/pricing) | $200 | ¥1343 | 40× | 2.5% | ≈9亿 | claude-fable-5.1 (#1) | 68.8 | 0.224 | 307.3 |
| 13 | [ChatGPT Pro 5x](https://chatgpt.com/pricing) | $100 | ¥672 | 35× | 2.9% | ≈4亿 | gpt-6-astra (#4) | 65.2 | 0.283 | 230.7 |
| 14 | [ChatGPT Plus](https://chatgpt.com/pricing) | $20 | ¥134 | 35× | 2.9% | ≈0.7亿 | gpt-6-astra (#4) | 65.2 | 0.283 | 230.7 |
| 15 | [MiMo Token Plan Max](https://mimo.mi.com/docs/zh-CN/price/token-plan) | $100 | ¥672 | 1.3× | 79.0% | ≈4.5亿/月 | mimo-v2.5-pro (#39) | 46.8 | 0.221 | 211.6 |
| 16 | [MiMo Token Plan Lite](https://mimo.mi.com/docs/zh-CN/price/token-plan) | $6 | ¥40 | 1.1× | 94.0% | ≈2300万/月 | mimo-v2.5-pro (#39) | 46.8 | 0.263 | 177.8 |
| 17 | [SuperGrok Heavy](https://x.ai/pricing) | $300 | ¥2015 | 5.3× | 18.8% | ≈9亿 | grok-4.6 (#12) | 57.4 | 0.332 | 172.9 |
| 18 | [SuperGrok](https://x.ai/pricing) | $30 | ¥201 | 5.3× | 18.8% | ≈0.9亿 | grok-4.6 (#12) | 57.4 | 0.332 | 172.9 |
| 19 | [Claude Max 5x](https://claude.com/pricing) | $100 | ¥672 | 20× | 5.0% | ≈2亿 | claude-fable-5.1 (#1) | 68.8 | 0.448 | 153.6 |
| 20 | [Claude Pro](https://claude.com/pricing) | $20 | ¥134 | 20× | 5.0% | ≈0.4亿 | claude-fable-5.1 (#1) | 68.8 | 0.448 | 153.6 |
| 21 | [OpenCode Go](https://opencode.ai/go) | $10 | ¥67 | 6× | 16.7% | $60/月（$60 档模型） | kimi-k3 (#5) | 62.7 | 0.913 | 68.7 |
| 22 | [Kimi 会员 Allegretto](https://www.kimi.com/membership/pricing) | $27.6 | ¥185 | 4.5× | 22.0% | ≈0.2亿 | kimi-k3 (#5) | 62.7 | 1.203 | 52.1 |
| 23 | [Kimi Andante](https://www.kimi.com/membership/pricing) | $6.8 | ¥46 | 2.5× | 40.5% | 周4M uncached in/out | kimi-k3 (#5) | 62.7 | 2.215 | 28.3 |
| 24 | [Factory Droid Pro](https://factory.ai) | $20 | ¥134 | 2.4× | 41.7% | 2000万标准token | claude-fable-5.1 (#1) | 68.8 | 3.735 | 18.4 |
| 25 | [GitHub Copilot Max](https://github.com/features/copilot/plans) | $100 | ¥672 | 2× | 50.0% | ≈0.2亿 | claude-fable-5.1 (#1) | 68.8 | 4.478 | 15.4 |
| 26 | [Trae Pro](https://www.trae.ai) | $10 | ¥67 | 2× | 50.0% | $20 基础用量 | claude-fable-5.1 (#1) | 68.8 | 4.478 | 15.4 |
| 27 | [GitHub Copilot Pro+](https://github.com/features/copilot/plans) | $39 | ¥262 | 1.8× | 55.7% | ≈8M | claude-fable-5.1 (#1) | 68.8 | 4.988 | 13.8 |
| 28 | [GitHub Copilot Pro](https://github.com/features/copilot/plans) | $10 | ¥67 | 1.5× | 66.7% | ≈2M | claude-fable-5.1 (#1) | 68.8 | 5.974 | 11.5 |
| | *—— 以下为积分/任务制套餐（官方未公布 Credits→token 换算，不参与倍率排序）——* | | | | | | | | | |
| 29 | [Qwen Token Plan Lite](https://platform.qianwenai.com/pricing/token-plan) | $5.4 | ¥36 | - | - | 2,500 Credits/7天 | qwen3.8-max (#20) | 53.2 | 1.559 | 34.1 |
| 30 | [WorkBuddy 标准版](https://www.workbuddy.cn/docs/workbuddy/Pricing) | $13.8 | ¥93 | - | - | ≈1600万/月 | hy3 (#41) | 45.5 | 0.134 | 339.6 |
| 31 | [Qwen Token Plan Standard](https://platform.qianwenai.com/pricing/token-plan) | $19.3 | ¥130 | - | - | 10,000 Credits/7天 | qwen3.8-max (#20) | 53.2 | 1.559 | 34.1 |
| 32 | [Cursor Pro](https://cursor.com/pricing) | $20 | ¥134 | - | - | $20 API 用量 | claude-fable-5.1 (#1) | 68.8 | 8.956 | 7.7 |
| 33 | [WorkBuddy 高级版](https://www.workbuddy.cn/docs/workbuddy/Pricing) | $27.6 | ¥185 | - | - | ≈3700万/月 | hy3 (#41) | 45.5 | 0.134 | 339.6 |
| 34 | [Qwen Token Plan Pro](https://platform.qianwenai.com/pricing/token-plan) | $69.3 | ¥465 | - | - | 40,000 Credits/7天 | qwen3.8-max (#20) | 53.2 | 1.559 | 34.1 |
| 35 | [WorkBuddy 旗舰版](https://www.workbuddy.cn/docs/workbuddy/Pricing) | $138.8 | ¥932 | - | - | ≈2亿/月 | hy3 (#41) | 45.5 | 0.134 | 339.6 |
<!--PLANS_GUIDE_END-->

---

## 数据源

| 源 | 测什么 | 维护方 | 抗污染 |
|---|---|---|---|
| [LiveBench](https://livebench.ai) | 编码 / Agentic Coding / 指令遵循 / 语言 | Abacus.AI + 学界 | ✅ 半年刷新 |
| [DeepSWE](https://deepswe.datacurve.ai) | 长程软件工程 agent | Datacurve | ✅ 原创任务 |
| [EQ-Bench](https://eqbench.com) | 创意写作 | 独立（LLM-judge） | ⚠️ 主观维度 |
| [Artificial Analysis](https://artificialanalysis.ai) | 长上下文 / 事实性 / 知识 | 独立评测机构 | ✅ 第三方统一跑分 |
| [Frankfurter](https://frankfurter.dev) | USD→CNY 汇率（ECB 官方） | 开源 | — |

## 权重与打分

固定锚点打分：每项指标按理论范围换算到 0–100 分，再按权重加权。

- 通用榜：编码 25%（LiveBench Coding）、Agent 25%（DeepSWE 60% + Agentic Coding 40%）、指令遵循 15%、长上下文 10%（LCR）、事实 15%（Omniscience）、知识 10%（GPQA 30% + HLE 70%）
- 文本榜：创意写作 25%（EQ-Bench 70% + Language 30%）、事实 20%、指令遵循 20%、知识 20%、长上下文 15%
- 性价比榜：与通用榜同权重同名次，展示官方 API 价与最优订阅折算价（含倍率和购买链接），Value = 综合分 ÷ 套餐内 $/1M；配套的套餐购买指南按套餐内性价比排序

[完整方法论](METHODOLOGY.md)

## FAQ

**为什么只收旗舰、不收长尾？**

几百个模型里九成是重复变体、长尾小厂和已弃用条目，真正有人用的就这几十个。榜单定位是精选，不是堆量。

**分数为什么不像别家那么高，连 90 都见不到？**

不做 min-max 名次分。DeepSWE 最好的模型也只有 74%，那就写 74，不硬抬成 100。分数是能力，不是名次。

**为什么不用 SWE-bench？**

SWE-bench Verified 已经饱和，前沿厂商陆续停止报告（OpenAI 因污染问题退出），它的榜单停在旧模型上。真实工程能力由 DeepSWE 和 LiveBench Agentic Coding 覆盖。

**汇率哪来的？**

每次构建实时抓取 Frankfurter（ECB 官方参考价），失败时回退 open.er-api.com，不硬编码。

**想低价用 Claude 或 GPT 写代码，有什么路子？**

两条路：官方高倍率订阅，或国产低折池。Claude Max 20x 用满额度上限约等于 API 打 2.5 折，ChatGPT Pro 对 GPT-5.6 系约 1.4 折；GLM Coding Plan 三档折算折扣在 2.9%~4.5%，OpenCode Go 每月 $10 对部分国产模型给到 $60 月度额度。差别在用谁的模型——前者始终是榜单最前排，后者目前最强 glm-5.3 排第 10。要分数还是要单价，看预算对哪个更敏感。

**DeepSeek 为什么没有推荐套餐？**

DeepSeek 官方只卖 API 按量计费，没有订阅制。榜单给它挂的是腾讯云 Hy Token Plan Standard 聚合池：¥78/月共享 1 亿 token，能跑 DeepSeek-V4 等多家模型，折算约 79% 折扣。这是兜底选项，不如厂商自营订阅划算。

**Kimi 的会员档位怎么选？**

四档月付：Andante ¥49、Moderato ¥99、Allegretto ¥199、Allegro ¥699，年付约合八折，都含 Kimi Code 调用。轻度使用 Andante 够用；当编程主力一般要上到 Allegretto。官方已公告新会员体系将把 Kimi 与 Kimi Code 权益拆分，购买前留意公告。

## 复现

```bash
pip install -r requirements.txt
python scripts/build.py            # 完整构建（抓取 + 合并 + 评分 + README）
python scripts/build.py --offline  # 离线复算缓存
python -m pytest -q                # 测试
```

GitHub Actions 每月 1 号自动更新。

## License

评分脚本与整理结果：MIT。原始数据版权归各基准维护方。
