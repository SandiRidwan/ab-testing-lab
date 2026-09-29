"""
explanations.py — narasi Kenapa · Tujuan · Dampak untuk setiap elemen.

Standar: setiap metrik/uji menjelaskan kenapa dipilih, apa yang dijawab,
dan keputusan apa yang timbul — plus cara membaca bila tidak intuitif.
"""

from __future__ import annotations

EXPLAIN: dict[str, dict] = {
    "kpi": {
        "judul": "Ringkasan Eksperimen (KPI)",
        "kenapa": "Sebelum masuk statistik, pembaca butuh konteks: berapa sampel, "
                  "grup apa, dan varian mana yang lebih baik secara deskriptif.",
        "tujuan": "Menjawab: eksperimen ini tentang apa, dan seberapa besar?",
        "dampak": "Ukuran sampel menentukan seberapa halus efek yang bisa "
                  "dideteksi; bila sampel kecil, efek kecil tak terdeteksi.",
        "baca": "Angka di sini DESKRIPTIF — belum tentang signifikansi.",
    },
    "result_table": {
        "judul": "Hasil Uji Statistik per Metrik",
        "kenapa": "Perbedaan mentah bisa terjadi karena kebetulan. Uji "
                  "signifikansi memisahkan sinyal dari derau.",
        "tujuan": "Menjawab: apakah perbedaan antar-varian nyata atau kebetulan?",
        "dampak": "Keputusan rilis produk HARUS berbasis p-value + CI yang "
                  "dikoreksi, bukan hanya angka mentah yang tampak lebih besar.",
        "baca": "p-value < 0.05 (setelah koreksi) = signifikan. CI yang tidak "
                "mencakup 0 = efek nyata. Lihat kolom p_adj untuk koreksi.",
    },
    "ci_plot": {
        "judul": "Efek + Confidence Interval 95%",
        "kenapa": "Estimasi titik (mis. -4.3%) menyesatkan tanpa ketidakpastian. "
                  "CI menunjukkan rentang nilai yang masuk akal.",
        "tujuan": "Menjawab: seberapa besar efeknya, dan seberapa yakin kita?",
        "dampak": "CI lebar = data belum cukup untuk keputusan tegas; CI sempit "
                  "jauh dari 0 = keputusan dapat diambil. CI yang menyentuh 0 = "
                  "belum yakin arah efeknya.",
        "baca": "Garis = estimasi; batang horizontal = CI 95%. Bila batang "
                "tidak melewati garis 0, efek signifikan.",
    },
    "power": {
        "judul": "Power Analysis",
        "kenapa": "Eksperimen tanpa perhitungan power berisiko: sampel terlalu "
                  "kecil → gagal deteksi efek nyata (Type II error).",
        "tujuan": "Menjawab: apakah kita punya cukup data untuk mendeteksi efek "
                  "sebesar yang dicari?",
        "dampak": "Bila n aktual < n dibutuhkan, hasil 'tidak signifikan' bisa "
                  "berarti 'belum cukup data', bukan 'tidak ada efek'. Ini "
                  "mencegah kesimpulan salah.",
        "baca": "n_req = sampel dibutuhkan per grup; bandingkan dengan n aktual. "
                "Power ≥ 0.80 dianggap layak.",
    },
    "srm": {
        "judul": "SRM — Sample Ratio Mismatch",
        "kenapa": "Jika alokasi grup tidak dekat 50:50, eksperimen mungkin cacat "
                  "(bug randomisasi). Hasilnya tak dapat dipercaya apa pun angkanya.",
        "tujuan": "Menjawab: apakah pembagian grup seperti yang direncanakan?",
        "dampak": "SRM terdeteksi (p<0.001) → STOP, perbaiki eksperimen sebelum "
                  "menyimpulkan apa pun. Ini gerbang validitas.",
        "baca": "p tinggi (>0.05) = alokasi normal. p sangat rendah = curiga SRM.",
    },
    "segments": {
        "judul": "Efek Heterogen per Segmen Engagement",
        "kenapa": "Efek rata-rata menyembunyikan perbedaan: sebuah fitur bisa "
                  "merugikan sebagian pengguna dan menguntungkan yang lain.",
        "tujuan": "Menjawab: SIAPA yang terpengaruh, bukan hanya rata-ratanya?",
        "dampak": "Dasar personalisasi / rollout bertahap. Jika efek negatif "
                  "terkonsentrasi di segmen nilai-tinggi, risikonya jauh lebih "
                  "besar dari angka rata-rata.",
        "baca": "Kuartil berdasarkan engagement (ronde). Q4 = pengguna paling "
                "aktif. Lift per segmen menunjukkan di mana dampak terkonsentrasi.",
    },
    "cuped": {
        "judul": "CUPED — Variance Reduction",
        "kenapa": "Sebagian besar variasi antar-pengguna adalah 'derau' bawaan "
                  "(sebagian orang memang main lebih banyak). CUPED mengurangi "
                  "derau itu memakai data pra-eksperimen.",
        "tujuan": "Mendapat sensitivitas lebih tinggi (CI lebih sempit) TANPA "
                  "menambah sampel / memperpanjang eksperimen.",
        "dampak": "Efek nyata lebih cepat terdeteksi → eksperimen lebih singkat "
                  "& keputusan lebih cepat, tanpa menambah risiko statistik.",
        "baca": "Menurunkan varians ≥ 20% dianggap bermanfaat. CUPED tidak "
                "mengubah ekspektasi efek, hanya presisinya.",
    },
    "conclusion": {
        "judul": "Kesimpulan & Rekomendasi",
        "kenapa": "Analisis tanpa rekomendasi tidak berguna bagi pengambil "
                  "keputusan. Ini jembatan dari statistik ke tindakan.",
        "tujuan": "Menyarikan temuan menjadi keputusan yang dapat dipertanggungjawabkan.",
        "dampak": "Rekomendasi eksplisit dengan tingkat keyakinan & risiko yang "
                  "dinyatakan — bukan klaim berlebihan.",
        "baca": "Setiap rekomendasi mengacu pada bukti (p-value, CI, power) di atas.",
    },
    "limitations": {
        "judul": "Keterbatasan & Peringatan (jujur)",
        "kenapa": "Kejujuran statistik adalah bagian dari kualitas. Menyembunyikan "
                  "asumsi/risiko menyesatkan pengambil keputusan.",
        "tujuan": "Menyatakan apa yang TIDAK bisa disimpulkan dari analisis ini.",
        "dampak": "Mencegah overclaim (mis. menyebut efek kecil 'menang') dan "
                  "mendorong replikasi bila perlu.",
        "baca": "Lihat docs/ADR.md untuk keputusan metodologis lengkap.",
    },
    "method": {
        "judul": "Metodologi & Sumber",
        "kenapa": "Hasil harus dapat ditelusuri & direproduksi.",
        "tujuan": "Menjelaskan sumber data & metode statistik yang dipakai.",
        "dampak": "Pemangku kepentingan dapat memverifikasi & menjalankan ulang.",
        "baca": "Uji otomatis memverifikasi validitas (SRM, konsistensi CI↔p).",
    },
}


