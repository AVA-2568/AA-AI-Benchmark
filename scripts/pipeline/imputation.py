"""Shared ridge-regression imputation + leave-one-out validation.

The imputation pool is the 11 metrics shared by both leaderboards.
Imputation uses cross-feature ridge regression (no Intelligence Index
in the features) with z-score standardization and damped updates.
The same engine is reused by the P99 experiment — the only
parameter that differs there is ``clip_quantile``.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.preprocessing import StandardScaler

from .config import to_float


def compute_stats(rows, pool, clip_quantile=0.95):
    """Per-metric (lo, hi, top50mean, p90, clip) over observed values."""
    stats = {}
    for m in pool:
        vals = [to_float(r.get(m)) for r in rows]
        vals = [v for v in vals if v is not None]
        if len(vals) < 2:
            raise ValueError(f"{m} effective samples {len(vals)} < 2")
        lo, hi = min(vals), max(vals)
        sv = sorted(vals)
        p90 = sv[min(len(sv) - 1, int(0.90 * (len(sv) - 1)))]
        clip = sv[min(len(sv) - 1, int(clip_quantile * (len(sv) - 1)))]
        top50 = sv[len(sv) // 2:]
        top50mean = sum(top50) / len(top50)
        stats[m] = (lo, hi, top50mean, p90, clip)
    return stats


class ImputationEngine:
    """Holds the shared pool state and runs iterative imputation + LOO."""

    def __init__(self, rows, pool, cfg_params):
        self.rows = rows
        self.pool = pool
        self.n_pool = len(pool)
        self.alpha = cfg_params["ridge_alpha"]
        self.min_samples = cfg_params["imputation_min_samples"]
        self.standardize = cfg_params["standardize_features"]
        self.damping = cfg_params["damping"]
        n = len(rows)
        self.raw = {m: [to_float(r.get(m)) for r in rows] for m in pool}
        self.stats = compute_stats(rows, pool, cfg_params["clip_quantile"])
        self.cur = {
            m: [(v if v is not None else self.stats[m][2]) for v in self.raw[m]]
            for m in pool
        }
        self.imputation_quality = {
            m: {"n_train": sum(1 for i in range(n) if self.raw[m][i] is not None)}
            for m in pool
        }
        if self.standardize:
            x_raw_real = np.array([
                [self.raw[m][i] if self.raw[m][i] is not None else self.stats[m][2]
                 for i in range(n)]
                for m in pool
            ], dtype=float)  # N_POOL x n
            self.scaler = StandardScaler()
            self.scaler.fit(x_raw_real.T)  # fit on n x N_POOL
        else:
            self.scaler = None

    def all_feat_row(self, i):
        """Full pool feature row for model i (all pool metrics)."""
        return [self.cur[mm][i] for mm in self.pool]

    def to_X(self, arr_pool, target_m):
        """arr_pool: n x N_POOL. Returns [1, std N_POOL-1 excluding target]."""
        if self.scaler is not None:
            arr_pool = self.scaler.transform(arr_pool)
        target_idx = self.pool.index(target_m)
        keep = np.r_[:target_idx, target_idx + 1:self.n_pool]
        return np.hstack([np.ones((len(arr_pool), 1)), arr_pool[:, keep]])

    def run(self, max_iters, rel_tol, stable_rounds):
        """Iterative imputation. Returns (converged_iter, max_delta)."""
        n = len(self.rows)
        prev = {m: list(self.cur[m]) for m in self.pool}
        stable_count = 0
        max_delta = 0.0
        converged_iter = None
        for it in range(max_iters):
            for m in self.pool:
                xtr, ytr = [], []
                for i in range(n):
                    if self.raw[m][i] is not None:
                        xtr.append(self.all_feat_row(i))
                        ytr.append(self.raw[m][i])
                if len(xtr) < 3:
                    continue
                xtr_arr = np.array(xtr, dtype=float)
                ytr_arr = np.array(ytr, dtype=float)
                x1 = self.to_X(xtr_arr, m)
                a = x1.T @ x1 + self.alpha * np.eye(x1.shape[1])
                try:
                    beta = np.linalg.solve(a, x1.T @ ytr_arr)
                except np.linalg.LinAlgError:
                    beta = np.linalg.lstsq(x1, ytr_arr, rcond=None)[0]
                lo, hi, _, _, clip = self.stats[m]
                n_train = self.imputation_quality[m]["n_train"]
                for i in range(n):
                    if self.raw[m][i] is None and n_train >= self.min_samples:
                        xi = self.to_X(np.array([self.all_feat_row(i)], dtype=float), m)[0]
                        pred = max(lo, min(clip, float(xi @ beta)))
                        # Damped update: suppress oscillation from strongly
                        # correlated columns (e.g. Omniscience trio).
                        self.cur[m][i] = (1 - self.damping) * self.cur[m][i] + self.damping * pred
            max_delta = 0.0
            for m in self.pool:
                lo, hi = self.stats[m][0], self.stats[m][1]
                rng = (hi - lo) or 1.0
                for i in range(n):
                    if self.raw[m][i] is None:
                        max_delta = max(
                            max_delta, abs(self.cur[m][i] - prev[m][i]) / rng)
            if max_delta < rel_tol:
                stable_count += 1
                if stable_count >= stable_rounds:
                    converged_iter = it - 1
                    break
            else:
                stable_count = 0
            prev = {m: list(self.cur[m]) for m in self.pool}
        return converged_iter, max_delta

    def loo_validation(self):
        """Leave-one-out validation over the whole observed set (no subsample).

        Note: features come from ``all_feat_row`` after imputation fills
        ``cur``, so LOO is slightly optimistic vs raw-only (documented
        in METHODOLOGY). The clipping quantile uses ``stats``.
        """
        n = len(self.rows)
        validation = {}
        for target_m in self.pool:
            has_true = [j for j in range(n) if self.raw[target_m][j] is not None]
            nn = len(has_true)
            if nn < 10:
                validation[target_m] = {"mae": None, "pct_over10": None, "n": nn}
                continue
            errors = []
            true_vals = []
            for skip_i in has_true:
                true_val = self.raw[target_m][skip_i]
                xtr, ytr = [], []
                for j in range(n):
                    if j != skip_i and self.raw[target_m][j] is not None:
                        xtr.append(self.all_feat_row(j))
                        ytr.append(self.raw[target_m][j])
                if len(xtr) < 3:
                    continue
                xtr_arr = np.array(xtr, dtype=float)
                ytr_arr = np.array(ytr, dtype=float)
                x1 = self.to_X(xtr_arr, target_m)
                a = x1.T @ x1 + self.alpha * np.eye(x1.shape[1])
                try:
                    beta = np.linalg.solve(a, x1.T @ ytr_arr)
                except np.linalg.LinAlgError:
                    beta = np.linalg.lstsq(x1, ytr_arr, rcond=None)[0]
                xi = self.to_X(np.array([self.all_feat_row(skip_i)], dtype=float), target_m)[0]
                pred = float(xi @ beta)
                lo, hi, _, _, clip = self.stats[target_m]
                pred = max(lo, min(clip, pred))
                errors.append(abs(pred - true_val))
                true_vals.append(true_val)
            if not errors:
                validation[target_m] = {"mae": None, "pct_over10": None, "n": nn}
                continue
            mae = sum(errors) / len(errors)
            over10 = sum(
                1 for i, e in enumerate(errors)
                if abs(true_vals[i]) > 0.001 and e / abs(true_vals[i]) > 0.10
            )
            validation[target_m] = {
                "mae": round(mae, 4),
                "pct_over10": round(over10 / len(errors) * 100, 1),
                "n": nn,
            }
        return validation

    def r2_log(self):
        """Training R2 per metric (z-score space, cross-predict only)."""
        n = len(self.rows)
        out = {}
        for m in self.pool:
            xtr, ytr = [], []
            for i in range(n):
                if self.raw[m][i] is not None:
                    xtr.append(self.all_feat_row(i))
                    ytr.append(self.raw[m][i])
            if len(xtr) < 3:
                continue
            xtr_arr = np.array(xtr, dtype=float)
            ytr_arr = np.array(ytr, dtype=float)
            x1 = self.to_X(xtr_arr, m)
            beta = np.linalg.lstsq(x1, ytr_arr, rcond=None)[0]
            pred = x1 @ beta
            ybar = ytr_arr.mean()
            ss_tot = ((ytr_arr - ybar) ** 2).sum() or 1e-12
            ss_res = ((ytr_arr - pred) ** 2).sum()
            out[m] = max(0.0, 1 - ss_res / ss_tot)
        return out
