# 评分方法论

> 本文档是 [README](README.md) 中评分方法的完整展开，包含权重推导、数据源与模型池、归一化细节、特征标准化、缺失值填补算法、留一验证和 R² 拟合质量。

## 数据源与模型池

### 模型池：主流旗舰精选

榜单只收录**国际 + 国内主流厂商旗舰**模型（当前 41 个），而非全量长尾。模型池定义在 [`scripts/model_registry.json`](scripts/model_registry.json)：

- **国际**：OpenAI（GPT-5.6/5.5/5.4/5.2）、Anthropic（Claude Fable 5 / Opus 5 / Opus 4.x / Sonnet）、Google（Gemini 3.x）、xAI（Grok 4.x）、Meta（Muse Spark）、Thinking Machines（Inkling）
- **国内**：DeepSeek（V4）、Kimi（K3/K2.6/K2.7）、Qwen（3.8/3.7/3.6）、GLM（5.2）、MiniMax（M3）

**为什么是精选而非全量**：AA 的 1000+ 模型里 90% 是重复变体（同一模型不同推理档）、长尾小厂、已弃用条目。精选池让覆盖率更高（核心指标覆盖 34–40/41）、填补更少、分数更「实」。

### 数据源（6 个，全部公开可抓）

| 源 | 提供指标 | 维护方 | 抓取方式 |
|---|---|---|---|
| LiveBench | Coding / Agentic Coding / Instruction Following / Language | Abacus.AI + 学界 | `table_<release>.csv` + `categories_<release>.json` |
| DeepSWE | Pass@1（长程工程 agent） | Datacurve | `/artifacts/v1.1/leaderboard-live.json`（JSON API，每模型取最高 pass_rate 档） |
| EQ-Bench | Creative Writing Elo | 独立 | `creative_writing.js` 内嵌 CSV |
| Artificial Analysis | LCR / Omniscience Index / GPQA Diamond / HLE | 独立评测机构 | RSC 流（三级解析链） |
| Frankfurter | USD→CNY 汇率（ECB 官方） | 开源 | v2 rates API（备源 open.er-api.com） |

### 人民币价格

性价比榜同时输出美元与人民币价格：`Total ¥/1M` / `Effective ¥/1M` = 对应美元价 × 实时 USD→CNY 汇率。汇率每次构建实时抓取（Frankfurter 主、open.er-api 备），写入 `scripts/.cache/fx.json`，不硬编码。

### 订阅套餐与倍率

官方订阅套餐定义在 `config.json` 的 `plans` 表（每条含 `creator_match` / `monthly` / `implied_value` 或 `credit_value` / `discount` / `url`）。两种价值基准：

- **`credit_value`**：官方随附的 API 额度（如 GitHub Copilot——月费直接买到等额 API 美元）
- **`implied_value`**：社区实测的订阅额度上限 API 等价（如 SemiAnalysis 2026-06 对 ChatGPT/Claude 各档跑满上限的实测）

三个派生量：

- **折扣 `discount` = monthly ÷ value**：乘在无折扣混合价上得到套餐内等效价
- **倍率 `multiplier` = value ÷ monthly**：每 1 元月费换到的 API 等价额度（如 ChatGPT Pro 20x = 70×）。从 value/monthly 直接计算而非 1/discount，避免 3 位小数折扣反算的舍入误差（0.014 → 71×，实际 70×）
- **`Blended $/1M`**：无折扣的 per-creator 缓存混合价（`Effective $/1M` = Blended × discount 的基准），用于在任意套餐下重算等效价

**≈Token/月（套餐购买指南列）**：优先用官方公布的 token 池（`plans[].tokens`，如 MiniMax 6 亿/18 亿/55 亿）；其余按 `API 等价价值 ÷ 最强模型官方混合价（Blended $/1M）` 折算——即把额度全部用于该最强模型时的 token 量级，实际使用便宜模型可换到更多。

**三类套餐**（`plans` 表）：

1. **implied_value 型**：订阅额度上限的 API 等价（SemiAnalysis 实测 ChatGPT/Claude 等）
2. **token 池型**：官方公布月 token 额度 × 榜单该厂商最强模型混合价折成 implied_value（MiniMax / GLM / 混元 / MiMo，折算口径随构建快照人工更新）
3. **Credit/积分计量型**（`discount = 1.0`，无 implied_value）：千问 Token Plan、WorkBuddy——官方未公布可靠的 Credits→token 系数，无法折算 API 等价倍率；`_plan_for` 跳过 `discount >= 1` 的套餐，它们只出现在套餐购买指南，不参与每模型的成本折算（主表对这类厂商按 API 按量展示）。token 量尽量给估算：WorkBuddy 按官方实得积分 × 社区实测（1 积分 ≈ 4,100 token）；千问社区口径分歧 5~10 倍，仅列官方积分额

