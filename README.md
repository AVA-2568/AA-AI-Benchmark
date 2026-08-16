# 🏆 AI 前沿模型排行

**只排真正可用的第一梯队模型**（约 40 个），数据来自多个公开、抗污染的第三方基准，价格同时给出美元与人民币（实时汇率）。

---

## 为什么是这个榜单

市面上的 AI 榜单大多有两类问题：要么用单一聚合站（如 Artificial Analysis）的合成指数，要么堆几百个长尾模型凑数。这个榜单反着来：

| 设计决策 | 做法 | 解决什么问题 |
|---|---|---|
| **第一梯队精选** | 只收国际 + 国内主流厂商的旗舰（约 40 个） | 长尾模型没人用，堆砌只会稀释榜单 |
| **多源聚合** | LiveBench + DeepSWE + EQ-Bench + AA 四个源 | 单一源有偏见，交叉验证更可信 |
| **固定锚点打分** | 按指标理论范围缩放，不做 min-max 名次分 | min-max 把「第一名=100」虚高，扭曲真实差距 |
| **人民币价格** | USD 价格 × 实时汇率 | 国内用户直接可比 |

---

## 📊 通用榜 Top 15

> **编程 / 智能体 / 日常混合使用** · 编码 25% / Agent 25% / 指令遵循 15% / 长上下文 10% / 事实 15% / 知识 10%

<!--SNAPSHOT_GENERAL_START-->
> 2026-08-16 抓取（42 第一梯队模型 -> 42 行）。
> 填补验证：LiveBench Coding MAE=2.80 (>10%: 5.0%/40) ; DeepSWE MAE=10.45 (>10%: 66.7%/24) ; LiveBench Agentic Coding MAE=3.84 (>10%: 20.0%/40) ; LiveBench Instruction Following MAE=4.27 (>10%: 17.5%/40) ; LCR MAE=0.03 (>10%: 4.9%/41) ; Omniscience Index MAE=9.48 (>10%: 95.1%/41) ; GPQA Diamond MAE=0.01 (>10%: 0.0%/41) ; HLE MAE=0.03 (>10%: 26.8%/41)
<!--SNAPSHOT_GENERAL_END-->

<!--TOP15_GENERAL_START-->
| # | Model | Creator | Score | Imputed |
|---|---|---|---|---|
| 1 | claude-fable-5 | Anthropic | 77.9 | - |
| 2 | claude-opus-5 | Anthropic | 74.8 | - |
| 3 | gpt-5.6-sol | OpenAI | 73.2 | - |
| 4 | gemini-3.7-flash | Google | 72.6 | LCR(reg), Omniscience Index(reg), GPQA Diamond(reg), HLE(reg) |
| 5 | kimi-k3 | Moonshot AI | 72.4 | - |
| 6 | grok-4.6 | xAI | 71.2 | - |
| 7 | gpt-5.5 | OpenAI | 71.1 | - |
| 8 | claude-opus-4.8 | Anthropic | 70.4 | - |
| 9 | muse-spark-1.2 | Meta | 70.3 | - |
| 10 | muse-spark-1.1 | Meta | 69.3 | - |
| 11 | claude-opus-4.7 | Anthropic | 68.5 | DeepSWE(reg) |
| 12 | claude-sonnet-5 | Anthropic | 67.1 | - |
| 13 | gemini-3.6-flash | Google | 66.5 | - |
| 14 | gpt-5.6-terra | OpenAI | 66.5 | - |
| 15 | grok-4.5 | xAI | 66.1 | - |
<!--TOP15_GENERAL_END-->

👉 [完整排名 CSV](results/general_scored.csv)

## 📝 文本榜 Top 15

> **写小说 / 日常问答** · 创意写作 25% / 事实 20% / 指令遵循 20% / 知识 20% / 长上下文 15%

<!--SNAPSHOT_TEXT_START-->
> 2026-08-16 抓取（42 第一梯队模型 -> 42 行）。
> 填补验证：EQ-Bench Creative Writing MAE=111.05 (>10%: 17.2%/29) ; LiveBench Language MAE=3.28 (>10%: 5.0%/40) ; Omniscience Index MAE=9.48 (>10%: 95.1%/41) ; LiveBench Instruction Following MAE=4.27 (>10%: 17.5%/40) ; GPQA Diamond MAE=0.01 (>10%: 0.0%/41) ; HLE MAE=0.03 (>10%: 26.8%/41) ; LCR MAE=0.03 (>10%: 4.9%/41)
<!--SNAPSHOT_TEXT_END-->

