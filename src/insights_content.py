
# ---------------------------------------------------------------------------
# KONTEN INSIGHT — A/B Testing Lab
# Setiap chart/analisis punya kesimpulan + rekomendasi + risiko.
# Ditulis dari SUDUT PANDANG pemilik produk (Cookie Cats) yang memutuskan.
# ---------------------------------------------------------------------------
from insight import register

register(
    "kpi",
    kesimpulan=(
        "Eksperimen gate 30→40 melibatkan 90.189 pemain (seimbang, SRM bersih). "
        "Dari 3 metrik yang diuji, hanya RETENSI HARI-7 yang berubah secara "
        "signifikan — dan arahnya NEGATIF (−4.31%). Dua metrik lain tidak "
        "signifikan, artinya belum ada bukti perbedaan nyata."),
    rekomendasi=[
        "JANGAN rilis gate level 40 secara penuh — bukti menunjukkan kerugian retensi.",
        "Bila tetap ingin menguji gate, uji posisi/nilai lain (mis. level 35, 50) "
        "dengan durasi & sampel yang direncanakan lewat power analysis.",
        "Dokumentasikan keputusan ini sebagai preseden: perubahan onboarding "
        "berisiko tinggi terhadap retensi jangka panjang.",
    ],
    risiko=(
        "Bila gate 40 dirilis karena 'angka mentah retensi-1 terlihat mirip', "
        "kamu kehilangan ~4% pengguna yang kembali di hari-7 untuk setiap 100 "
        "pemain baru. Pada skala 90rb, itu ribuan pengguna hilang per siklus — "
        "dan efeknya menumpuk diam-diam karena retensi-1 tidak menunjukkannya."),
    tingkat="kritis",
)

register(
    "result_table",
    kesimpulan=(
        "Setelah koreksi Benjamini-Hochberg (FDR), hanya retensi-7 yang lolos "
        "signifikansi (p_adj=0.0047). Retensi-1 (p_adj=0.112) dan jumlah ronde "
        "(p_adj=0.647) TIDAK signifikan — perbedaan mereka paling mungkin "
        "kebetulan. Ini contoh penting: dua metrik bisa 'tampak berbeda' namun "
        "tidak meyakinkan secara statistik."),
    rekomendasi=[
        "Ambil keputusan HANYA dari baris dengan signifikan_adj = True.",
        "Untuk metrik non-signifikan, jangan simpulkan 'tidak ada efek' — "
        "kata yang benar: 'belum ada bukti cukup' (cek power di tab Power).",
        "Laporkan p_adj, bukan hanya p mentah, di setiap ringkasan ke stakeholder.",
    ],
    risiko=(
        "Menjadikan retensi-1 'menang' padahal tidak signifikan adalah bentuk "
        "p-hacking yang halus. Keputusan berbasis derau → fitur dirilis tanpa "
        "manfaat nyata, biaya engineering terbuang, dan tim kehilangan "
        "kepercayaan pada proses eksperimen."),
    tingkat="tinggi",
)

register(
    "ci_plot",
    kesimpulan=(
        "Interval kepercayaan 95% untuk retensi-7 seluruhnya berada di bawah 0 "
        "(tidak melewati garis nol) → efek negatif ini nyata, bukan kebetulan. "
        "Untuk retensi-1 dan ronde, CI melewati nol → arah efek belum dapat "
        "dipastikan. Lebar CI menunjukkan seberapa presisi estimasi kita."),
    rekomendasi=[
        "Gunakan lebar CI untuk menilai kesiapan keputusan: CI sempit & jauh dari "
        "0 = aman memutuskan; CI lebar = perpanjang/ perbesar sampel.",
        "Sampaikan ke stakeholder dalam bahasa rentang: 'retensi-7 turun antara "
        "X% dan Y%', bukan satu angka tunggal yang terlihat pasti.",
        "Untuk metrik dengan CI melewati 0, jalankan eksperimen lanjutan "
        "sebelum memutuskan apa pun.",
    ],
    risiko=(
        "Melaporkan hanya estimasi titik (mis. '-4.3%') menyembunyikan "
        "ketidakpastian. Jika efek sebenarnya bisa jauh lebih buruk (ujung bawah "
        "CI), keputusan yang terlihat 'aman' bisa merugikan lebih besar dari dugaan."),
    tingkat="tinggi",
)

