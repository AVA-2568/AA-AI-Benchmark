#!/usr/bin/env python3
"""能力-成本 Pareto 前沿图：给定每 1M token 预算时的最优模型选择。

读 value_scored.csv 的行（通用榜名次序），横轴取实际支付价（最优订阅
套餐折算后的等效价，无订阅厂商即官方按量混合价）× 汇率折人民币，
纵轴取 Weighted Total。前沿 = 价格升序中能力递增的模型；阶梯线在
预算 x 处的高度即该预算能买到的最强模型。输出单面板 SVG（人民币
计价），标签用英文以兼容无中文字体的构建环境。
"""
import matplotlib

matplotlib.use("Agg")
# 中文标签字体链：CI（ubuntu，装 fonts-noto-cjk）用 Noto，Windows 本地回退雅黑/黑体
matplotlib.rcParams["font.sans-serif"] = [
    "Noto Sans CJK SC", "Microsoft YaHei", "SimHei", "DejaVu Sans"]

import matplotlib.pyplot as plt  # noqa: E402


def pareto_frontier(points):
    """[(price, score, label)] -> 价格升序中能力递增的最优点序列。

    剔除无价格/无分数的点；同价取先到者（分数必须严格更高才入前沿）。
    """
    pts = sorted((p for p in points if p[0] and p[1] is not None),
                 key=lambda p: p[0])
    out = []
    best = float("-inf")
    for price, score, label in pts:
        if score > best:
            out.append((price, score, label))
            best = score
    return out


def render(rows, out_path, fx_rate=None):
    """渲染单面板（人民币）前沿图到 out_path（SVG）。

    rows 为 value_scored.csv 的行；fx_rate（USD→CNY）必需。
    画幅与字号按 GitHub README ~780px 的显示宽度校准：字号相对放大、
    x 轴用手动刻度直标 ¥ 数值（不出现 10^n 或 USD 字样）。
    """
    if not fx_rate:
        raise ValueError("fx_rate is required: the chart is priced in CNY")
    points = []
    for r in rows:
        try:
            price = float(r.get("Effective $/1M") or 0) * fx_rate
            score = float(r.get("Weighted Total") or 0)
        except ValueError:
            continue
        if price > 0 and score > 0:
            points.append((price, score, r.get("Model") or "?"))
    frontier = pareto_frontier(points)
    if not frontier:
        raise ValueError("no plottable models: empty frontier")

    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    ax.scatter([p for p, _, _ in points], [s for _, s, _ in points],
               s=24, color="#c3c7cc", alpha=0.75, zorder=1,
               label="全部模型 all models")
    fx_p = [p for p, _, _ in frontier]
    scores = [s for _, s, _ in frontier]
    ax.step(fx_p + [fx_p[-1] * 1.8], scores + [scores[-1]],
            where="post", color="#d62728", linewidth=2.4, zorder=2,
            label="最优选择前沿 best choice")
    ax.scatter(fx_p, scores, s=55, color="#d62728", zorder=3)
    # 上下交替标注，避免中段密集区的模型名互相重叠
    for i, (p, s, label) in enumerate(frontier):
        if i % 2 == 0:
            ax.annotate(label, (p, s), xytext=(6, -5),
                        textcoords="offset points", fontsize=9.5,
                        rotation=18, ha="left", va="top", color="#222")
        else:
            ax.annotate(label, (p, s), xytext=(6, 9),
                        textcoords="offset points", fontsize=9.5,
                        rotation=18, ha="left", va="bottom", color="#222")
    ax.set_xscale("log")
    ticks = [0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"¥{t:g}" for t in ticks], fontsize=10.5)
    ax.set_xlim(0.015, 60)
    ax.set_ylim(45, 82)
    ax.set_yticks([50, 55, 60, 65, 70, 75, 80])
    ax.set_xlabel("实际等效价 / 1M tokens（¥，对数刻度）", fontsize=12)
    ax.set_ylabel("通用榜综合分", fontsize=12)
    ax.grid(True, which="major", alpha=0.25)
    ax.tick_params(axis="y", labelsize=10.5)
    ax.legend(fontsize=10, loc="lower right", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(out_path, format="svg")
    plt.close(fig)
    return frontier
