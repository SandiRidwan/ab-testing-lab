"""
analyze.py — ANALISIS: jalankan uji statistik & tulis hasil ke marts.

Alur: DuckDB (staging) → stats.py → marts (mart_test_results, mart_power,
mart_segment_effects). Juga hasil deskriptif via sql/transform.sql.

Metrik: retention_1, retention_7 (biner); sum_gamerounds (kontinu).
Kontrol = gate_30, Treatment = gate_40.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb
import numpy as np
import pandas as pd

from config import (ALPHA, DB_FILE, MDE_REL, POWER, SEED, SQL)
from stats import (benjamini_hochberg, bootstrap_ci, power_mean,
                   power_proportion, srm_check, test_mean, test_proportion,
                   achieved_power)


def main() -> None:
    con = duckdb.connect(str(DB_FILE))
    print("[analyze] transform deskriptif (SQL)...")
    con.execute((SQL / "transform.sql").read_text(encoding="utf-8"))

    df = con.execute("""
        SELECT version, sum_gamerounds,
               retention_1::INT AS retention_1,
               retention_7::INT AS retention_7
        FROM stg_cookie_cats
    """).df()
    df.columns = ["version", "sum_gamerounds", "retention_1", "retention_7"]
    ctrl = df[df.version == "gate_30"]
    trt = df[df.version == "gate_40"]
    print(f"[analyze] kontrol={len(ctrl):,}, treatment={len(trt):,}")

    # ---- SRM -------------------------------------------------------------
    srm = srm_check(len(ctrl), len(trt))
    print(f"[analyze] SRM: p={srm['p_value']:.4f} "
          f"({'TERDETEKSI!' if srm['srm_terdeteksi'] else 'ok'})")

    results, powers = [], []

    # ---- 1. retention_1 (biner) -----------------------------------------
    r1 = test_proportion(int(ctrl.retention_1.sum()), len(ctrl),
                         int(trt.retention_1.sum()), len(trt), ALPHA)
    r1["metric"] = "retention_1"
    results.append(r1)
    lo, hi = bootstrap_ci(ctrl.retention_1.values, trt.retention_1.values,
                          seed=SEED)
    print(f"[analyze] retention_1: {r1['kontrol']:.4f}→{r1['treatment']:.4f} "
          f"({r1['rel_lift_pct']:+.2f}%) p={r1['p_value']:.4f} "
          f"[bootstrap CI {lo:+.4f},{hi:+.4f}]")
    n_req = power_proportion(r1["kontrol"], MDE_REL, ALPHA, POWER)
    powers.append({"metric": "retention_1", "baseline": r1["kontrol"],
                   "mde_rel": MDE_REL, "n_per_group_req": n_req,
                   "n_actual_min": min(len(ctrl), len(trt))})

    # ---- 2. retention_7 (biner) -----------------------------------------
    r7 = test_proportion(int(ctrl.retention_7.sum()), len(ctrl),
                         int(trt.retention_7.sum()), len(trt), ALPHA)
    r7["metric"] = "retention_7"
    results.append(r7)
    n_req7 = power_proportion(r7["kontrol"], MDE_REL, ALPHA, POWER)
    powers.append({"metric": "retention_7", "baseline": r7["kontrol"],
                   "mde_rel": MDE_REL, "n_per_group_req": n_req7,
                   "n_actual_min": min(len(ctrl), len(trt))})
    print(f"[analyze] retention_7: {r7['kontrol']:.4f}→{r7['treatment']:.4f} "
          f"({r7['rel_lift_pct']:+.2f}%) p={r7['p_value']:.4f}")

    # ---- 3. sum_gamerounds (kontinu) ------------------------------------
    # Robust: buang outlier ekstrem (>99.9 persentil) karena heavily skewed
    cap = df["sum_gamerounds"].quantile(0.999)
    a = ctrl[ctrl.sum_gamerounds <= cap]["sum_gamerounds"].values
    b = trt[trt.sum_gamerounds <= cap]["sum_gamerounds"].values
    rg = test_mean(a, b, ALPHA)
    rg["metric"] = "sum_gamerounds"
    results.append(rg)
    std = float(np.concatenate([a, b]).std(ddof=1))
    mde_abs = rg["kontrol"] * MDE_REL
    n_reqg = power_mean(std, mde_abs, ALPHA, POWER)
    powers.append({"metric": "sum_gamerounds", "baseline": rg["kontrol"],
                   "mde_rel": MDE_REL, "n_per_group_req": n_reqg,
                   "n_actual_min": min(len(a), len(b))})
    print(f"[analyze] sum_gamerounds: {rg['kontrol']:.2f}→{rg['treatment']:.2f} "
          f"({rg['rel_lift_pct']:+.2f}%) p={rg['p_value']:.4f} (cap {cap:.0f})")

    # ---- Koreksi multiple-testing (BH-FDR) ------------------------------
    pvals = [r["p_value"] for r in results]
    adj = benjamini_hochberg(pvals, ALPHA)
    for r, p_adj in zip(results, adj):
        r["p_value_adj"] = p_adj
        r["signifikan_raw"] = r["p_value"] < ALPHA
        r["signifikan_adj"] = p_adj < ALPHA
    print(f"[analyze] koreksi BH: {[round(x,4) for x in adj]}")

    # ---- Simpan mart_test_results ---------------------------------------
    con.execute("DELETE FROM mart_test_results")
    for r in results:
        con.execute("""INSERT INTO mart_test_results VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?)""", [
            r["metric"], r["kontrol"], r["treatment"], r["abs_lift"],
            r["rel_lift_pct"], r["ci_low"], r["ci_high"], r["p_value"],
            r["p_value_adj"], r["signifikan_raw"], r["signifikan_adj"],
            r["test_used"]])

    # ---- Simpan mart_power ----------------------------------------------
    con.execute("DELETE FROM mart_power")
    for p in powers:
        n_req = p["n_per_group_req"]
        es = (p["baseline"] * MDE_REL) / (
            np.sqrt(p["baseline"] * (1 - p["baseline"]))
            if p["metric"].startswith("ret") else 1.0) if p["baseline"] else 0
        p_ach = achieved_power(p["n_actual_min"], es, ALPHA)
        con.execute("""INSERT INTO mart_power VALUES (?,?,?,?,?,?,?)""", [
            p["metric"], p["baseline"], p["mde_rel"], n_req,
            p["n_actual_min"], round(p_ach, 3), p["n_actual_min"] >= n_req])

    # ---- Heterogeneous effect per segmen engagement ---------------------
    con.execute("DELETE FROM mart_segment_effects")
    seg_df = df[df.sum_gamerounds <= cap].copy()
    seg_df["segmen"] = pd.qcut(seg_df["sum_gamerounds"], 4,
                               labels=["Q1 (rendah)", "Q2", "Q3",
                                       "Q4 (tinggi)"], duplicates="drop")
    segs = []
    for s in seg_df["segmen"].cat.categories:
        sub = seg_df[seg_df.segmen == s]
        sc = sub[sub.version == "gate_30"]
        st = sub[sub.version == "gate_40"]
        if len(sc) and len(st):
            k = sc.retention_7.mean()
            t = st.retention_7.mean()
            segs.append((s, k, t, (t - k) / k * 100 if k else 0,
                         len(sc), len(st)))
            con.execute("""INSERT INTO mart_segment_effects VALUES
                (?,?,?,?,?,?,?)""",
                ["retention_7", str(s), k, t,
                 (t - k) / k * 100 if k else 0, len(sc), len(st)])

    print("\n[analyze] === HASIL UJI (retention_7) per segmen engagement ===")
    for s in segs:
        print(f"   {str(s[0]):12} kontrol={s[1]:.3f} treat={s[2]:.3f} "
              f"lift={s[3]:+.1f}%  n={s[4]+s[5]}")

    # Ekspor marts ke Parquet
    for t in ["mart_variant_metrics", "mart_srm", "mart_test_results",
              "mart_power", "mart_segment_effects"]:
        con.execute(f"""COPY (SELECT * FROM {t})
            TO '{(Path(DB_FILE).parent.parent / "data" / "marts" / (t + ".parquet")).as_posix()}'
            (FORMAT PARQUET)""")
    con.close()
    print("\n[analyze] selesai — marts diekspor")


if __name__ == "__main__":
    main()
