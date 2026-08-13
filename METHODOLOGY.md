# 评分方法论

> 本文档是 [README](README.md) 中评分方法的完整展开，包含权重推导、数据源与模型池、归一化细节、特征标准化、缺失值填补算法、留一验证和 R² 拟合质量。

## 数据源与模型池

### 模型池：第一梯队精选

榜单只收录**国际 + 国内第一梯队**模型（当前 41 个），而非全量长尾。模型池定义在 [`scripts/model_registry.json`](scripts/model_registry.json)：

- **国际**：OpenAI（GPT-5.6/5.5/5.4/5.2）、Anthropic（Claude Fable 5 / Opus 5 / Opus 4.x / Sonnet）、Google（Gemini 3.x）、xAI（Grok 4.x）、Meta（Muse Spark）、Thinking Machines（Inkling）
- **国内**：DeepSeek（V4）、Kimi（K3/K2.6/K2.7）、Qwen（3.8/3.7/3.6）、GLM（5.2）、MiniMax（M3）

**为什么是精选而非全量**：AA 的 1000+ 模型里 90% 是重复变体（同一模型不同推理档）、长尾小厂、已弃用条目。精选池让覆盖率更高（核心指标覆盖 34–40/41）、填补更少、分数更「实」。

### 数据源（5 个，全部公开可抓）

| 源 | 提供指标 | 维护方 | 抓取方式 |
|---|---|---|---|
| LiveBench | Coding / Agentic Coding / Instruction Following / Language | Abacus.AI + 学界 | `table_<release>.csv` + `categories_<release>.json` |
| DeepSWE | Pass@1（长程工程 agent） | Datacurve | 静态 HTML |
| EQ-Bench | Creative Writing Elo | 独立 | `creative_writing.js` 内嵌 CSV |
| Artificial Analysis | LCR / Omniscience Index / GPQA Diamond / HLE | 独立评测机构 | RSC 流（三级解析链） |

### 跨源模型名对齐

各源模型命名风格各异（如 LiveBench `claude-opus-4-7-xhigh-effort`、DeepSWE `claude-opus-4.7`、AA `claude-opus-4-7`）。`model_registry.json` 为每个统一 slug 维护各源别名，`merge.py` 按别名合并。**新增模型需同步维护别名映射**。

## 指标选取与权重

本仓库维护**两个榜单**，共用同一次抓取、合并与缺失值填补，仅评分权重不同。

### 通用榜 General（六维）

面向**编程 / 智能体 / 日常混合使用**，选取 8 个指标归入 6 大类：

| 大类（权重） | 指标 | 子权重 | 全局权重 |
|---|---|---|---|
| **编码 Coding** (30%) | LiveBench Coding | 100% | 30% |
| **Agent 能力** (25%) | DeepSWE | 60% | 15% |
| | LiveBench Agentic Coding | 40% | 10% |
| **指令遵循** (15%) | LiveBench Instruction Following | 100% | 15% |
| **长上下文** (10%) | LCR | 100% | 10% |
| **事实准确性** (10%) | Omniscience Index | 100% | 10% |
| **知识领域** (10%) | GPQA Diamond | 60% | 6% |
| | HLE | 40% | 4% |

全局权重之和 = 1.00。

**设计逻辑**：编码（30%）与 Agent（25%）是 vibe coding 场景主菜；指令遵循（15%）是「指哪打哪」的高频体验；长上下文 + 事实（20%）是可靠性双保险；知识（10%）是基础门槛。

### 文本榜 Text（五维）

面向**写小说、日常问答**，选取 7 个指标归入 5 大类：

| 大类（权重） | 指标 | 子权重 | 全局权重 |
|---|---|---|---|
| **创意写作** (25%) | EQ-Bench Creative Writing | 70% | 17.5% |
| | LiveBench Language | 30% | 7.5% |
| **事实准确性** (20%) | Omniscience Index | 100% | 20% |
| **指令遵循** (20%) | LiveBench Instruction Following | 100% | 20% |
| **知识领域** (20%) | GPQA Diamond | 60% | 12% |
| | HLE | 40% | 8% |
| **长上下文** (15%) | LCR | 100% | 15% |

全局权重之和 = 1.00。

**设计逻辑**：创意写作（25%）是「写小说」核心，用 EQ-Bench（LLM-judge，主观维度可做到的最可信折中）+ LiveBench Language；事实性（20%）对应日常问答防幻觉；指令遵循、知识、长上下文覆盖其余对话场景。

> 两榜权重均可在 [`config.json`](config.json) `leaderboards` 中自定义，无需修改源码。

## 数据预处理

### 跨源合并

`merge.py` 读 `model_registry.json` + 各源 CSV，把 5 个源的分数合并成统一宽表（行 = 统一 slug，列 = 10 个指标 + Model/Creator）。LiveBench 别名可为列表（如 `deepseek-v4-pro` 的正式版 `-0813` 与预览版），多个匹配时取分数最高者。缺失值留空，交由评分阶段的岭回归填补。

### 数据哨兵（AA）

AA 解析沿用三级降级链（RSC 流 → `__next_f.push` → `__NEXT_DATA__`）+ 数据哨兵（行数 + 评分字段非空率），不达标即失败退出，避免半残数据静默污染排名。

