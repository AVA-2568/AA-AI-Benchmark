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

> **编程 / 智能体 / 日常混合使用** · 编码 30% / Agent 25% / 指令遵循 15% / 长上下文 10% / 事实 10% / 知识 10%

<!--SNAPSHOT_GENERAL_START-->
> 2026-08-14 抓取（41 第一梯队模型 -> 41 行）。
> 填补验证：LiveBench Coding MAE=2.05 (>10%: 0.0%/38) ; DeepSWE MAE=5.67 (>10%: 43.8%/16) ; LiveBench Agentic Coding MAE=4.07 (>10%: 31.6%/38) ; LiveBench Instruction Following MAE=4.22 (>10%: 28.9%/38) ; LCR MAE=0.01 (>10%: 0.0%/34) ; Omniscience Index MAE=5.24 (>10%: 85.3%/34) ; GPQA Diamond MAE=0.01 (>10%: 0.0%/34) ; HLE MAE=0.03 (>10%: 26.5%/34)
<!--SNAPSHOT_GENERAL_END-->

<!--TOP15_GENERAL_START-->
| # | Model | Creator | Score | Imputed |
|---|---|---|---|---|
| 1 | claude-fable-5 | Anthropic | 78.7 | - |
| 2 | claude-opus-5 | Anthropic | 75.7 | - |
| 3 | gpt-5.6-sol | OpenAI | 75.1 | - |
| 4 | kimi-k3 | Moonshot AI | 74.4 | - |
| 5 | gpt-5.5 | OpenAI | 73.1 | - |
| 6 | claude-opus-4.8 | Anthropic | 71.9 | - |
| 7 | claude-opus-4.7 | Anthropic | 70.8 | DeepSWE(reg) |
| 8 | muse-spark-1.2 | Meta | 70.1 | LCR(reg), Omniscience Index(reg), GPQA Diamond(reg), HLE(reg) |
| 9 | qwen3.8-max | Alibaba | 69.7 | LCR(reg), Omniscience Index(reg), GPQA Diamond(reg), HLE(reg) |
| 10 | claude-sonnet-5 | Anthropic | 69.3 | - |
| 11 | gpt-5.4 | OpenAI | 68.8 | DeepSWE(reg) |
| 12 | gemini-3.6-flash | Google | 68.4 | - |
| 13 | gpt-5.6-terra | OpenAI | 68.3 | DeepSWE(reg) |
| 14 | gemini-3.1-pro | Google | 68.2 | DeepSWE(reg) |
| 15 | gpt-5.2-codex | OpenAI | 68.2 | DeepSWE(reg) |
<!--TOP15_GENERAL_END-->

👉 [完整排名 CSV](results/general_scored.csv)

## 📝 文本榜 Top 15

> **写小说 / 日常问答** · 创意写作 25% / 事实 20% / 指令遵循 20% / 知识 20% / 长上下文 15%

<!--SNAPSHOT_TEXT_START-->
> 2026-08-14 抓取（41 第一梯队模型 -> 41 行）。
> 填补验证：EQ-Bench Creative Writing MAE=71.54 (>10%: 7.7%/26) ; LiveBench Language MAE=3.47 (>10%: 7.9%/38) ; Omniscience Index MAE=5.24 (>10%: 85.3%/34) ; LiveBench Instruction Following MAE=4.22 (>10%: 28.9%/38) ; GPQA Diamond MAE=0.01 (>10%: 0.0%/34) ; HLE MAE=0.03 (>10%: 26.5%/34) ; LCR MAE=0.01 (>10%: 0.0%/34)
<!--SNAPSHOT_TEXT_END-->

<!--TOP15_TEXT_START-->
| # | Model | Creator | Score | Imputed |
|---|---|---|---|---|
| 1 | claude-fable-5 | Anthropic | 81.8 | - |
| 2 | claude-opus-5 | Anthropic | 80.1 | - |
| 3 | kimi-k3 | Moonshot AI | 77.8 | - |
| 4 | gpt-5.6-sol | OpenAI | 76.7 | - |
| 5 | muse-spark-1.1 | Meta | 75.7 | - |
| 6 | claude-opus-4.8 | Anthropic | 74.9 | - |
| 7 | gpt-5.5 | OpenAI | 74.6 | - |
| 8 | claude-opus-4.7 | Anthropic | 74.1 | - |
| 9 | gemini-3.1-pro | Google | 74.1 | - |
| 10 | qwen3.8-max | Alibaba | 73.7 | Omniscience Index(reg), GPQA Diamond(reg), HLE(reg), LCR(reg) |
| 11 | muse-spark-1.2 | Meta | 72.8 | EQ-Bench Creative Writing(reg), Omniscience Index(reg), GPQA Diamond(reg), HLE(reg), LCR(reg) |
| 12 | gemini-3.5-flash | Google | 72.4 | EQ-Bench Creative Writing(reg) |
| 13 | gemini-3.6-flash | Google | 72.0 | - |
| 14 | grok-4.5 | xAI | 71.0 | - |
| 15 | gpt-5.4 | OpenAI | 70.5 | - |
<!--TOP15_TEXT_END-->

