# AI 模型供应商排名 · 自定义加权评分

基于 [Artificial Analysis](https://artificialanalysis.ai/leaderboards/providers) 的 providers leaderboard，按自定义分层权重重算综合能力总分，并给出每 1M token 的成本预估。

<!--SNAPSHOT_START-->
> 数据快照：2026-07-24 抓取（1068 模型×服务商 → 去重 391 → 取前 15% = 59 行）。
<!--SNAPSHOT_END-->

> 本仓库由 GitHub Actions 每周自动抓取最新榜单并重算，无需手动维护。

## 仓库内容

| 文件 | 说明 |
|---|---|
| `aa_providers_scored.xlsx` | 最终评分表（两级分类色带表头 + Rank + 红格标注回归填补值 + 说明 sheet） |
| `aa_providers_scored.csv` | 同上数据的 CSV 版，GitHub 可直接内联渲染为表格 |
| `parse_aa.py` | 抓取并解析 AA leaderboard 原始 HTML → CSV/XLSX |
| `dedup_aa.py` | 按 Model Slug 去重（保留 Intelligence Index 最高档） |
| `score_aa.py` | 分层加权评分 + 多变量岭回归填补 + 成本预估，生成最终 xlsx |
| `说明`(xlsx 内 sheet) | 方法论文档（权重、归一化、填补、成本口径） |

## 评分方法

**总分** = Σ（指标归一分 × 全局权重），范围 0–100。全局权重 = 大类权重 × 该指标子权重。

| 大类（权重） | 指标 | 子权重 | 全局 |
|---|---|---|---|
| 智能体 Agentic (20%) | GDPval-AA | 100% | 20% |
| 编程 Coding (20%) | Terminal-Bench Hard | 50% | 10% |
| | Terminal-Bench v2.1 | 30% | 6% |
| | SciCode | 20% | 4% |
| 通用 General (40%) | LCR | 30% | 12% |
| | Omniscience Index | 30% | 12% |
| | IFBench | 40% | 16% |
| 知识 Knowledge (20%) | GPQA Diamond | 40% | 8% |
| | HLE | 60% | 12% |

- **归一化**：各指标按全量 390 行实测 min/max 线性映射到 0–100（相对当前榜单，非理论满分）。
- **缺失值填补**：表格无值的指标用「多变量岭回归 + 迭代填补」预测（以其余 8 指标 + Intelligence Index 为特征），预测值裁剪到该列 P95。被预测的值在 xlsx 中以**红格**标出，`Imputed` 列标注 `(reg)`。
- **成本口径**：每 1M token = 70% 输入 / 30% 输出，且 50% 输入命中提示缓存。
  `Total $/1M = 0.35×输入价 + 0.35×缓存价 + 0.30×输出价`。

## Top 15（完整 59 行见 CSV / XLSX）

<!--TOP15_START-->
| # | 模型 | 厂商 | 总分 | $/1M | 回归填补项 |
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

## 如何复现

```bash
pip install -r requirements.txt
python build.py         # 一键：抓页 → 解析 → 去重 → 评分 → 导出 → 刷新 README
```

分步：`python parse_aa.py && python dedup_aa.py && python score_aa.py && python export_deliverables.py`

## 自动化更新

由 `.github/workflows/update.yml` 驱动：每周一 UTC 06:00 自动抓取最新榜单、重算并推送提交；也可在仓库 **Actions** 页手动 `Run workflow` 立即触发。

## 注意事项

- 分数为「在当前样本中相对靠前」，不代表理论能力满分。
- 带红格 / `Imputed` 标注的行，其缺失项由回归预测，参考时建议优先看白底行。
- 价格为抓取时快照，随服务商调价变动。

## License

数据 © Artificial Analysis，按原站条款使用；本仓库的评分脚本与整理结果以 MIT 许可发布（按需调整）。
