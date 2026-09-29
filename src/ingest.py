"""
ingest.py — INGEST: unduh dataset eksperimen → staging (Parquet).

Sumber publik (tanpa API key). Idempoten. Juga menyimpan metadata eksperimen.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

from config import COOKIE_CATS_URL, EXPERIMENT, RAW, STAGING, UDACITY_AB_URL

H = {"User-Agent": "ab-testing-lab/1.0 (portfolio)"}


def _download(url: str, dest: Path) -> bytes:
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    dest.write_bytes(data)
    return data


def main() -> None:
    t0 = time.time()
    print("[ingest] mulai")

    # 1. Cookie Cats (dataset utama)
    print("[ingest] Cookie Cats...")
    b = _download(COOKIE_CATS_URL, RAW / "cookie_cats.csv")
    df = pd.read_csv(RAW / "cookie_cats.csv")
    df["retention_1"] = df["retention_1"].astype(bool)
    df["retention_7"] = df["retention_7"].astype(bool)
    df.to_parquet(STAGING / "cookie_cats.parquet", index=False)
    print(f"  → {len(df):,} pemain | versi: {df['version'].value_counts().to_dict()}")

    # 2. Udacity AB (dataset sekunder — replikasi lintas-domain)
    print("[ingest] Udacity AB...")
    try:
        _download(UDACITY_AB_URL, RAW / "udacity_ab.csv")
        ud = pd.read_csv(RAW / "udacity_ab.csv")
        ud["converted"] = ud["converted"].astype(int)
        ud.to_parquet(STAGING / "udacity_ab.parquet", index=False)
        print(f"  → {len(ud):,} baris | grup: {ud['group'].value_counts().to_dict()}")
    except Exception as e:  # noqa: BLE001
        print(f"  ! Udacity gagal ({e}) — dilewati")
        ud = pd.DataFrame()

    meta = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "experiment": EXPERIMENT["name"],
        "sources": {"cookie_cats": COOKIE_CATS_URL, "udacity_ab": UDACITY_AB_URL},
        "cookie_cats_rows": int(len(df)),
        "cookie_cats_md5": hashlib.md5(b).hexdigest(),
        "udacity_rows": int(len(ud)),
        "stages": ["control (gate_30)", "treatment (gate_40)"],
        "duration_sec": round(time.time() - t0, 2),
    }
    (STAGING / "_ingest_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[ingest] selesai dalam {meta['duration_sec']}s")


if __name__ == "__main__":
    main()