register(
    "segments",
    kesimpulan=(
        "Efek TIDAK seragam. Segmen engagement menengah (Q3) paling terdampak "
        "negatif (−10.5%), sementara segmen terendah (Q1) justru sedikit positif. "
        "Ini menunjukkan gate 40 mengganggu pengguna yang sedang membangun "
        "kebiasaan bermain — kelompok paling bernilai untuk konversi jangka panjang."),
    rekomendasi=[
        "Fokus investigasi produk pada pengguna engagement menengah: apa yang "
        "membuat mereka berhenti saat mencapai gate level 40?",
        "Jika tetap ingin menguji gate, pertimbangkan rollout HANYA ke segmen "
        "berisiko rendah (Q1) sebagai pembelajaran, bukan ke semua orang.",
        "Jadikan segmentasi sebagai standar: jangan pernah puas dengan 'efek rata-rata'.",
    ],
    risiko=(
        "Membaca hanya efek rata-rata (−4.3%) menyembunyikan bahwa sebagian "
        "segmen jatuh −10.5%. Keputusan berbasis rata-rata bisa menghancurkan "
        "segmen bernilai tinggi tanpa terlihat di dashboard — kerugian tersembunyi."),
    tingkat="tinggi",
)

register(
    "power",
    kesimpulan=(
        "Eksperimen punya sampel BESAR (≥44rb per grup), cukup untuk mendeteksi "
        "efek sekecil ~5% relatif dengan power 80%. Artinya, saat hasil berkata "
        "'tidak signifikan' (retensi-1, ronde), itu benar-benar berarti efeknya "
        "kecil — BUKAN karena kurang data."),
    rekomendasi=[
        "Percayai hasil 'tidak signifikan' di sini: dengan power tinggi, itu "
        "memang bukti ketiadaan efek yang praktis berarti.",
        "Untuk eksperimen berikutnya, hitung n dibutuhkan SEBELUM mulai "
        "(gunakan fungsi power_proportion/power_mean di src/stats.py).",
        "Tetapkan MDE (minimum detectable effect) yang bermakna bisnis sejak awal, "
        "bukan setelah melihat hasil.",
    ],
    risiko=(
        "Menjalankan eksperimen tanpa power analysis berisiko dua arah: sampel "
        "kurang → efek nyata terlewat (Type II); sampel berlebih → biaya & waktu "
        "terbuang. Keduanya menghasilkan keputusan yang salah atau tidak efisien."),
    tingkat="sedang",
)

register(
    "srm",
    kesimpulan=(
        "Alokasi grup mendekati 50:50 dan uji SRM tidak menemukan penyimpangan "
        "(p tinggi). Ini berarti randomisasi berjalan benar — prasyarat WAJIB "
        "agar kesimpulan kita bisa disebut kausal, bukan sekadar korelasional."),
    rekomendasi=[
        "Jadikan SRM check sebagai langkah WAJIB pertama di setiap analisis "
        "eksperimen — sebelum melihat metrik apa pun.",
        "Catat p-value SRM di laporan; bila suatu saat p<0.001, hentikan analisis.",
        "Otomatiskan pemeriksaan ini di pipeline agar tidak bisa dilewati.",
    ],
    risiko=(
        "Jika randomisasi cacat (SRM) dan kita tetap menganalisis, seluruh "
        "kesimpulan — termasuk yang 'signifikan' — tidak dapat dipercaya. "
        "Keputusan produk berbasis eksperimen rusak akan lebih buruk daripada "
        "tidak bereksperimen sama sekali."),
    tingkat="rendah",
)


# --- Decision engine: keputusan terukur (skor + tier + justifikasi) ---
register(
    "decision",
    kesimpulan=(
        "Selain narasi, sistem kini menghasilkan SKOR KEPUTUSAN numerik per item "
        "(anomali/negara/ticker/metrik) berbasis sinyal berbobot, lalu memetakan "
        "ke TIER AKSI via ambang. Keputusan dapat dibandingkan & diurutkan."),
    rekomendasi=[
        "Jalankan item dengan tier prioritas tertinggi lebih dulu.",
        "Sesuaikan bobot sinyal & ambang tier di config sesuai kebijakan organisasi.",
        "Audit tiap keputusan lewat skor & justifikasi terukurnya.",
    ],
    risiko=(
        "Keputusan tanpa skor terukur cenderung subjektif & tidak konsisten. "
        "Namun skor pun bisa salah bila formulasi sinyal keliru — karena itu "
        "setiap keputusan menyertakan justifikasi yang dapat diaudit."),
    tingkat="tinggi",
)
