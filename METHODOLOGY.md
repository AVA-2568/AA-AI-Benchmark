# 评分方法论

> 本文档是 [README](README.md) 中评分方法的完整展开，包含权重推导、归一化细节、特征标准化、缺失值填补算法、留一验证、成本口径公式和 R² 拟合质量。

## 指标选取与权重

本仓库维护**两个榜单**，共用同一次抓取、去重与缺失值填补，仅评分权重不同。

### 通用榜 General

从 Artificial Analysis 的 providers leaderboard 中选取 **9 个代表性基准指标**，归入 4 个大类，每大类再分配子权重：

| 大类（权重） | 指标 | 子权重 | 全局权重 |
|---|---|---|---|
| **智能体 Agentic** (20%) | GDPval-AA | 100% | 20% |
| **编程 Coding** (20%) | Terminal-Bench Hard | 50% | 10% |
| | Terminal-Bench v2.1 | 30% | 6% |
| | SciCode | 20% | 4% |
| **通用 General** (40%) | LCR | 30% | 12% |
| | Omniscience Index | 30% | 12% |
| | IFBench | 40% | 16% |
| **知识 Knowledge** (20%) | GPQA Diamond | 40% | 8% |
| | HLE | 60% | 12% |

全局权重之和 = 1.00。

**设计逻辑**：通用能力（LCR + Omniscience + IFBench）权重最高（40%），因为它代表模型的日常使用体验；编程和智能体各 20%；知识（GPQA + HLE）20%。

### 文本榜 Text

面向**日常对话、查资料、事实问答**场景，选取 6 个纯文本相关指标，归入 3 个大类：

| 大类（权重） | 指标 | 子权重 | 全局权重 |
|---|---|---|---|
| **事实性 Factuality** (40%) | Omniscience Non-Hallucination | 60% | 24% |
| | Omniscience Accuracy | 40% | 16% |
| **交互 Interaction** (35%) | IFBench | 70% | 24.5% |
| | LCR | 30% | 10.5% |
| **知识 Knowledge** (25%) | HLE | 60% | 15% |
| | GPQA Diamond | 40% | 10% |

全局权重之和 = 1.00。

**设计逻辑**：
- **事实性最重（40%）**：查资料场景下"不编造"比"多答对"更致命，故 Non-Hallucination 60% > Accuracy 40%。两列均来自 AA Omniscience 基准的公开拆分（与 Omniscience Index 同源，但拆开后语义正交：一个测幻觉率、一个测答对率），文本榜不再使用合成的 Omniscience Index，避免与拆分列重复计权。
- **交互次之（35%）**：IFBench（指令遵循）是对话体验的核心代理指标，占大头 70%；LCR（长上下文）覆盖长文阅读 / 资料吞吐，占 30%。
- **知识 25%**：HLE 偏综合推理知识（60%），GPQA Diamond 偏科学知识（40%），与通用榜内部比例一致。
- **不含编程 / 智能体指标**：Terminal-Bench、SciCode、GDPval-AA 与文本场景无关，全部剔除。
- **不评创意写作**：AA 没有可靠的公开写作质量基准，写作是主观偏好维度，宁缺毋滥（见 README FAQ）。

> 两榜权重均可在 [`config.json`](config.json) `leaderboards` 中自定义，无需修改源码。

## 数据抓取与解析

AA 已迁移到 Next.js App Router，页面不再内嵌 `__NEXT_DATA__`。流水线采用**三级降级链**：

| 级别 | 方式 | 说明 |
|---|---|---|
| 1（主路径） | 带 `RSC: 1` 头请求同一 URL | 直取 RSC 数据流（~2.4MB 纯数据），`json.JSONDecoder().raw_decode` 标准库解析 |
| 2（回退） | 整页 HTML 的 `__next_f.push` | App Router 流式注水的 JS 字符串，反转义后同法解析 |
| 3（遗留） | `__NEXT_DATA__` script 标签 | Pages Router 时代格式，2026-07 起已不出现，仅保底 |

解析成功后过**数据哨兵**才放行：行数 >800（近期快照 ~1080）、11 个评分字段全池平均非空率 ≥60%（2026-07 实测 87%）、单字段非空率 ≥5%（=0 说明该列已从页面消失）。任一不达标即失败退出，由 CI 开 Issue 告警，避免半残数据静默污染排名。

默认情况下，两次抓取均失败即构建失败；只有显式传入 `--allow-stale` 才允许使用旧缓存，且陈旧输入不会刷新 README。`--offline` 用于明确复算现有缓存，同样标记为 `stale=true`。每次成功构建写入 `results/manifest.json`，记录输入/配置哈希和 stale 状态。

