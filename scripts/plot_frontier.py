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

    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.scatter([p for p, _, _ in points], [s for _, s, _ in points],
               s=22, color="#b8bcc2", zorder=1, label="all models")
    fx_p = [p for p, _, _ in frontier]
    scores = [s for _, s, _ in frontier]
    ax.step(fx_p + [fx_p[-1] * 1.6], scores + [scores[-1]],
            where="post", color="#d62728", linewidth=2.0, zorder=2,
            label="best-choice frontier")
    ax.scatter(fx_p, scores, s=42, color="#d62728", zorder=3)
    for p, s, label in frontier:
        ax.annotate(label, (p, s), xytext=(5, -3),
                    textcoords="offset points", fontsize=8,
                    rotation=30, ha="left", va="top", color="#333")
    ax.set_xscale("log")
    ax.set_xlabel(f"Effective ¥/1M (log, incl. best plan · 1 USD = {fx_rate})",
                  fontsize=10.5)
    ax.set_ylabel("Weighted Total (General)", fontsize=10.5)
    ax.grid(True, which="both", alpha=0.18)
    ax.tick_params(labelsize=9)
    ax.legend(fontsize=9, loc="lower right")
    fig.suptitle("Capability vs Cost — best choice at your budget",
                 fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out_path, format="svg")
    plt.close(fig)
    return frontier
