"""
decide_actions.py — decision engine untuk keputusan rilis fitur A/B test.

Mengubah hasil uji statistik menjadi KEPUTUSAN RILIS terukur (bukan sekadar
"p-value < 0.05"). Sinyal:
  · lift_positive — arah & besar efek menguntungkan (dinormalisasi)
  · significance  — kekuatan bukti (dari p-value terkoreksi)
  · power         — apakah sampel memadai (power/ n cukup)
Bobot: 0.4 / 0.4 / 0.2. Tier:
  · rilis          (>=0.7 & efek positif signifikan) — aman dirilis
  · uji_lanjut     (>=0.4)  — bukti belum konklusif
  · jangan_rilis   (<0.4)   — efek negatif/tidak aman
Output: marts/mart_decisions.parquet
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb
import pandas as pd

from config import DB_FILE, MARTS
from decision import decide, normalize

WEIGHTS = {"evidence": 0.4, "effect": 0.4, "power": 0.2}
THRESHOLDS = {"rilis": 0.70, "uji_lanjut": 0.40}
OUT = "mart_decisions"


def main() -> None:
    con = duckdb.connect(str(DB_FILE))
    tests = con.execute("SELECT * FROM mart_test_results").df()
    power = con.execute("SELECT * FROM mart_power").df()
    con.close()

    if tests.empty:
        print("[decision] tidak ada hasil uji")
        return

    pw_map = power.set_index("metric")["cukup"].to_dict() if len(power) else {}

    payload = []
    for _, r in tests.iterrows():
        p = max(r.p_value_adj, 1e-9)
        # evidence: -log10(p_adj) dinormalisasi ke [0,1]; p kecil → bukti kuat
        evidence = max(0.0, min(1.0, (-math.log10(p)) / 3.0))
        # effect: HANYA efek positif yang dinilai baik. Efek <=0 → 0.
        # Skala: +5% relatif atau lebih → 1.0. Inilah yang benar: fitur yang
        # menurunkan metrik TIDAK layak dirilis, sebesar apa pun.
        effect = max(0.0, min(1.0, r.rel_lift_pct / 5.0))
        power_sig = 1.0 if pw_map.get(r.metric, False) else 0.5
        payload.append({
            "id": r.metric,
            "signals": {"evidence": evidence, "effect": effect,
                        "power": power_sig},
            "weights": WEIGHTS, "thresholds": THRESHOLDS,
            "rel_lift_pct": r.rel_lift_pct, "p_adj": r.p_value_adj,
            "signifikan": bool(r.signifikan_adj),
        })

    dec = decide(payload)
    # GUARDRAIL: efek negatif yang SIGNIFIKAN tidak boleh lolos ke tier rilis/
    # uji_lanjut — paksa 'jangan_rilis'. Ini mencegah "skor tinggi dari evidence
    # kuat" menyamarkan kerugian nyata.
    mask = (dec.rel_lift_pct < 0) & (dec.signifikan)
    if mask.any():
        dec.loc[mask, "tier"] = "jangan_rilis"
        dec.loc[mask, "justifikasi"] = (
            dec.loc[mask, "rel_lift_pct"].apply(
                lambda v: f"GUARDRAIL: efek negatif signifikan ({v:+.2f}%) → "
                          f"jangan rilis, apa pun kekuatan buktinya."))
    con = duckdb.connect(str(DB_FILE))
    con.execute(f"DROP TABLE IF EXISTS {OUT}")
    con.execute(f"CREATE TABLE {OUT} AS SELECT * FROM dec")
    con.execute(f"""COPY {OUT} TO '{(MARTS / (OUT + '.parquet')).as_posix()}'
        (FORMAT PARQUET)""")
    con.close()

    print(f"[decision] {len(dec)} metrik → keputusan rilis:")
    for _, r in dec.iterrows():
        print(f"   [{r['tier']:12}] skor={r['skor']:.2f}  {r['id']:18} "
              f"lift={r['rel_lift_pct']:+.2f}%  p_adj={r['p_adj']:.4f}")
        print(f"      {r['justifikasi']}")


if __name__ == "__main__":
    main()
