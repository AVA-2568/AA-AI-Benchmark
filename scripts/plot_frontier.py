#!/usr/bin/env python3
"""能力-成本 Pareto 前沿图：给定每 1M token 预算时的最优模型选择。

读 value_scored.csv 的行（通用榜名次序），横轴取 Effective $/1M（最优
订阅套餐折算后的实际支付价，无订阅厂商即官方按量混合价），纵轴取
Weighted Total。前沿 = 价格升序中能力递增的模型；阶梯线在预算 x 处的
高度即该预算能买到的最强模型。左图美元、右图人民币（实时汇率）。
输出 SVG，标签用英文以兼容无中文字体的构建环境。
"""
import matplotlib

matplotlib.use("Agg")

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
    """渲染双面板（USD / CNY）前沿图到 out_path（SVG）。

    rows 为 value_scored.csv 的行；fx_rate 缺失时只画美元面板。
    """
    points = []
    for r in rows:
        try:
            price = float(r.get("Effective $/1M") or 0)
            score = float(r.get("Weighted Total") or 0)
        except ValueError:
            continue
        if price > 0 and score > 0:
            points.append((price, score, r.get("Model") or "?"))
    frontier = pareto_frontier(points)
    if not frontier:
        raise ValueError("no plottable models: empty frontier")

    panels = [("Effective $/1M (incl. best plan)", 1.0, "USD")]
    if fx_rate:
        panels.append((f"¥/1M (1 USD = {fx_rate} CNY)", fx_rate, "CNY"))

    fig, axes = plt.subplots(1, len(panels), figsize=(6.4 * len(panels), 4.8),
                             sharey=True)
    if len(panels) == 1:
        axes = [axes]
    fx_prices = [p * fx_rate for p, _, _ in frontier] if fx_rate else None

    for ax, (xlabel, mult, _tag) in zip(axes, panels):
        ax.scatter([p * mult for p, _, _ in points],
                   [s for _, s, _ in points],
                   s=14, color="#b8bcc2", zorder=1,
                   label="all models")
        fx_p = [p * mult for p, _, _ in frontier]
        scores = [s for _, s, _ in frontier]
        ax.step(fx_p + [fx_p[-1] * 1.6], scores + [scores[-1]],
                where="post", color="#d62728", linewidth=1.6, zorder=2,
                label="best-choice frontier")
        ax.scatter(fx_p, scores, s=26, color="#d62728", zorder=3)
        for (p, s, label), x in zip(frontier, fx_p):
            ax.annotate(label, (x, s), xytext=(4, -2),
                        textcoords="offset points", fontsize=6.5,
                        rotation=35, ha="left", va="top", color="#333")
        ax.set_xscale("log")
        ax.set_xlabel(xlabel, fontsize=9)
        ax.grid(True, which="both", alpha=0.18)
        ax.tick_params(labelsize=8)
    axes[0].set_ylabel("Weighted Total (General)", fontsize=9)
    axes[0].legend(fontsize=8, loc="lower right")
    fig.suptitle("Capability vs Cost — pick the frontier at your budget",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_path, format="svg")
    plt.close(fig)
    return frontier
