"""
load_db.py — muat staging (Parquet) ke DuckDB. Idempoten.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb

from config import DB_FILE, SQL, STAGING


def main() -> None:
    con = duckdb.connect(str(DB_FILE))
    print(f"[load] database → {DB_FILE}")
    con.execute((SQL / "schema.sql").read_text(encoding="utf-8"))

    cc = STAGING / "cookie_cats.parquet"
    if not cc.exists():
        raise SystemExit("staging cookie_cats tidak ada — jalankan ingest.py")

    con.execute("DELETE FROM stg_cookie_cats")
    con.execute(f"""
        INSERT INTO stg_cookie_cats
        SELECT userid, version, sum_gamerounds, retention_1, retention_7
        FROM read_parquet('{cc.as_posix()}')
    """)
    n_cc = con.execute("SELECT count(*) FROM stg_cookie_cats").fetchone()[0]

    ud = STAGING / "udacity_ab.parquet"
    n_ud = 0
    if ud.exists():
        con.execute("DELETE FROM stg_udacity_ab")
        con.execute(f"""
            INSERT INTO stg_udacity_ab
            SELECT user_id, timestamp, "group", landing_page, converted
            FROM read_parquet('{ud.as_posix()}')
        """)
        n_ud = con.execute("SELECT count(*) FROM stg_udacity_ab").fetchone()[0]

    print(f"[load] stg_cookie_cats : {n_cc:,} baris")
    if n_ud:
        print(f"[load] stg_udacity_ab : {n_ud:,} baris")

    v = con.execute("""SELECT version, count(*) n,
        round(avg(sum_gamerounds),1) avg_rounds,
        round(avg(CASE WHEN retention_1 THEN 1 ELSE 0 END)*100,2) r1,
        round(avg(CASE WHEN retention_7 THEN 1 ELSE 0 END)*100,2) r7
        FROM stg_cookie_cats GROUP BY version ORDER BY version""").fetchall()
    print("[load] ringkasan varian:")
    for r in v:
        print(f"   {r[0]:8} n={r[1]:,}  rounds={r[2]}  ret1={r[3]}%  ret7={r[4]}%")
    con.close()


if __name__ == "__main__":
    main()
