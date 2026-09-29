"""
test_data_quality.py — uji kualitas data & validitas eksperimen (CI-friendly).

Selain uji data standar, file ini memverifikasi VALIDITAS STATISTIK:
  · SRM (alokasi grup seimbang)
  · CI mencakup efek (konsistensi)
  · p-value terkoreksi >= p-value mentah (sifat BH)
  · reproduktibilitas uji (deterministik)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import duckdb

from config import DB_FILE

FAILS: list[str] = []
PASSES: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        PASSES.append(name)
        print(f"  PASS  {name}")
    else:
        FAILS.append(f"{name} — {detail}")
        print(f"  FAIL  {name}  {detail}")


def main() -> int:
    con = duckdb.connect(str(DB_FILE), read_only=True)
    print("[dq] uji kualitas data & validitas eksperimen\n")

    # ---- 1. Data mentah ---------------------------------------------------
    n = con.execute("SELECT count(*) FROM stg_cookie_cats").fetchone()[0]
    u = con.execute("SELECT count(DISTINCT userid) FROM stg_cookie_cats").fetchone()[0]
    check("userid unik (unit eksperimen)", n == u, f"{n} vs {u}")

    nv = con.execute("SELECT count(DISTINCT version) FROM stg_cookie_cats").fetchone()[0]
    check("tepat 2 varian", nv == 2, f"{nv} varian")

    bad = con.execute("SELECT count(*) FROM stg_cookie_cats WHERE sum_gamerounds < 0").fetchone()[0]
    check("sum_gamerounds >= 0", bad == 0, f"{bad} negatif")

    nulls = con.execute("""SELECT count(*) FROM stg_cookie_cats
        WHERE retention_1 IS NULL OR retention_7 IS NULL
           OR version IS NULL""").fetchone()[0]
    check("kolom wajib tidak null", nulls == 0, f"{nulls} null")

    # ---- 2. SRM (validitas eksperimen) -----------------------------------
    srm_p = con.execute("""
        SELECT 1 FROM mart_srm LIMIT 1
    """).fetchone()
    if srm_p:
        lo, hi = con.execute("SELECT min(n), max(n) FROM mart_srm").fetchone()
        ratio = lo / (lo + hi)
        check("alokasi grup dekat 50:50 (SRM)", 0.48 <= ratio <= 0.52,
              f"rasio={ratio:.4f}")

    # ---- 3. Konsistensi hasil uji ---------------------------------------
    r = con.execute("""SELECT metric, abs_lift, ci_low, ci_high, p_value,
        p_value_adj, signifikan_adj FROM mart_test_results""").fetchall()
    check("ada hasil uji", len(r) >= 3, f"{len(r)} hasil")

    for m, lift, lo, hi, p, p_adj, sig in r:
        # CI harus mencakup titik estimasi (lift)
        check(f"{m}: CI mencakup estimasi", lo <= lift <= hi,
              f"lift={lift:.4f} bukan di [{lo:.4f},{hi:.4f}]")
        # p terkoreksi >= p mentah (BH hanya menaikkan)
        check(f"{m}: p_adj >= p_raw", p_adj >= p - 1e-9,
              f"p={p:.5f} p_adj={p_adj:.5f}")

    # signifikansi harus konsisten: CI eksklusif-0 <=> p<alpha (dua sisi)
    for m, lift, lo, hi, p, p_adj, sig in r:
        ci_excl0 = (lo > 0) or (hi < 0)
        consistent = (ci_excl0 == (p < 0.05))
        check(f"{m}: CI & p-value konsisten", consistent,
              f"CI di-0={ci_excl0}, p<0.05={(p<0.05)}")

    # ---- 4. Power ---------------------------------------------------------
    pw = con.execute("SELECT count(*) FROM mart_power").fetchone()[0]
    check("power analysis tersedia", pw >= 3, f"{pw} baris")

    # ---- 5. Segmen --------------------------------------------------------
    seg = con.execute("SELECT count(*) FROM mart_segment_effects").fetchone()[0]
    check("efek per segmen tersedia", seg >= 3, f"{seg} baris")

    # ---- 6. Reproduktibilitas (uji deterministik) ------------------------
    # p-value identik bila dijalankan ulang dari data sama
    from stats import test_proportion  # noqa: E402
    r1 = test_proportion(500, 1000, 520, 1000)
    r2 = test_proportion(500, 1000, 520, 1000)
    check("uji deterministik (p stabil)", r1["p_value"] == r2["p_value"],
          "p berubah antar-perhitungan")

    con.close()
    print(f"\n[dq] {len(PASSES)} lulus, {len(FAILS)} gagal")
    if FAILS:
        print("\nGAGAL:")
        for f in FAILS:
            print("  -", f)
        return 1
    print("[dq] SEMUA UJI LULUS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
