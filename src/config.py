"""
config.py — satu sumber kebenaran: path, sumber, konstanta, parameter statistik.

Project: A/B Testing & Causal Inference Lab
Dataset: Cookie Cats (90.189 pemain) — eksperimen memindahkan gate level 30→40.
Sumber: GitHub raw (publik, tanpa API key).
"""

from __future__ import annotations

from pathlib import Path

# ---- Path -----------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
STAGING = DATA / "staging"
MARTS = DATA / "marts"
DB = ROOT / "db"
SQL = ROOT / "sql"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"

for _p in (RAW, STAGING, MARTS, DB, REPORTS, FIGURES):
    _p.mkdir(parents=True, exist_ok=True)

DB_FILE = DB / "experiment.duckdb"

# ---- Sumber ----------------------------------------------------------------
COOKIE_CATS_URL = ("https://raw.githubusercontent.com/ryanschaub/"
                   "Mobile-Games-A-B-Testing-with-Cookie-Cats/master/"
                   "cookie_cats.csv")
UDACITY_AB_URL = ("https://raw.githubusercontent.com/ahujaya/"
                  "Analyze-AB-Test-Results-Python/main/ab_data.csv")

# ---- Definisi eksperimen ---------------------------------------------------
EXPERIMENT = {
    "name": "Cookie Cats — Gate Level 30 vs 40",
    "control": "gate_30",
    "treatment": "gate_40",
    "unit": "pemain (userid)",
    "metrics": {
        "retention_1": {"tipe": "biner", "label": "Retensi Hari-1",
                        "arah": "lebih tinggi lebih baik"},
        "retention_7": {"tipe": "biner", "label": "Retensi Hari-7",
                        "arah": "lebih tinggi lebih baik"},
        "sum_gamerounds": {"tipe": "kontinu", "label": "Jumlah Ronde",
                            "arah": "lebih tinggi lebih baik"},
    },
}

# ---- Parameter statistik ---------------------------------------------------
ALPHA = 0.05                 # tingkat signifikansi
POWER = 0.80                 # target statistical power
MDE_REL = 0.05               # minimum detectable effect (relatif) yang dicari
N_BOOTSTRAP = 2000           # iterasi bootstrap untuk CI
SEED = 42

# ---- Palet warna -----------------------------------------------------------
COLORS = {
    "control": "#2E6F95", "treatment": "#1F5C3D",
    "primary": "#1F5C3D", "accent": "#E4A11B", "red": "#C0392B",
    "grey": "#8B9AA6", "purple": "#6A4C93", "teal": "#2A9D8F",
}
