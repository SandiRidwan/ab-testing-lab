"""
make_charts.py — chart PNG statis untuk README (rigor statistik divisualkan).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from config import COLORS as C, DB_FILE, FIGURES

plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight",
                     "axes.grid": True, "grid.alpha": 0.25,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "font.size": 10})


def q(sql):
    con = duckdb.connect(str(DB_FILE), read_only=True)
    df = con.execute(sql).df()
    con.close()
    return df


def chart_ci() -> None:
    t = q("SELECT * FROM mart_test_results ORDER BY abs_lift")
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, r in enumerate(t.itertuples()):
        col = C["red"] if r.abs_lift < 0 else C["primary"]
        ax.errorbar(r.abs_lift, i, xerr=[[r.abs_lift - r.ci_low],
                    [r.ci_high - r.abs_lift]], fmt="o", color=col,
                    capsize=6, markersize=9, lw=2.5)
    ax.axvline(0, ls="--", color="#888")
    ax.set_yticks(range(len(t)))
    ax.set_yticklabels(t["metric"])
    ax.set_title("Efek + Confidence Interval 95%", fontweight="bold")
    ax.set_xlabel("selisih (treatment − kontrol)")
    fig.savefig(FIGURES / "01_effect_ci.png")
    plt.close(fig)
    print("  ✓ 01_effect_ci.png")


def chart_retention() -> None:
    m = q("""SELECT metric, variant, nilai_rata FROM mart_variant_metrics
             WHERE metric LIKE 'retention%' ORDER BY metric, variant""")
    piv = m.pivot(index="metric", columns="variant", values="nilai_rata")
    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(piv))
    w = 0.35
    ax.bar([i - w/2 for i in x], piv["gate_30"], w, label="gate_30 (kontrol)",
           color=C["control"])
    ax.bar([i + w/2 for i in x], piv["gate_40"], w, label="gate_40 (treatment)",
           color=C["treatment"])
    for i, (a, b) in enumerate(zip(piv["gate_30"], piv["gate_40"])):
        ax.text(i-w/2, a, f"{a:.3f}", ha="center", va="bottom", fontsize=8)
        ax.text(i+w/2, b, f"{b:.3f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(piv.index)
    ax.set_ylim(0, max(piv.max()) * 1.2)
    ax.set_title("Retensi per Varian", fontweight="bold")
    ax.set_ylabel("proporsi")
    ax.legend()
    fig.savefig(FIGURES / "02_retention.png")
    plt.close(fig)
    print("  ✓ 02_retention.png")


def chart_power() -> None:
    p = q("SELECT * FROM mart_power")
    fig, ax = plt.subplots(figsize=(8, 4))
    x = range(len(p))
    w = 0.35
    ax.bar([i - w/2 for i in x], p["n_per_group_req"], w,
           label="dibutuhkan", color=C["accent"])
    ax.bar([i + w/2 for i in x], p["n_actual_min"], w,
           label="aktual", color=C["primary"])
    ax.set_xticks(list(x))
    ax.set_xticklabels(p["metric"], fontsize=8)
    ax.set_title("Sampel Dibutuhkan vs Aktual (per grup)", fontweight="bold")
    ax.legend()
    fig.savefig(FIGURES / "03_power.png")
    plt.close(fig)
    print("  ✓ 03_power.png")


def chart_segments() -> None:
    s = q("""SELECT segmen, rel_lift_pct FROM mart_segment_effects
             ORDER BY segmen""")
    fig, ax = plt.subplots(figsize=(7, 4))
    cols = [C["red"] if v < 0 else C["primary"] for v in s["rel_lift_pct"]]
    ax.bar(s["segmen"], s["rel_lift_pct"], color=cols)
    for i, v in enumerate(s["rel_lift_pct"]):
        ax.text(i, v, f"{v:+.1f}%", ha="center",
                va="bottom" if v >= 0 else "top", fontsize=9)
    ax.axhline(0, color="#888", lw=0.8)
    ax.set_title("Efek Retensi-7 per Segmen Engagement", fontweight="bold")
    ax.set_ylabel("rel-lift %")
    fig.savefig(FIGURES / "04_segments.png")
    plt.close(fig)
    print("  ✓ 04_segments.png")


def main() -> None:
    if not DB_FILE.exists():
        raise SystemExit("DB belum ada — jalankan: python src/run_pipeline.py")
    print("[charts] menghasilkan PNG untuk README:")
    chart_ci()
    chart_retention()
    chart_power()
    chart_segments()
    print(f"[charts] selesai → {FIGURES}")


if __name__ == "__main__":
    main()
