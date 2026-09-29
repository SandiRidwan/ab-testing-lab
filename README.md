<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Orbitron&weight=900&size=34&duration=3000&pause=1000&color=6A4C93&center=true&vCenter=true&width=940&height=70&lines=A%2FB+TESTING+%26+CAUSAL+INFERENCE+LAB" alt="A/B Testing & Causal Inference Lab" />

![Python](https://img.shields.io/badge/Python-3.10+-1F5C3D?style=for-the-badge&logo=python&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-SQL-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)
![scipy](https://img.shields.io/badge/scipy-statsmodels-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

### 🔗 [**Buka A/B Testing Lab →**](https://ab-testing-lab.streamlit.app)

</div>

---

## 🧪 Apa ini?

**Analisis A/B testing yang benar** — bukan sekadar "bandingkan rata-rata".
Project ini menerapkan **statistik inferensial penuh**: uji hipotesis,
confidence interval, power analysis, koreksi multiple-testing, deteksi SRM,
efek heterogen, dan CUPED — semuanya **diuji otomatis** untuk kebenarannya.

**Studi kasus:** Cookie Cats memindahkan gate dari level 30 → 40 pada
**90.189 pemain**. Apakah keputusan itu menguntungkan?

```bash
python src/run_pipeline.py     # ingest → analyze → tests → charts
streamlit run app/dashboard.py
```

---

## 🎯 Temuan (berbasis bukti)

| Metrik | Kontrol (gate_30) | Treatment (gate_40) | Rel-lift | p (raw) | p (adj) | Signifikan? |
|---|---:|---:|---:|---:|---:|:--:|
| Retensi Hari-1 | 0.4482 | 0.4423 | **−1.32%** | 0.074 | 0.112 | ❌ |
| **Retensi Hari-7** | 0.1902 | 0.1820 | **−4.31%** | **0.0016** | **0.0047** | ✅ |
| Jumlah Ronde | 50.09 | 49.81 | −0.56% | 0.647 | 0.647 | ❌ |

**Kesimpulan:** memindahkan gate 30→40 **menurunkan retensi hari-7 secara
signifikan** (−4.31%, tetap signifikan setelah koreksi FDR).
**Rekomendasi: JANGAN** pindahkan gate ke level 40.

**Efek heterogen:** dampak terbesar pada segmen engagement menengah (Q3: −10.5%).

---

## 📊 Visualisasi

### Efek + Confidence Interval 95%

![Efek + CI](reports/figures/01_effect_ci.png)

> **Kenapa** — estimasi titik menyesatkan tanpa ketidakpastian.
> **Tujuan** — seberapa besar efeknya & seberapa yakin kita?
> **Dampak** — batang CI yang tidak melewati 0 = efek nyata. Retensi-7 jelas negatif.

### Retensi per varian

![Retensi](reports/figures/02_retention.png)

> **Kenapa** — perbedaan mentah adalah titik mulai analisis.
> **Tujuan** — gambaran deskriptif arah efek.
> **Dampak** — gate_40 lebih rendah di kedua metrik retensi.

### Power analysis

![Power](reports/figures/03_power.png)

> **Kenapa** — sampel terlalu kecil → gagal deteksi efek nyata (Type II).
> **Tujuan** — apakah kita punya cukup data?
> **Dampak** — mencegah salah tafsir "tidak signifikan" sebagai "tidak ada efek".

### Efek per segmen engagement

![Segmen](reports/figures/04_segments.png)

> **Kenapa** — efek rata-rata menyembunyikan perbedaan antar-pengguna.
> **Tujuan** — SIAPA yang terpengaruh?
> **Dampak** — dasar personalisasi / rollout bertahap.

---

## 🔬 Metode statistik

| Metode | Dipakai untuk |
|---|---|
| **2-proporsi z-test** | metrik biner (retensi) |
| **Welch t-test** | metrik kontinu (ronde), tahan varians tak-sama |
| **Bootstrap CI** | verifikasi silang CI analitis |
| **Power analysis** | n dibutuhkan & power tercapai (statsmodels) |
| **Benjamini-Hochberg FDR** | koreksi multiple-testing |
| **SRM check** (chi-square) | gerbang validitas eksperimen |
| **Efek heterogen** | lift per segmen engagement |
| **CUPED** | variance reduction (kovariat pra-periode) |

---

## 🧪 Kualitas & validitas (18 uji otomatis)

```
PASS  userid unik (unit eksperimen)
PASS  alokasi grup dekat 50:50 (SRM)
PASS  retention_7: CI mencakup estimasi
PASS  retention_7: p_adj >= p_raw
PASS  retention_7: CI & p-value konsisten
PASS  uji deterministik (p stabil)
...
[dq] SEMUA UJI LULUS
```

Uji memverifikasi **validitas statistik**, bukan hanya kebersihan data —
termasuk konsistensi antara CI dan p-value, dan determinisme uji.

---

## ⚠️ Keterbatasan (jujur)

- **Satu dataset, satu domain** (mobile game) — generalisasi perlu replikasi.
- **Uji dua-sisi** (lebih ketat, lebih jujur daripada satu-sisi).
- **Efek segmen bersifat eksploratif** — p-value segmen tidak dikoreksi
  terpisah; jangan jadikan klaim konfirmatori tanpa praregistrasi.
- **Metrik kontinu di-cap** pada persentil 99.9 (data sangat skewed).
- Klaim kausal valid selama randomisasi bersih — **terverifikasi via SRM**.

Lihat [`docs/ADR.md`](docs/ADR.md) untuk keputusan metodologis lengkap.

---

## 📁 Struktur

```
ab-testing-lab/
├── src/
│   ├── config.py          # path, definisi eksperimen, parameter statistik
│   ├── ingest.py          # unduh dataset → staging
│   ├── load_db.py         # → DuckDB
│   ├── stats.py           # ★ modul statistik (9 metode)
│   ├── analyze.py         # uji & tulis hasil ke marts
│   ├── explanations.py    # narasi Kenapa·Tujuan·Dampak
│   ├── make_charts.py     # PNG README
│   └── run_pipeline.py    # orkestrator
├── sql/{schema,transform}.sql
├── tests/test_data_quality.py   # 18 uji (data + validitas statistik)
├── app/dashboard.py       # Streamlit
├── docs/ADR.md
└── reports/figures/       # PNG
```

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt
python src/run_pipeline.py
streamlit run app/dashboard.py
```

---

## 🛠️ Tech Stack

| Layer | Teknologi |
|---|---|
| **Statistik** | scipy · statsmodels |
| **Database** | DuckDB (embedded OLAP) |
| **Pipeline** | Python stdlib + pandas |
| **Visualisasi** | Plotly · matplotlib |
| **Dashboard** | Streamlit |
| **Data** | Cookie Cats (90.189 pemain) + Udacity AB (replikasi) |

---

## 👤 Author

<div align="center">

**Sandi Ridwan** — Data Analyst · Data Automation Engineer · Python

📍 Palu, Central Sulawesi, Indonesia

[![Upwork](https://img.shields.io/badge/Upwork-Hire_Me-6A4C93?style=for-the-badge&logo=upwork&logoColor=white)](https://www.upwork.com/freelancers/~011f6d0fbb4a372974)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/sandi-ridwan)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/SandiRidwan)

</div>

## 📄 License

MIT — Educational & portfolio. Dataset Cookie Cats (publik, Kaggle/GitHub).