国内套餐人民币月费按固定口径 ÷7.2 折算为 USD（与构建时汇率独立，避免历史数据漂移）。

**倍率按用满额度上限估算**——轻量用户实际折扣更少；无订阅套餐的厂商（DeepSeek / Qwen / GLM 等）按 API 按量计费（倍率 1×）。`url` 为官方购买直链（展示用，构建不请求）。

### 跨源模型名对齐

各源模型命名风格各异（如 LiveBench `claude-opus-4-7-xhigh-effort`、DeepSWE `claude-opus-4.7`、AA `claude-opus-4-7`）。`model_registry.json` 为每个统一 slug 维护各源别名，`merge.py` 按别名合并。**新增模型需同步维护别名映射**。

### 新模型自动发现与别名漏配检测

`merge.py` 以 `model_registry.json` 为白名单，registry 维护不当会静默丢数据。`detect_new_models.py` 在每次构建时做两类检测，结果写入 `results/new_model_candidates.json` 并打印告警：

1. **新模型**：源里出现、registry 完全没有收录的模型。只扫 LiveBench + DeepSWE 两个「前沿模型评测源」（命名规范、几乎无长尾噪音）；EQ-Bench / SWE-bench / AA 因含大量 open-weights 长尾与旧模型不纳入。
2. **别名漏配**：registry 已收录但某源字段为 null，而该源里存在「规范化 slug」（点/连字符互换）对应的数据 —— 数据其实有，只是别名没配。这类检测覆盖 aa / eqbench / deepswe / livebench 四源，用 registry slug 做确定性反向匹配，无长尾噪音问题。

- **只发现、不自动改 registry**：入选筛选与别名确认是人工判断，候选经人工确认后补录 `model_registry.json`。
- **发现候选不视为构建失败**：新模型上线是正常事件，不应阻塞榜单刷新。

## 指标选取与权重

本仓库维护**三个榜单**（通用榜 / 文本榜 / 性价比榜），共用同一次抓取、合并与缺失值填补，仅评分权重不同。性价比榜与通用榜同权重、同名次（`rank_by: "score"`，按综合分排序，避免便宜小模型霸榜），每行展示官方 API 混合价、最优订阅套餐的月费 / 倍率 / 套餐内等效价与购买链接；`Value = 综合分 ÷ 套餐内 $/1M` 仅作参考列。配套的「套餐购买指南」按套餐维度汇总：每个套餐取其覆盖厂商在通用榜上的最强模型，`套餐内 Value = 最强模型综合分 ÷ (Blended $/1M × 折扣)`，按该值降序——同时反映套餐可用的模型上限与折算价格（详见「订阅套餐与倍率」一节）。

### 通用榜 General（六维）

面向**编程 / 智能体 / 日常混合使用**，选取 8 个指标归入 6 大类：

| 大类（权重） | 指标 | 子权重 | 全局权重 |
|---|---|---|---|
| **编码 Coding** (25%) | LiveBench Coding | 100% | 25% |
| **Agent 能力** (25%) | DeepSWE | 60% | 15% |
| | LiveBench Agentic Coding | 40% | 10% |
| **指令遵循** (15%) | LiveBench Instruction Following | 100% | 15% |
| **长上下文** (10%) | LCR | 100% | 10% |
| **事实准确性** (15%) | Omniscience Index | 100% | 15% |
| **知识领域** (10%) | GPQA Diamond | 30% | 3% |
| | HLE | 70% | 7% |

全局权重之和 = 1.00。

**设计逻辑**：编码（25%）与 Agent（25%）是 vibe coding 场景主菜；指令遵循（15%）是「指哪打哪」的高频体验；长上下文 + 事实（25%）是可靠性双保险；知识（10%）是基础门槛。事实准确性权重上调（10%→15%）、编码下调（30%→25%），因为前者区分度最高（归一化 std 16.7）、后者已饱和（std 4.7）；GPQA 已饱和（真实值 0.87~0.94，std 2.9）故降权，HLE 区分度更好（std 7.6）故升权。

### 文本榜 Text（五维）

面向**写小说、日常问答**，选取 7 个指标归入 5 大类：

| 大类（权重） | 指标 | 子权重 | 全局权重 |
|---|---|---|---|
| **创意写作** (25%) | EQ-Bench Creative Writing | 70% | 17.5% |
| | LiveBench Language | 30% | 7.5% |
| **事实准确性** (20%) | Omniscience Index | 100% | 20% |
| **指令遵循** (20%) | LiveBench Instruction Following | 100% | 20% |
| **知识领域** (20%) | GPQA Diamond | 30% | 6% |
| | HLE | 70% | 14% |
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
- **越界裁剪**：原始值超出锚点范围时裁剪到 0–100（如 EQ-Bench Elo 超过 2200 上限不再产生 >100 的异常分）