## 归一化方法（固定锚点缩放）

```
归一化得分 = (原始值 - 锚点下限) / (锚点上限 - 锚点下限) × 100
```

- 锚点是**固定的理论范围**（不是样本动态 min/max），定义在 `config.json` 的 `metric_scales`
- 结果范围 0–100，代表「原始值在理论范围中的位置」，即**真实能力分**而非**名次分**
- 保留绝对难度信息：DeepSWE 最高 74%（基准难）就是 74 分，GPQA 最高 92%（快饱和）就是 92 分，两者不再被同等拍成 100
- 加新模型不影响已有模型的分数（锚点固定，不随样本漂移）

各指标锚点：

| 指标 | 锚点 [lo, hi] | 说明 |
|---|---|---|
| LiveBench 各分类 / DeepSWE | [0, 100] | 已是 0–100 百分比 |
| LCR / GPQA Diamond / HLE | [0, 1] | 0–1 比例，×100 隐含 |
| Omniscience Index | [-100, 100] | AA 指数理论范围 |
| EQ-Bench Creative Writing | [800, 2200] | Elo 合理范围 |

> 与旧版 min-max 的区别：min-max 用「样本最高=100、最低=0」动态锚点，把名次差当能力差（离群值敏感、样本小不稳定、二次归一化抹掉难度）；固定锚点保留绝对难度与稳定性。排名顺序大体一致，但分数刻度与个别相邻名次会变（如 Opus 5 与 Kimi K3 的 0.4 分互换）。

## 特征标准化（岭回归输入）

> 适用对象：**只用于缺失值填补阶段的岭回归输入 X**，不影响归一化（固定锚点 0-100）和最终加权求和。

跨源指标量纲差异大（EQ-Bench Elo 200–2100 vs 其他 0–100），`X^TX` 病态 → β 估计不稳。做法：

1. **fit 一次**：用全量 raw 真实值构造 (n × 10) 矩阵 → `StandardScaler.fit`
2. **最多 100 轮迭代 + LOO + R² 都用同一个 scaler** —— 不重 fit，避免随填补值漂移
3. **每次 transform 10 列**（含 target），删 target 列 + 加 bias 列 → 9 维标准化特征
4. **α=0.1**（z-score 空间统一）

`config.json` 加 `standardize_features` 开关（默认 `true`），设 `false` 退回原始 X + α=1.0。

## 缺失值填补

### 填补池：10 个指标共享

填补在**两榜合并的 10 指标池**上进行一次，两榜共享填补结果。池成员在 `config.json` `imputation_pool` 中声明，榜单用到的指标必须在池内（启动时校验）。

### 填补算法：多变量岭回归 + 迭代收敛

对每个目标指标 `T`，用池内其他 9 个指标交叉预测：

1. 初始化：缺失值用训练集 top50% 均值填充
2. 每轮对每个指标：提取真实值样本训练岭回归 → 预测缺失值 → 裁剪到 P95 → 阻尼更新（`cur = 0.5*cur + 0.5*pred`）
3. 迭代直至收敛或达到最大 100 轮

**收敛判据（量程相对）**：每轮计算缺失位相对变化 `max_delta = max(|cur - prev| / (hi - lo))`，容差 0.5% 量程，连续 3 轮满足即收敛。

### 最小样本门槛

若某指标有效训练样本 < `imputation_min_samples`（当前 10），不回归填补，缺失值保留 top50% 均值，Imputed 列标注 `(reg,low)`。门槛从原 50 降到 10，因为精选池仅 41 个模型。

### 如何识别填补值

- CSV 中 `Imputed` 列标注 `指标名(reg)` 或 `指标名(reg,low)`
- README 排名表中「Imputed」列直接显示

## 留一验证

每次评分运行后，自动对每个指标做留一交叉验证（假装修饰一个真实值，用其余样本训练岭回归预测，报告 MAE 与 >10% 误差比例）。结果按榜单拆分写入 `results/validation_general.json` / `results/validation_text.json`。

**乐观偏差（须知）**：当前 LOO 在迭代填补写满 `cur` 之后运行，其他指标的已填补值会进入特征，故 MAE 略偏乐观（低估真实填补误差）。解读时按上界参考。

## 模型拟合质量（R²）

用全量训练集拟合后，计算每个指标的训练集 R²（z-score 空间）。R² 越高，该指标的缺失值预测越可信。当前（2026-08 快照）各指标 R² 约 0.71–0.93，其中 GPQA Diamond（0.93）与 HLE（0.92）最可预测，LiveBench Instruction Following（0.71）最低——填补可信度请以留一验证 MAE 为准。

## 注意事项

1. **非绝对排名**：分数是相对排名，不代表能力绝对值
2. **填补值可信度**：留一验证 MAE 越低的指标填补越可靠；`(reg,low)` 填补仅供参考
3. **权重可自定义**：权重设计反映「编程 + 智能体 + 日常对话」的平衡，可通过 `config.json` 调整
4. **模型池需维护**：第一梯队模型池与别名映射在 `model_registry.json`，新增模型需同步
5. **特征独立性**：填补仅用评分指标交叉预测，不含任何合成综合分，避免循环论证
