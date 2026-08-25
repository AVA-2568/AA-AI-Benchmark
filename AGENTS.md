# AA-AI-Benchmark Agent Guide

## 目标
按多源公开基准数据（LiveBench / DeepSWE / EQ-Bench / Artificial Analysis）生成 General / Text / Value 三个榜单。

## 唯一入口
```bash
python scripts/build.py
```

离线复算现有缓存：
```bash
python scripts/build.py --offline
```

## 测试
```bash
python -m pytest -q
```

## 数据流
fetch(多源) -> detect(新模型发现，`--apply` 自动入池) -> merge(跨源合并) -> imputation -> validation -> scoring -> README

## 核心不变量
- leaderboard 权重总和必须为 1。
- 每个评分指标必须存在于 imputation_pool，且其固定锚点必须在 metric_scales 中。
- 原始值与填补值必须区分。
- 填补仅用评分指标交叉预测，不得引入任何合成综合分。
- README 只能替换标记区块；标记缺失时构建失败。
- 抓取失败时默认失败；`--allow-stale` 仅用于显式诊断，且不刷新 README。
- 每次构建生成 `results/manifest.json`，记录输入哈希、配置哈希和 stale 状态。
- 模型池与别名映射在 `scripts/model_registry.json`，新增模型需同步维护。
- `detect_new_models.py` 默认只读，输出 `results/new_model_candidates.json` 候选清单（新模型 + 别名漏配两类）；build 以 `--apply` 运行：双源确认（livebench/deepswe/aa 任二出现）的新模型自动入池，条目带 `auto_added` 日期标记；单源孤立候选只报告不入池；registry 顶层可选 `auto_add_exclude`（fnmatch 通配）永久排除误报名称；发现候选不视为构建失败。

## 修改规则
- 修改算法必须同步更新 METHODOLOGY.md。
- 修改结果字段必须同步更新测试和 README。
- 不得在实验脚本复制评分逻辑。
- 修改后先运行 `python -m pytest -q`，再用 `python scripts/build.py --offline` 做端到端验证。