各指标锚点：

| 指标 | 锚点 [lo, hi] | 说明 |
|---|---|---|
| LiveBench 各分类 / DeepSWE | [0, 100] | 已是 0–100 百分比 |
| LCR / GPQA Diamond / HLE | [0, 1] | 0–1 比例，×100 隐含 |
| Omniscience Index | [-50, 50] | 净得分实际可达范围（全对/全错几乎不可能，0=中性） |
| EQ-Bench Creative Writing | [1400, 2200] | Elo 实际分布约 1438~2105，下限收紧到 1400 避免分数被压到 45 分以上 |

> 与旧版 min-max 的区别：min-max 用「样本最高=100、最低=0」动态锚点，把名次差当能力差（离群值敏感、样本小不稳定、二次归一化抹掉难度）；固定锚点保留绝对难度与稳定性。Omniscience Index 用 [-50,50] 而非官方 [-100,100]：后者把实际样本（约 -19~43）压缩到 40-72 的窄区间、且让负分模型虚高到 40 分，[-50,50] 更贴合实际可达范围，负分模型正确压到 <50 分。

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

### 填补降权（可配置）

填补值可信度低于真实值（留一验证 MAE 越大越不可靠）。`score_board` 支持对填补指标的权重打折：填补指标的权重 × `imputed_weight_discount`，其余真实指标权重不变，再**重新归一化**到总权重 1，保证总分仍落在 0–100 可比。

- `imputed_weight_discount = 1.0`（默认）= 不降权，与旧版一致。
- `discount < 1` 时，填补指标对总分贡献降低、真实指标权重相对上升——用于抑制填补误差（如 DeepSWE MAE≈10）对排名的干扰。
- 参数在 `config.json` 顶层 `imputed_weight_discount` 配置，缺失时默认 1.0。

## 留一验证

每次评分运行后，自动对每个指标做留一交叉验证（假装修饰一个真实值，用其余样本训练岭回归预测，报告 MAE 与 >10% 误差比例）。结果按榜单拆分写入 `results/validation_general.json` / `results/validation_text.json`。

**乐观偏差（须知）**：当前 LOO 在迭代填补写满 `cur` 之后运行，其他指标的已填补值会进入特征，故 MAE 略偏乐观（低估真实填补误差）。解读时按上界参考。

## 模型拟合质量（R²）

用全量训练集拟合后，计算每个指标的训练集 R²（z-score 空间）。R² 越高，该指标的缺失值预测越可信。当前（2026-08 快照）各指标 R² 约 0.71–0.93，其中 GPQA Diamond（0.93）与 HLE（0.92）最可预测，LiveBench Instruction Following（0.71）最低——填补可信度请以留一验证 MAE 为准。

## 能力-成本前沿图

`results/value_frontier.svg`（通用榜，纵轴 = 通用榜综合分）与 `results/text_frontier.svg`（文本榜，纵轴 = 文本榜综合分）随每次构建重新生成，算法在 `scripts/plot_frontier.py`：

- **横轴**：实际等效价（`Effective $/1M`，最优订阅套餐折算后的等效价，无订阅厂商即官方按量混合价）× 当次汇率折人民币，对数刻度；**纵轴**：对应榜单的 Weighted Total。
- **前沿定义**：价格升序中综合分严格递增的点序列（Pareto 最优）；红色阶梯线在预算 x 处的高度即该预算能买到的最强模型。
- **y 轴自适应**：下界 floor(min/5)×5、上界 ceil(max/5)×5+2，刻度间隔 5。
- **标注布局**：标签水平放点右侧，按水平投影分簇、簇内按锚点高度贪心垂直排布（重叠沿初始方向单调外推）、画布边界回退；离锚点较远的标签带细引线和白底框。布局用纯文本包围盒在 display 像素空间计算，与字体后端无关。

## 注意事项

1. **非绝对排名**：分数是相对排名，不代表能力绝对值
2. **填补值可信度**：留一验证 MAE 越低的指标填补越可靠；`(reg,low)` 填补仅供参考
3. **权重可自定义**：权重设计反映「编程 + 智能体 + 日常对话」的平衡，可通过 `config.json` 调整
4. **模型池需维护**：主流旗舰模型池与别名映射在 `model_registry.json`，新增模型需同步
5. **特征独立性**：填补仅用评分指标交叉预测，不含任何合成综合分，避免循环论证