## 数据预处理

### 去重策略

原始榜单包含同一模型在不同推理强度（max / xhigh / high / medium / low）的多条记录，以及同一模型在多个云平台（AWS / Vertex / AI Studio）的重复条目。

- 按 **Model Slug** 去重
- 同一 Slug 有多个条目时，只保留 **Intelligence Index 最高**的那一行
- 保留的各个变体覆盖不同强度级别，你可以根据成本和性能需求选合适的

### 排名截断

评分后按总分降序排列，**仅保留 ≥ 70 分**的模型。相比百分比截断，绝对分数门槛在不同月份间保持可比性——一个模型不会因为池子大小变化而被挤出或挤进榜单。

## 归一化方法

```
归一化得分 = (原始值 - 该指标最小值) / (该指标最大值 - 该指标最小值) × 100
```

- 最小值和最大值来自去重后的全部实测数据
- 结果范围 0–100，代表在该样本中的相对位置，而非理论能力满分
- 若某指标所有模型得分相同（hi == lo），归一化得分统一为 50.0

## 特征标准化（岭回归输入）

> 适用对象：**只用于缺失值填补阶段的岭回归输入 X**，不影响归一化（min-max 0-100）和最终加权求和。

### 为什么需要

交叉预测特征中，`Omniscience Index` 量纲 -12 ~ 100，`Omniscience Accuracy` / `Non-Hallucination` 为 0-100，其余为 0-1。**量纲差 100× → X^TX 病态 → β 估计不稳**。

具体计算：
- 7 个 0-1 特征方差 ~0.05
- Omniscience Index 方差 ~600
- X^TX 对角元比 ~12000（加 α=0.1 后仍 > 5000）
- 教科书经验：条件数 > 1000 即"病态"，β 估计方差显著放大

### 做法

1. **fit 一次**：用全量 raw 真实值（None 用 `stats[m][2]` top50% mean 替换）构造 (n × 11) 矩阵 → 跑 `sklearn.preprocessing.StandardScaler.fit` → 拿到 11 维 mean/scale
2. **最多 100 轮迭代 + LOO + R² log 都用同一个 scaler** —— 不重 fit，避免随填补值漂移
3. **每次 transform 11 列**（含 target_m），然后删 target_m 列 + 加 bias 列 → 10 维标准化特征

```python
def to_X(arr_pool, target_m):
    if scaler is not None:
        arr_pool = scaler.transform(arr_pool)
    target_idx = POOL.index(target_m)
    keep = np.r_[:target_idx, target_idx + 1:N_POOL]
    return np.hstack([np.ones((len(arr_pool), 1)), arr_pool[:, keep]])
```

### α 配套调整

- 旧值 α=1.0（隐式为 Omniscience 量纲补偿）
- 标准化后 α=0.1（z-score 空间统一）
- 在 [`config.json`](config.json) `ridge_alpha` 可调；迭代轮数、相对容差、稳定轮数、阻尼系数和裁剪分位点在 `imputation` 中配置
- 调参依据：看留一验证的 MAE，**目标不是 LOO MAE 最低，而是排名稳定**

### 回退开关

`config.json` 加 `standardize_features` 开关：

```json
"standardize_features": true
```

设 `false` 跳过 fit/transform，行为退回到"原始 X + α=1.0"——**仅供回退用**，不建议长期关闭。

### 实际改善

| 指标 | MAE 旧 | MAE 新 | 改善 | pct>10 旧 | pct>10 新 | 改善 |
|---|---|---|---|---|---|---|
| Terminal-Bench Hard | 0.0347 | 0.0265 | **-23.6%** | 60.0% | 51.1% | -8.9 |
| IFBench | 0.0725 | 0.058 | **-20.0%** | 58.3% | 47.4% | -10.9 |
| HLE | 0.0427 | 0.0307 | **-28.1%** | 75.0% | 73.0% | -2.0 |
| GPQA Diamond | 0.0537 | 0.0473 | -11.9% | 31.7% | 27.2% | -4.5 |
| Terminal-Bench v2.1 | 0.0533 | 0.0475 | -10.9% | 55.0% | 48.0% | -7.0 |
| LCR | 0.0745 | 0.0778 | +4.4% | 51.7% | 47.4% | -4.3 |
| Omniscience Index | 10.75 | 10.93 | +1.7% | 78.3% | 80.2% | +1.9 |
| GDPval-AA | 0.0406 | 0.0396 | -2.5% | 43.3% | 45.4% | +2.1 |
| SciCode | 0.0385 | 0.0359 | -6.8% | 45.0% | 44.7% | -0.3 |