👉 [完整排名 CSV](results/text_scored.csv)

## 💰 性价比榜 Top 15

> **每美元 / 每人民币买到多少分** · `Value` = 综合分 ÷ Effective $/1M。有效成本含订阅折扣与缓存命中率；人民币价按实时汇率换算（本次 ¥6.741/$）。

<!--SNAPSHOT_VALUE_START-->
> 2026-08-14 抓取（41 第一梯队模型 -> 34 行）。
> 填补验证：LiveBench Coding MAE=2.05 (>10%: 0.0%/38) ; DeepSWE MAE=5.67 (>10%: 43.8%/16) ; LiveBench Agentic Coding MAE=4.07 (>10%: 31.6%/38) ; LiveBench Instruction Following MAE=4.22 (>10%: 28.9%/38) ; LCR MAE=0.01 (>10%: 0.0%/34) ; Omniscience Index MAE=5.24 (>10%: 85.3%/34) ; GPQA Diamond MAE=0.01 (>10%: 0.0%/34) ; HLE MAE=0.03 (>10%: 26.5%/34)
<!--SNAPSHOT_VALUE_END-->

<!--TOP15_VALUE_START-->
| # | Model | Creator | Score | $/1M | Effective $/1M | ¥/1M | Eff ¥/1M | Value | Imputed |
|---|---|---|---|---|---|---|---|---|---|
| 1 | minimax-m3 | MiniMax | 58.9 | 0.389 | 0.008 | 2.622 | 0.054 | 7357.24 | DeepSWE(reg) |
| 2 | gpt-5.4-mini | OpenAI | 57.8 | 1.639 | 0.02 | 11.048 | 0.135 | 2890.37 | DeepSWE(reg) |
| 3 | gpt-5.6-luna | OpenAI | 67.6 | 2.492 | 0.032 | 16.798 | 0.216 | 2113.31 | - |
| 4 | gpt-5.2-codex | OpenAI | 68.2 | 4.874 | 0.062 | 32.855 | 0.418 | 1099.55 | DeepSWE(reg) |
| 5 | gpt-5.2 | OpenAI | 63.5 | 4.874 | 0.062 | 32.855 | 0.418 | 1024.12 | DeepSWE(reg) |
| 6 | gpt-5.4 | OpenAI | 68.8 | 5.463 | 0.068 | 36.825 | 0.458 | 1011.82 | DeepSWE(reg) |
| 7 | gpt-5.6-terra | OpenAI | 68.3 | 6.232 | 0.08 | 42.009 | 0.539 | 853.56 | DeepSWE(reg) |
| 8 | claude-sonnet-5 | Anthropic | 69.3 | 3.931 | 0.089 | 26.498 | 0.6 | 778.63 | - |
| 9 | gpt-5.5 | OpenAI | 73.1 | 10.925 | 0.135 | 73.643 | 0.91 | 541.33 | - |
| 10 | gpt-5.6-sol | OpenAI | 75.1 | 11.328 | 0.145 | 76.36 | 0.977 | 517.94 | - |
| 11 | deepseek-v4-flash | DeepSeek | 63.0 | 0.148 | 0.122 | 0.998 | 0.822 | 515.99 | - |
| 12 | claude-sonnet-4.6 | Anthropic | 64.3 | 5.896 | 0.133 | 39.744 | 0.897 | 483.73 | DeepSWE(reg) |
| 13 | claude-opus-5 | Anthropic | 75.7 | 9.828 | 0.222 | 66.249 | 1.496 | 340.86 | - |
| 14 | claude-opus-4.8 | Anthropic | 71.9 | 9.828 | 0.222 | 66.249 | 1.496 | 323.79 | - |
| 15 | claude-opus-4.7 | Anthropic | 70.8 | 9.828 | 0.222 | 66.249 | 1.496 | 318.89 | DeepSWE(reg) |
<!--TOP15_VALUE_END-->

👉 [完整排名 CSV](results/value_scored.csv)

> **Imputed 列**：`-` = 全部真实值；`指标(reg)` = 岭回归填补；`指标(reg,low)` = 低可信填补。

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

**通用榜**：编码 30%（LiveBench Coding）· Agent 25%（DeepSWE 60% + Agentic Coding 40%）· 指令遵循 15% · 长上下文 10%（LCR）· 事实 10%（Omniscience）· 知识 10%（GPQA 60% + HLE 40%）

**文本榜**：创意写作 25%（EQ-Bench 70% + Language 30%）· 事实 20% · 指令遵循 20% · 知识 20% · 长上下文 15%

**性价比榜**：同通用榜权重，按 `综合分 ÷ Effective $/1M` 排序。

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
