"""
rebuild_from_marts.py — bangun DuckDB langsung dari marts Parquet yang
di-commit (tanpa ingest / kredensial). Berguna untuk CI & verifikasi cepat.

Membuat tabel <nama> dari tiap data/marts/<nama>.parquet di DB_FILE.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import duckdb

from config import DB_FILE, MARTS


def main() -> None:
    parquets = sorted(MARTS.glob("*.parquet"))
    if not parquets:
        raise SystemExit("tidak ada marts Parquet — jalankan pipeline dulu")
    con = duckdb.connect(str(DB_FILE))
    for p in parquets:
        name = p.stem
        con.execute(f"DROP TABLE IF EXISTS {name}")
        con.execute(f"""CREATE TABLE {name} AS
            SELECT * FROM read_parquet('{p.as_posix()}')""")
        n = con.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
        print(f"[rebuild] {name:32} {n:6} baris")
    con.close()
    print(f"[rebuild] {len(parquets)} tabel → {DB_FILE}")


if __name__ == "__main__":
    main()
