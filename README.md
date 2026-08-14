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
> 2026-08-14 抓取（42 第一梯队模型 -> 42 行）。
> 填补验证：LiveBench Coding MAE=2.82 (>10%: 2.5%/40) ; DeepSWE MAE=10.44 (>10%: 62.5%/24) ; LiveBench Agentic Coding MAE=3.86 (>10%: 20.0%/40) ; LiveBench Instruction Following MAE=4.24 (>10%: 17.5%/40) ; LCR MAE=0.03 (>10%: 4.8%/42) ; Omniscience Index MAE=9.28 (>10%: 92.9%/42) ; GPQA Diamond MAE=0.01 (>10%: 0.0%/42) ; HLE MAE=0.03 (>10%: 26.2%/42)
<!--SNAPSHOT_GENERAL_END-->

<!--TOP15_GENERAL_START-->
| # | Model | Creator | Score | Imputed |
|---|---|---|---|---|
| 1 | claude-fable-5 | Anthropic | 77.9 | - |
| 2 | claude-opus-5 | Anthropic | 74.8 | - |
| 3 | gpt-5.6-sol | OpenAI | 73.2 | - |
| 4 | gemini-3.7-flash | Google | 72.9 | - |
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
> 2026-08-14 抓取（42 第一梯队模型 -> 42 行）。
> 填补验证：EQ-Bench Creative Writing MAE=111.65 (>10%: 17.2%/29) ; LiveBench Language MAE=3.26 (>10%: 5.0%/40) ; Omniscience Index MAE=9.28 (>10%: 92.9%/42) ; LiveBench Instruction Following MAE=4.24 (>10%: 17.5%/40) ; GPQA Diamond MAE=0.01 (>10%: 0.0%/42) ; HLE MAE=0.03 (>10%: 26.2%/42) ; LCR MAE=0.03 (>10%: 4.8%/42)
<!--SNAPSHOT_TEXT_END-->

<!--TOP15_TEXT_START-->
| # | Model | Creator | Score | Imputed |
|---|---|---|---|---|
| 1 | claude-fable-5 | Anthropic | 77.1 | - |
| 2 | claude-opus-5 | Anthropic | 76.9 | - |
| 3 | kimi-k3 | Moonshot AI | 73.7 | - |
| 4 | gpt-5.6-sol | OpenAI | 71.8 | - |
| 5 | muse-spark-1.1 | Meta | 70.3 | - |
| 6 | muse-spark-1.2 | Meta | 69.4 | EQ-Bench Creative Writing(reg) |
| 7 | gemini-3.7-flash | Google | 69.1 | - |
| 8 | claude-opus-4.8 | Anthropic | 68.9 | - |
| 9 | claude-opus-4.7 | Anthropic | 68.4 | - |
| 10 | gpt-5.5 | OpenAI | 68.3 | - |
| 11 | grok-4.6 | xAI | 67.6 | EQ-Bench Creative Writing(reg) |
| 12 | gemini-3.5-flash | Google | 65.1 | EQ-Bench Creative Writing(reg) |
| 13 | gemini-3.1-pro | Google | 64.6 | - |
| 14 | gpt-5.4 | OpenAI | 64.2 | - |
| 15 | qwen3.8-max | Alibaba | 63.8 | - |
<!--TOP15_TEXT_END-->

👉 [完整排名 CSV](results/text_scored.csv)

## 💰 性价比榜 Top 15

> **每美元 / 每人民币买到多少分** · `Value` = 综合分 ÷ Effective $/1M。有效成本含订阅折扣与缓存命中率；人民币价按实时汇率换算（本次 ¥6.741/$）。

<!--SNAPSHOT_VALUE_START-->
> 2026-08-14 抓取（42 第一梯队模型 -> 42 行）。
> 填补验证：LiveBench Coding MAE=2.82 (>10%: 2.5%/40) ; DeepSWE MAE=10.44 (>10%: 62.5%/24) ; LiveBench Agentic Coding MAE=3.86 (>10%: 20.0%/40) ; LiveBench Instruction Following MAE=4.24 (>10%: 17.5%/40) ; LCR MAE=0.03 (>10%: 4.8%/42) ; Omniscience Index MAE=9.28 (>10%: 92.9%/42) ; GPQA Diamond MAE=0.01 (>10%: 0.0%/42) ; HLE MAE=0.03 (>10%: 26.2%/42)
<!--SNAPSHOT_VALUE_END-->

<!--TOP15_VALUE_START-->
| # | Model | Creator | Score | $/1M | Effective $/1M | ¥/1M | Eff ¥/1M | Value | Imputed |
|---|---|---|---|---|---|---|---|---|---|
| 1 | gpt-5.4-nano | OpenAI | 49.1 | 0.452 | 0.006 | 3.047 | 0.04 | 8176.79 | DeepSWE(reg) |
| 2 | minimax-m3 | MiniMax | 55.4 | 0.389 | 0.007 | 2.622 | 0.047 | 7915.66 | DeepSWE(reg) |
| 3 | gpt-5.4-mini | OpenAI | 51.5 | 1.639 | 0.021 | 11.048 | 0.142 | 2454.76 | DeepSWE(reg) |
| 4 | gpt-5.6-luna | OpenAI | 63.9 | 2.492 | 0.033 | 16.798 | 0.222 | 1936.9 | - |
| 5 | gpt-5.2-codex | OpenAI | 64.4 | 4.874 | 0.064 | 32.855 | 0.431 | 1006.56 | DeepSWE(reg) |
| 6 | gpt-5.2 | OpenAI | 60.8 | 4.874 | 0.064 | 32.855 | 0.431 | 950.62 | DeepSWE(reg) |
| 7 | gpt-5.4 | OpenAI | 65.0 | 5.463 | 0.07 | 36.826 | 0.472 | 929.17 | - |
| 8 | gpt-5.6-terra | OpenAI | 66.5 | 6.232 | 0.082 | 42.009 | 0.553 | 810.78 | - |
| 9 | claude-sonnet-5 | Anthropic | 67.1 | 3.931 | 0.09 | 26.498 | 0.607 | 745.46 | - |
| 10 | gpt-5.5 | OpenAI | 71.1 | 10.925 | 0.14 | 73.644 | 0.944 | 507.63 | - |
| 11 | gpt-5.6-sol | OpenAI | 73.2 | 11.328 | 0.149 | 76.361 | 1.004 | 491.04 | - |
| 12 | deepseek-v4-flash | DeepSeek | 59.4 | 0.148 | 0.123 | 0.998 | 0.829 | 483.08 | - |
| 13 | claude-sonnet-4.6 | Anthropic | 59.8 | 5.896 | 0.135 | 39.744 | 0.91 | 442.77 | - |
| 14 | claude-opus-5 | Anthropic | 74.8 | 9.828 | 0.225 | 66.25 | 1.517 | 332.46 | - |
| 15 | claude-opus-4.8 | Anthropic | 70.4 | 9.828 | 0.225 | 66.25 | 1.517 | 313.02 | - |
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

**通用榜**：编码 25%（LiveBench Coding）· Agent 25%（DeepSWE 60% + Agentic Coding 40%）· 指令遵循 15% · 长上下文 10%（LCR）· 事实 15%（Omniscience）· 知识 10%（GPQA 30% + HLE 70%）

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