<!--TOP15_TEXT_START-->
| # | Model | Creator | Score | Imputed |
|---|---|---|---|---|
| 1 | claude-fable-5 | Anthropic | 77.1 | - |
| 2 | claude-opus-5 | Anthropic | 76.9 | - |
| 3 | kimi-k3 | Moonshot AI | 73.7 | - |
| 4 | gpt-5.6-sol | OpenAI | 71.8 | - |
| 5 | muse-spark-1.1 | Meta | 70.3 | - |
| 6 | muse-spark-1.2 | Meta | 69.6 | EQ-Bench Creative Writing(reg) |
| 7 | claude-opus-4.8 | Anthropic | 68.9 | - |
| 8 | gemini-3.7-flash | Google | 68.6 | Omniscience Index(reg), GPQA Diamond(reg), HLE(reg), LCR(reg) |
| 9 | claude-opus-4.7 | Anthropic | 68.4 | - |
| 10 | gpt-5.5 | OpenAI | 68.3 | - |
| 11 | grok-4.6 | xAI | 67.4 | EQ-Bench Creative Writing(reg) |
| 12 | gemini-3.5-flash | Google | 65.1 | EQ-Bench Creative Writing(reg) |
| 13 | gemini-3.1-pro | Google | 64.6 | - |
| 14 | gpt-5.4 | OpenAI | 64.2 | - |
| 15 | qwen3.8-max | Alibaba | 63.8 | - |
<!--TOP15_TEXT_END-->

👉 [完整排名 CSV](results/text_scored.csv)

## 💰 性价比榜 Top 15

> **买哪个套餐最划算** · 按通用榜名次排序（不按性价比排，避免便宜小模型霸榜）。`API $/1M` = 官方按量混合价（含缓存命中假设）；`套餐内 $/1M` = 该厂商最优订阅套餐折算后的等效价；`倍率` = 每 1 元月费换到的 API 等价额度（如 70× 即 $1 月费 ≈ $70 API 额度）；`Value` = 综合分 ÷ 套餐内 $/1M。套餐名为官方购买直链，无订阅的厂商按 API 按量计费（1×）。

<!--SNAPSHOT_VALUE_START-->
> 2026-08-16 抓取（42 第一梯队模型 -> 42 行）。
> 填补验证：LiveBench Coding MAE=2.80 (>10%: 5.0%/40) ; DeepSWE MAE=10.45 (>10%: 66.7%/24) ; LiveBench Agentic Coding MAE=3.84 (>10%: 20.0%/40) ; LiveBench Instruction Following MAE=4.27 (>10%: 17.5%/40) ; LCR MAE=0.03 (>10%: 4.9%/41) ; Omniscience Index MAE=9.48 (>10%: 95.1%/41) ; GPQA Diamond MAE=0.01 (>10%: 0.0%/41) ; HLE MAE=0.03 (>10%: 26.8%/41)
<!--SNAPSHOT_VALUE_END-->

