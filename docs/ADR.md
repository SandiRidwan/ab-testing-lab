# ADR — A/B Testing & Causal Inference Lab

## ADR-001: Dataset — Cookie Cats (publik)

**Status:** Diputuskan
**Konteks:** Butuh dataset A/B nyata, terbuka, dengan ≥1 metrik biner & kontinu.

**Investigasi sumber:**

| Dataset | Status uji | Dipakai |
|---|---|---|
| Cookie Cats (`ryanschaub/…`) | 200, 90.189 pemain, 2 retensi + ronde | ✅ utama |
| Udacity AB (`ahujaya/…`) | 200, 294k baris, konversi biner | ✅ sekunder (replikasi) |
| Criteo Uplift | URL bukan CSV langsung | ❌ |
| Cookie Cats (mirror lain) | 404 | ❌ |

**Keputusan:** Cookie Cats utama (kaya: biner + kontinu), Udacity untuk replikasi.
**Alasan:** eksperimen nyata (gate 30→40), sampel besar (power sehat), terbuka.
**Konsekuensi:** satu domain (game); generalisasi perlu replikasi.

---

## ADR-002: Metode statistik (bukan hanya deskriptif)

**Status:** Diputuskan
**Konteks:** Banyak "portofolio A/B testing" hanya bandingkan rata-rata.
**Keputusan:** Implementasi metode inferensial lengkap:
- 2-proporsi z-test & Welch t-test (bukan Student — varians tak diasumsikan sama)
- CI 95% analitis **+ bootstrap** (verifikasi silang)
- Power analysis (n dibutuhkan & power tercapai)
- Koreksi **Benjamini-Hochberg** (FDR) untuk multiple-testing
- **SRM check** (chi-square) sebagai gerbang validitas
- Efek heterogen per segmen + CUPED (variance reduction)
**Alasan:** menunjukkan pemahaman statistik yang benar, bukan sekadar tooling.
**Konsekuensi:** lebih rumit; diuji otomatis (tests) untuk menjaga kebenaran.

---

## ADR-003: Welch t-test untuk metrik kontinu

**Status:** Diputuskan
**Konteks:** `sum_gamerounds` sangat skewed (mayoritas 0–50, ekor hingga 49.854).
**Keputusan:** Welch t-test + cap outlier di persentil 99.9 + catat keterbatasan.
**Alasan:** Student t-test mengasumsikan varians sama (tidak valid di sini);
Welch lebih tahan. Cap mencegah 1 outlier ekstrem mendominasi mean.
**Konsekuensi:** hasil pada data ter-cap; metrik alternatif (median/quantile)
disarankan untuk analisis lanjutan (dicatat di keterbatasan).

---

## ADR-004: Koreksi multiple-testing (BH-FDR)

**Status:** Diputuskan
**Konteks:** Menguji banyak metrik meningkatkan risiko Type I error.
**Keputusan:** Benjamini-Hochberg FDR (bukan Bonferroni).
**Alasan:** BH lebih powerful (mengendalikan proporsi false discovery), standar
di industri A/B modern; Bonferroni terlalu konservatif untuk banyak metrik.
**Konsekuensi:** p_adj dilaporkan berdampingan dengan p mentah; signifikansi
final memakai p_adj.

---

## ADR-005: DuckDB (konsisten dengan project lain)

**Status:** Diputuskan
**Keputusan:** DuckDB (embedded OLAP) untuk staging & marts.
**Alasan:** portabel, nol infra, SQL penuh. Konsisten lintas portofolio.
**Konsekuensi:** data cloud disajikan via marts Parquet yang di-commit.

---

## ADR-006: Randomisasi & klaim kausal

**Status:** Diputuskan
**Konteks:** Klaim "X menyebabkan Y" hanya valid bila randomisasi berjalan.
**Keputusan:** Verifikasi SRM (chi-square) sebelum menyimpulkan kausal; bila
SRM terdeteksi → STOP.
**Alasan:** integritas inferensi kausal bergantung pada validitas desain.
**Konsekuensi:** bila data tidak menunjukkan SRM (ini kasusnya), klaim efek
dapat diberi label kausal dengan percaya diri terbatas pada populasi eksperimen.