**显著改善**：Terminal-Bench Hard、IFBench、HLE（MAE -20% 以上）  
**持平 / 略升**：LCR、Omniscience Index（Omniscience 因分布跨度大本身难预测，标准化救不了）  
**排名影响**：Top 3 稳定，4-15 互调（4-10 名 ±2 位为常见幅度）

## 缺失值填补

### 为什么会有缺失值

- 并非所有模型都跑过每项基准测试
- 部分新模型刚发布、测试数据尚未覆盖
- 部分服务商未提交特定基准

### 填补池：11 个指标共享

填补在**两榜合并的 11 指标池**上进行一次（9 个通用榜指标 + 文本榜新增的 Omniscience Accuracy / Non-Hallucination），两榜共享填补结果：

- 特征更多 → 交叉预测信息量更大，对两榜都有利
- 同一模型的同一指标在两榜中填补值一致，避免"同数据不同分"的解释成本
- 池成员在 `config.json` `imputation_pool` 中声明，榜单用到的指标必须在池内（启动时校验）

### 填补算法：多变量岭回归 + 迭代收敛

对每个目标指标 `T`，用**池内其他 10 个指标交叉预测**（不含 Intelligence Index，避免循环特征）：

1. 初始化：缺失值用训练集 top50% 均值填充
2. 每轮对每个指标：
   - 提取有真实值的样本作为训练集
   - **先 `scaler.transform` 把 11 列特征标准化**（详见"特征标准化"章节）
   - **删 target 列 + 加 bias 列** 得到 10 维标准化 X
   - 用池内其他 10 个特征做岭回归（**α=0.1**，z-score 空间统一）
   - 预测所有缺失值
   - 裁剪到该指标 P95（防止缺失模型被推到历史最佳分）
   - **阻尼更新**：`cur = 0.5 * cur + 0.5 * pred`（抑制 Omniscience Index / Accuracy / Non-Hallucination 等强相关列互预测时的 ping-pong 振荡）
3. 迭代直至收敛或达到最大 **100** 轮（`MAX_ITERS=100`）

**收敛判据（量程相对）**：每轮计算缺失位上的相对变化
`max_delta = max(|cur - prev| / (hi - lo))`，容差 **`REL_TOL=0.005`（量程的 0.5%）**，**连续 3 轮**满足即收敛。
不用绝对 `max_delta < 0.001`：对量纲约 -85..40 的 Omniscience Index，0.001 仅占量程约 0.0008%，过苛；Omniscience 三列训练 R²≈0.98–0.99 强耦合，迭代谱半径接近 1，收敛尾巴很长。0.5% 量程对应归一分 ≤0.5、加权后对总分影响通常 ≤0.12 分，远小于填补本身的 LOO MAE。

### P95 vs P99 裁剪实验

正式算法继续使用 **P95 裁剪**，不改为 P99。2026-07-28 用同一份去重后 396 行快照做非侵入式实验（`experiments/p99_clip.py`）：P99 同样收敛，但会系统性抬高缺失较多且预测靠近上沿的模型，尤其 Claude Opus 5 / Kimi K3 等条目。通用榜 Top 15 重叠 14/15，但 Top 5 直接重排，Claude Opus 5 (max) 从第 3 升第 1（89.3→92.8）；文本榜 Top 15 也重叠 14/15，Claude Opus 5 (xhigh) 从第 12 升第 6（76.9→80.2）。这说明 P99 不是单纯“放宽上限”，而是在高分区显著改变排序；在缺失填补误差仍较高的前提下，P95 更保守、更适合作为默认。

```
预测值 = beta0 + sum(beta_i × feature_i_std)，beta 由岭回归求解
                  ↑ 10 个标准化特征
         ↑ 裁剪到该列 raw P95
         ↑ 阻尼 0.5 写回 cur
```

### 最小样本门槛

若某指标的有效训练样本 < 50，则**不进行回归填补**，缺失值保留 top50% 均值初始值，并在 Imputed 列标注 `(reg,low)` 提示可信度低。

### 如何识别填补值

- CSV 中 `Imputed` 列标注 `指标名(reg)` 或 `指标名(reg,low)`
- README 排名表中「Imputed」列直接显示

## 留一验证

每次评分运行后，自动对每个指标做留一交叉验证：

1. 对每个有真实值的样本，假装其缺失，用其余样本训练岭回归
2. 预测该样本的值，与真实值比较
3. 报告 MAE（平均绝对误差）和误差 >10% 的样本比例

**全量计算**（无 60 元素采样）：n > 60 也不采样，保证 `n` 字段 = MAE 实际分母。性能开销 ~5 分钟可接受。