<!--TOP15_VALUE_START-->
| # | Model | Creator | Score | API $/1M | 套餐 | 月费 | 倍率 | 套餐内 $/1M | 套餐内 ¥/1M | Value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | claude-fable-5 | Anthropic | 77.9 | 9.076 | [Claude Max 20x](https://claude.ai/pricing) | $200 | 40× | 0.227 | 1.53 | 343.23 |
| 2 | claude-opus-5 | Anthropic | 74.8 | 4.749 | [Claude Max 20x](https://claude.ai/pricing) | $200 | 40× | 0.119 | 0.802 | 628.61 |
| 3 | gpt-5.6-sol | OpenAI | 73.2 | 5.69 | [ChatGPT Pro 20x](https://chatgpt.com/#pricing) | $200 | 70× | 0.08 | 0.539 | 914.57 |
| 4 | gemini-3.7-flash | Google | 72.6 |  | API 按量 | - | 1× |  |  |  |
| 5 | kimi-k3 | Moonshot AI | 72.4 | 4.102 | [Kimi 会员 Allegretto](https://www.kimi.com) | $27.6 | 4.5× | 0.902 | 6.08 | 80.31 |
| 6 | grok-4.6 | xAI | 71.2 | 1.771 | [SuperGrok Heavy](https://x.ai/pricing) | $300 | 5.3× | 0.337 | 2.272 | 211.16 |
| 7 | gpt-5.5 | OpenAI | 71.1 | 5.69 | [ChatGPT Pro 20x](https://chatgpt.com/#pricing) | $200 | 70× | 0.08 | 0.539 | 888.35 |
| 8 | claude-opus-4.8 | Anthropic | 70.4 | 4.749 | [Claude Max 20x](https://claude.ai/pricing) | $200 | 40× | 0.119 | 0.802 | 591.84 |
| 9 | muse-spark-1.2 | Meta | 70.3 | 1.139 | API 按量 | - | 1× | 1.139 | 7.678 | 61.75 |
| 10 | muse-spark-1.1 | Meta | 69.3 | 1.139 | API 按量 | - | 1× | 1.139 | 7.678 | 60.85 |
| 11 | claude-opus-4.7 | Anthropic | 68.5 | 4.749 | [Claude Max 20x](https://claude.ai/pricing) | $200 | 40× | 0.119 | 0.802 | 575.28 |
| 12 | claude-sonnet-5 | Anthropic | 67.1 | 1.899 | [Claude Max 20x](https://claude.ai/pricing) | $200 | 40× | 0.047 | 0.317 | 1427.47 |
| 13 | gemini-3.6-flash | Google | 66.5 | 1.482 | [GitHub Copilot Max](https://github.com/features/copilot/plans) | $100 | 2× | 0.741 | 4.995 | 89.79 |
| 14 | gpt-5.6-terra | OpenAI | 66.5 | 3.133 | [ChatGPT Pro 20x](https://chatgpt.com/#pricing) | $200 | 70× | 0.044 | 0.297 | 1510.99 |
| 15 | grok-4.5 | xAI | 66.1 | 1.661 | [SuperGrok Heavy](https://x.ai/pricing) | $300 | 5.3× | 0.316 | 2.13 | 209.19 |
<!--TOP15_VALUE_END-->

👉 [完整排名 CSV](results/value_scored.csv)

> **Imputed 列**：`-` = 全部真实值；`指标(reg)` = 岭回归填补；`指标(reg,low)` = 低可信填补。性价比榜完整 CSV 中另有 `Blended $/1M`（无折扣混合价）、`Plan Monthly / Multiplier / Discount / URL` 等套餐明细列。

## 🛒 套餐购买指南

> **订阅套餐怎么选** · 每个套餐取其覆盖厂商在通用榜上的最强模型，按「套餐内 Value = 最强模型综合分 ÷ 该套餐下等效价」降序——同时反映套餐能用到的模型上限与折算价格。`倍率` = 每 1 元月费换到的 API 等价额度；`折扣` = 套餐内等效单价 ÷ 官方 API 单价；`套餐内 $/1M` = 最强模型在该套餐下的等效混合价。套餐名为官方购买直链（非推广链接）。
>
> 倍率数据来源：SemiAnalysis 2026-06 实测（ChatGPT / Claude）、GitHub 官方额度（Copilot）、agentplans.fyi 2026-06 估算（Grok）、社区实测（Kimi）、MiniMax 官方 token 池。**倍率按用满额度上限估算**，轻量用户实际折扣更少。国内套餐（Kimi ¥199、MiniMax ¥49–469）原价为人民币，¥/月 按实时汇率折算。Gemini 官方订阅（Google AI Pro/Ultra）不含 API 额度，未入表；其模型编程场景可由 GitHub Copilot 覆盖。

<!--PLANS_GUIDE_START-->
| # | 套餐 | 月费 | ¥/月 | 倍率 | 折扣 | 最强模型（通用榜） | 模型分 | 套餐内 $/1M | Value |
|---|---|---|---|---|---|---|---|---|---|
| 1 | [MiniMax Max Token Plan](https://platform.minimaxi.com/subscribe/token-plan) | $16.5 | ¥111 | 53× | 1.9% | minimax-m3 (#35) | 55.1 | 0.005 | 11983.5 |
| 2 | [MiniMax Plus Token Plan](https://platform.minimaxi.com/subscribe/token-plan) | $6.8 | ¥46 | 42.9× | 2.3% | minimax-m3 (#35) | 55.1 | 0.006 | 9899.4 |
| 3 | [MiniMax Ultra Token Plan](https://platform.minimaxi.com/subscribe/token-plan) | $65.1 | ¥439 | 41.1× | 2.4% | minimax-m3 (#35) | 55.1 | 0.006 | 9486.9 |
| 4 | [ChatGPT Pro 20x](https://chatgpt.com/#pricing) | $200 | ¥1348 | 70× | 1.4% | gpt-5.6-sol (#3) | 73.2 | 0.08 | 918.9 |
| 5 | [ChatGPT Plus](https://chatgpt.com/#pricing) | $20 | ¥135 | 35× | 2.9% | gpt-5.6-sol (#3) | 73.2 | 0.165 | 443.6 |
| 6 | [Claude Max 20x](https://claude.ai/pricing) | $200 | ¥1348 | 40× | 2.5% | claude-fable-5 (#1) | 77.9 | 0.227 | 343.3 |
| 7 | [SuperGrok Heavy](https://x.ai/pricing) | $300 | ¥2022 | 5.3× | 19.0% | grok-4.6 (#6) | 71.2 | 0.336 | 211.6 |
| 8 | [SuperGrok](https://x.ai/pricing) | $30 | ¥202 | 5.3× | 19.0% | grok-4.6 (#6) | 71.2 | 0.336 | 211.6 |
| 9 | [Claude Max 5x](https://claude.ai/pricing) | $100 | ¥674 | 20× | 5.0% | claude-fable-5 (#1) | 77.9 | 0.454 | 171.7 |
| 10 | [Claude Pro](https://claude.ai/pricing) | $20 | ¥135 | 20× | 5.0% | claude-fable-5 (#1) | 77.9 | 0.454 | 171.7 |
| 11 | [Kimi 会员 Allegretto](https://www.kimi.com) | $27.6 | ¥186 | 4.5× | 22.0% | kimi-k3 (#5) | 72.4 | 0.902 | 80.2 |
| 12 | [GitHub Copilot Max](https://github.com/features/copilot/plans) | $100 | ¥674 | 2× | 50.0% | claude-fable-5 (#1) | 77.9 | 4.538 | 17.2 |
| 13 | [GitHub Copilot Pro+](https://github.com/features/copilot/plans) | $39 | ¥263 | 1.8× | 55.7% | claude-fable-5 (#1) | 77.9 | 5.055 | 15.4 |
| 14 | [GitHub Copilot Pro](https://github.com/features/copilot/plans) | $10 | ¥67 | 1.5× | 66.7% | claude-fable-5 (#1) | 77.9 | 6.054 | 12.9 |
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

**固定锚点打分**：每项指标按理论范围缩放到 0–100 分（不是「样本最高=100」的名次分），再按权重加权。

**通用榜**：编码 25%（LiveBench Coding）· Agent 25%（DeepSWE 60% + Agentic Coding 40%）· 指令遵循 15% · 长上下文 10%（LCR）· 事实 15%（Omniscience）· 知识 10%（GPQA 30% + HLE 70%）

**文本榜**：创意写作 25%（EQ-Bench 70% + Language 30%）· 事实 20% · 指令遵循 20% · 知识 20% · 长上下文 15%

**性价比榜**：同通用榜权重与名次，展示每个模型官方 API 价与最优订阅套餐折算价（含倍率与购买链接）；`Value = 综合分 ÷ 套餐内 $/1M`。配套「套餐购买指南」按套餐内性价比排序，回答「买哪个订阅最值」。

[完整方法论 →](METHODOLOGY.md)

## FAQ

**Q: 为什么只有 40 个模型？**
A: 榜单定位是「前沿可用模型精选」，不是长尾堆砌。几百个模型里 90% 是重复变体、长尾小厂、已弃用条目，实际被使用的就这几十个。

**Q: 分数为什么不像别的榜单那么高（比如 90+）？**
A: 我们不做 min-max 名次分。DeepSWE 最高只有 74%（说明这基准难），它就是 74 分，不会虚高成 100。分数反映真实能力，不反映「你排第几」。

**Q: 为什么不用 SWE-bench？**
A: SWE-bench Verified 已饱和且被前沿厂商弃用（OpenAI 因污染停止报告），其 leaderboard 停留在旧模型。真实 repo 工程能力由 DeepSWE + LiveBench Agentic Coding 覆盖。

**Q: 汇率怎么来的？**
A: 每次构建实时抓取 Frankfurter（ECB 官方参考汇率），失败回退 open.er-api.com，不硬编码。

## 复现

```bash
pip install -r requirements.txt
python scripts/build.py            # 完整构建（抓取 + 合并 + 评分 + README）
python scripts/build.py --offline  # 离线复算缓存
python -m pytest -q                # 测试
```

GitHub Actions 每月 1 号自动更新。

## License

评分脚本与整理结果：MIT · 原始数据版权归各基准维护方