def text(key: str) -> str:
    e = EXPLAIN.get(key)
    if not e:
        return ""
    p = [f"**{e['judul']}**", f"- **Kenapa:** {e['kenapa']}",
         f"- **Tujuan:** {e['tujuan']}", f"- **Dampak:** {e['dampak']}"]
    if e.get("baca"):
        p.append(f"- **Cara baca:** {e['baca']}")
    return "\n".join(p)


def render(key: str, expanded: bool = False, st=None) -> None:
    if st is None:
        import streamlit as st  # noqa
    e = EXPLAIN.get(key)
    if not e:
        return
    with st.expander(f"💡 {e['judul']} — Kenapa · Tujuan · Dampak",
                     expanded=expanded):
        st.markdown(
            f"**🔎 Kenapa** — {e['kenapa']}\n\n"
            f"**🎯 Tujuan** — {e['tujuan']}\n\n"
            f"**📈 Dampak** — {e['dampak']}")
        if e.get("baca"):
            st.caption(f"👁️ Cara baca: {e['baca']}")


def audit(verbose: bool = True) -> bool:
    ok = True
    for k, v in EXPLAIN.items():
        miss = [f for f in ("kenapa", "tujuan", "dampak") if not v.get(f)]
        if miss:
            ok = False
            if verbose:
                print(f"  MISSING {k}: {miss}")
    if verbose:
        print(f"Penjelasan: {len(EXPLAIN)} | "
              f"{'SEMUA LENGKAP' if ok else 'ADA YANG KURANG'}")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if audit() else 1)
