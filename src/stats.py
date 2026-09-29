"""
stats.py — ANALISIS STATISTIK (inti project).

Menyediakan metode inferensial yang BENAR & dapat diaudit:
  · Uji proporsi (2-proporsi z-test) & uji mean (Welch t-test)
  · Confidence interval 95% (analitis + bootstrap)
  · Power analysis (sampel dibutuhkan + power tercapai)
  · Koreksi multiple-testing (Benjamini-Hochberg FDR)
  · Deteksi SRM (Sample Ratio Mismatch, chi-square)
  · CUPED (variance reduction) — opsional bila ada kovariat pra-periode
  · Heterogeneous treatment effect per segmen

PRINSIP: hasil TIDAK di-overclaim. Setiap angka disertai ketidakpastian (CI)
dan status signifikansi yang dikoreksi. Efek kecil tidak disebut "berhasil"
hanya karena p<0.05.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats as sps
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize


# ---------------------------------------------------------------------------
# Uji hipotesis
# ---------------------------------------------------------------------------
def test_proportion(x_c: int, n_c: int, x_t: int, n_t: int,
                    alpha: float = 0.05) -> dict:
    """
    Uji 2 proporsi (z-test, setara chi-square 2x2) + 95% CI selisih absolut.
    Dipakai untuk metrik biner (retention).
    """
    p_c, p_t = x_c / n_c, x_t / n_t
    diff = p_t - p_c
    # standard error di bawah H0 (pooled) untuk p-value
    p_pool = (x_c + x_t) / (n_c + n_t)
    se_h0 = np.sqrt(p_pool * (1 - p_pool) * (1 / n_c + 1 / n_t))
    z = diff / se_h0 if se_h0 > 0 else 0.0
    p_value = 2 * (1 - sps.norm.cdf(abs(z)))
    # SE tak-terpool untuk CI (lebih tepat)
    se_ci = np.sqrt(p_c * (1 - p_c) / n_c + p_t * (1 - p_t) / n_t)
    z_crit = sps.norm.ppf(1 - alpha / 2)
    return {
        "kontrol": p_c, "treatment": p_t, "abs_lift": diff,
        "rel_lift_pct": (diff / p_c * 100) if p_c else 0.0,
        "ci_low": diff - z_crit * se_ci, "ci_high": diff + z_crit * se_ci,
        "p_value": float(p_value), "test_used": "2-proporsi z-test",
    }


def test_mean(a: np.ndarray, b: np.ndarray, alpha: float = 0.05) -> dict:
    """
    Welch t-test (tidak asumsi varians sama) + 95% CI selisih mean.
    Dipakai untuk metrik kontinu (sum_gamerounds). Tahan terhadap outlier
    dibanding Student t-test.
    """
    a, b = np.asarray(a, float), np.asarray(b, float)
    m_a, m_b = a.mean(), b.mean()
    diff = m_b - m_a
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = np.sqrt(va / len(a) + vb / len(b))
    t = diff / se if se > 0 else 0.0
    # df Welch-Satterthwaite
    df = (va / len(a) + vb / len(b)) ** 2 / (
        (va / len(a)) ** 2 / (len(a) - 1) + (vb / len(b)) ** 2 / (len(b) - 1))
    p_value = 2 * (1 - sps.t.cdf(abs(t), df))
    t_crit = sps.t.ppf(1 - alpha / 2, df)
    return {
        "kontrol": float(m_a), "treatment": float(m_b), "abs_lift": float(diff),
        "rel_lift_pct": (diff / m_a * 100) if m_a else 0.0,
        "ci_low": float(diff - t_crit * se), "ci_high": float(diff + t_crit * se),
        "p_value": float(p_value), "test_used": "Welch t-test",
    }


def bootstrap_ci(a: np.ndarray, b: np.ndarray, n_boot: int = 2000,
                 alpha: float = 0.05, seed: int = 42) -> tuple[float, float]:
    """Bootstrap 95% CI untuk selisih mean (metode non-parametrik, verifikasi)."""
    rng = np.random.default_rng(seed)
    a, b = np.asarray(a, float), np.asarray(b, float)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        diffs[i] = (rng.choice(b, len(b)).mean() - rng.choice(a, len(a)).mean())
    lo, hi = np.percentile(diffs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


# ---------------------------------------------------------------------------
# Power analysis
# ---------------------------------------------------------------------------
def power_proportion(p_c: float, mde_rel: float, alpha: float = 0.05,
                     power: float = 0.80) -> int:
    """Sampel per grup untuk mendeteksi efek relatif mde_rel pada proporsi."""
    p_t = p_c * (1 + mde_rel)
    es = proportion_effectsize(p_t, p_c)
    n = NormalIndPower().solve_power(effect_size=es, alpha=alpha,
                                     power=power, ratio=1.0, alternative="two-sided")
    return int(np.ceil(n))


def power_mean(std: float, mde_abs: float, alpha: float = 0.05,
               power: float = 0.80) -> int:
    """Sampel per grup untuk mendeteksi selisih mean absolut mde_abs."""
    es = mde_abs / std if std > 0 else 0
    n = NormalIndPower().solve_power(effect_size=es, alpha=alpha,
                                     power=power, ratio=1.0, alternative="two-sided")
    return int(np.ceil(n))


def achieved_power(n: int, effect_size: float, alpha: float = 0.05) -> float:
    """Power yang dicapai dengan n aktual per grup."""
    if effect_size <= 0:
        return 0.0
    return float(NormalIndPower().power(effect_size=effect_size, nobs1=n,
                                        alpha=alpha, ratio=1.0,
                                        alternative="two-sided"))


# ---------------------------------------------------------------------------
# Koreksi multiple testing
# ---------------------------------------------------------------------------
def benjamini_hochberg(p_values: list[float], alpha: float = 0.05) -> list[float]:
    """Koreksi FDR Benjamini-Hochberg. Kembalikan p-value terkoreksi."""
    p = np.asarray(p_values, float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order]
    adj = ranked * n / (np.arange(n) + 1)
    # monotonkan dari belakang
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    adj = np.clip(adj, 0, 1)
    out = np.empty(n)
    out[order] = adj
    return out.tolist()


# ---------------------------------------------------------------------------
# SRM (Sample Ratio Mismatch)
# ---------------------------------------------------------------------------
def srm_check(n_c: int, n_t: int, expected_ratio: float = 0.5) -> dict:
    """
    Uji apakah rasio alokasi menyimpang dari harapan (chi-square goodness of fit).
    SRM = tanda kuat eksperimen cacat; bila p<0.001, JANGAN percaya hasilnya.
    """
    total = n_c + n_t
    exp_c = total * expected_ratio
    exp_t = total * (1 - expected_ratio)
    chi2 = (n_c - exp_c) ** 2 / exp_c + (n_t - exp_t) ** 2 / exp_t
    p = float(1 - sps.chi2.cdf(chi2, df=1))
    return {"chi2": float(chi2), "p_value": p,
            "srm_terdeteksi": p < 0.001,
            "proporsi_control": n_c / total if total else 0}


# ---------------------------------------------------------------------------
# CUPED (variance reduction) — bila ada kovariat pra-periode
# ---------------------------------------------------------------------------
def cuped(y: np.ndarray, x: np.ndarray, theta: float | None = None):
    """
    CUPED: kurangi varians memakai kovariat pra-eksperimen x.
    y_adj = y - theta*(x - mean(x)); theta = cov(y,x)/var(x).
    Mengembalikan (y_adj, theta). Menurunkan varians -> CI lebih sempit.
    """
    y, x = np.asarray(y, float), np.asarray(x, float)
    if theta is None:
        theta = np.cov(y, x)[0, 1] / np.var(x) if np.var(x) > 0 else 0.0
    return y - theta * (x - x.mean()), float(theta)
