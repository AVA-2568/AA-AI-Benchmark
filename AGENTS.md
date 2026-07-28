# AA-AI-Benchmark Agent Guide

## 目标
按 Artificial Analysis 数据生成 General / Text 两个榜单。

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
RSC/HTML -> parse -> dedup -> imputation -> validation -> scoring -> README

## 核心不变量
- leaderboard 权重总和必须为 1。
- 每个评分指标必须存在于 imputation_pool。
- 原始值与填补值必须区分。
- 不得用 Intelligence Index 参与填补。
- README 只能替换标记区块；标记缺失时构建失败。
- 抓取失败时默认失败；`--allow-stale` 仅用于显式诊断，且不刷新 README。
- 每次构建生成 `results/manifest.json`，记录输入哈希、配置哈希和 stale 状态。

## 修改规则
- 修改算法必须同步更新 METHODOLOGY.md。
- 修改结果字段必须同步更新测试和 README。
- 不得在实验脚本复制评分逻辑。
- 修改后先运行 `python -m pytest -q`，再用 `python scripts/build.py --offline` 做端到端验证。