**乐观偏差（须知）**：当前 LOO 在**迭代填补写满 `cur` 之后**再跑；构造特征时走 `all_feat_row()`，**其他指标的已填补值会进入特征**，并非全程 raw-only。因此报告的 MAE / >10% 误差率会**略偏乐观**（低估真实填补误差）。解读留一数字时按上界参考，不宜当作严格 OOS 估计。更严谨的 raw-only LOO（缺失特征用 top50 mean）可作为后续硬化项，不改变当前排名算法。

验证结果按榜单拆分写入 `results/validation_general.json` / `results/validation_text.json`（各含该榜使用的指标），并在 README 各榜快照行中以摘要形式展示：

```
> 填补验证：IFBench MAE=0.06 (>10%: 47.4%/331) ; Terminal-Bench Hard MAE=0.03 (>10%: 51.1%/323) ; ...
```

## 模型拟合质量（R²）

用全量训练集拟合后，计算每个指标的训练集 R²（不含 Intelligence Index，仅池内 10→1 交叉预测，且 X 已标准化；下表为 2026-07-28 快照实测）：

| 指标 | 典型 R² | 解读 |
|---|---|---|
| GDPval-AA | ~0.93 | 较可预测 |
| Terminal-Bench Hard | ~0.96 | 较可预测 |
| Terminal-Bench v2.1 | ~0.95 | 较可预测 |
| SciCode | ~0.88 | 较可预测 |
| LCR | ~0.81 | 池内最低，预测值谨慎参考 |
| Omniscience Index | ~0.99 | 与 Acc / Non-Halluc 两列强相关，近乎恒等 |
| IFBench | ~0.83 | 中等可预测（训练 R² 高但 LOO >10% 误差率 ~40%） |
| GPQA Diamond | ~0.88 | 较可预测 |
| HLE | ~0.92 | 较可预测 |
| Omniscience Accuracy | ~0.99 | 与 Index / Non-Halluc 强相关 |
| Omniscience Non-Halluc. | ~0.98 | 与 Index / Acc 强相关 |

> 池扩到 11 列后各指标训练 R² 整体上升，部分来自 Omniscience 三列强相关的"信息重复"——**评估填补可信度请以留一验证（MAE / >10% 误差率）为准**，训练 R² 只反映拟合能力上限。

> R² 值随每次数据更新而浮动，精确值见流水线运行日志。R² 越高，表示该指标的缺失值预测越可信。
>
> 注意：R² 是在 **z-score 空间**的 X 上算的，与"不标准化时"数值上不可直接对比。

## 成本估算

### 成本口径

假设典型 API 调用模式：
- **70% 输入 token + 30% 输出 token** — `cost.input_share` / `cost.output_share`
- **50% 的输入 token 命中提示缓存** — `cost.cache_hit_rate`

### 成本公式

```
Total $/1M = (1 - cache_hit_rate) × input_share × 输入价
            + cache_hit_rate × input_share × 缓存命中价
            + output_share × 输出价
```

- `输入价` / `输出价`：来自服务商在 AA leaderboard 标注的 API 定价
- `缓存命中价`：优先从 leaderboard 的 `cacheHitPrice` 字段读取（多数 provider 没公布）
- **`缓存命中价` 缺失时，按 `config.json` 的 `cost_fallback.cache_hit_multiplier` 回退**，默认 `输入价 × 0.1`。如果场景偏 OpenAI，fallback 可能高估；偏 Anthropic/DeepSeek 则接近实际。
- 单位：USD / 百万 token
- **可调参数**（在 `config.json`）：`input_share` / `output_share` / `cache_hit_rate` / `cost_fallback.cache_hit_multiplier`

### 参考意义

成本估算让你在同分段模型间做性价比取舍。但注意：
- 价格为快照，实际可能变动
- 大客户通常有批发折扣，榜单未体现
- 不同推理强度（max / high / low）的价格差异已在各变体中体现

## 注意事项

1. **非绝对排名**：分数是相对排名，不代表模型的能力绝对值
2. **填补值可信度**：留一验证 MAE 越低的指标填补越可靠；标注 `(reg,low)` 的填补仅供参考
3. **权重可自定义**：权重设计反映了「日常使用 + 编程 + 知识」的平衡，可通过 `config.json` 调整
4. **去重策略影响**：保留 Intelligence Index 最高档意味着排名偏向模型「最优变体」的能力上限
5. **特征独立性**：填补仅用评分指标交叉预测，不含 Intelligence Index，避免循环论证
6. **标准化影响**：标准化让 LOO MAE 改善 10-28%（详见"特征标准化"章节），但 4-10 位排名会有 ±2 位互调。如果某些模型的"Omniscience 极端值"是其排名优势，标准化后会**变弱**——这是预期行为。
