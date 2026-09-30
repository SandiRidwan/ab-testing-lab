
# ---------------------------------------------------------------------------
# KONTEN INSIGHT — A/B Testing Lab
# Setiap chart/analisis punya kesimpulan + rekomendasi + risiko.
# Ditulis dari SUDUT PANDANG pemilik produk (Cookie Cats) yang memutuskan.
#
# Format rekomendasi = KAYA (v2): {aksi, langkah[], metrik, pemilik}
#   · aksi    — judul tindakan singkat
#   · langkah — langkah konkret & data-driven (angka nyata dari eksperimen)
#   · metrik  — cara mengukur keberhasilan (terukur)
#   · pemilik — siapa yang mengeksekusi (spesifik)
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
        {
            "aksi": "JANGAN rilis gate level 40 secara penuh — bukti menunjukkan kerugian retensi.",
            "langkah": [
                "Hentikan rencana rollout gate_40; pertahankan gate_30 sebagai default produksi.",
                "Kunci temuan utama: retensi hari-7 turun dari 0.1902 (gate_30) ke 0.1820 "
                "(gate_40) = −4.31% (p=0.0016, p_adj=0.0047 signifikan setelah koreksi FDR).",
                "Cek metrik sekunder (retensi-1 0.4423 vs 0.4482; ronde) — catat bahwa keduanya "
                "TIDAK signifikan sehingga tidak boleh dipakai sebagai alasan merilis.",
                "Sebar ringkasan keputusan 'no-go' ke stakeholder dalam ≤1 minggu dengan angka di atas.",
            ],
            "metrik": "Gate_40 tidak menjadi default di produksi; 0% trafik baru masuk gate_40 setelah keputusan.",
            "pemilik": "Product Owner (pemilik Cookie Cats) + Head of Growth",
        },
        {
            "aksi": "Bila tetap ingin menguji gate, uji posisi/nilai lain (mis. level 35, 50) dengan durasi & sampel yang direncanakan lewat power analysis.",
            "langkah": [
                "Tetapkan MDE bisnis yang bermakna (mis. 2% relatif pada retensi-7) sebelum mulai.",
                "Hitung n per grup lewat power_proportion (power 80%, α=0.05) — bandingkan dengan "
                "≈44rb/pemain per grup yang sudah terbukti cukup mendeteksi efek ~5%.",
                "Rancang arm gate_35 dan gate_50 dengan alokasi 50:50 dan durasi tetap (jangan "
                "mengintip lalu berhenti lebih awal).",
                "Registrasikan hipotesis + metrik primer (retensi-7) sebelum data terkumpul agar "
                "tidak ada p-hacking.",
            ],
            "metrik": "Dokumen power analysis (n & MDE) disetujui sebelum eksperimen jalan; SRM bersih saat analisis.",
            "pemilik": "Experiment Owner / Data Scientist",
        },
        {
            "aksi": "Dokumentasikan keputusan ini sebagai preseden: perubahan onboarding berisiko tinggi terhadap retensi jangka panjang.",
            "langkah": [
                "Tulis post-mortem: gate naik 30→40 → retensi-7 −4.31% (≈3.900+ pengguna hilang per "
                "100rb pemain baru di hari-7).",
                "Jadikan retensi hari-7 sebagai metrik GUARD wajib untuk tiap perubahan onboarding.",
                "Simpan template keputusan (kesimpulan + skor + risiko) agar dapat dirujuk ulang.",
                "Sosialisasi ke tim produk: efek kecil di retensi-1 menyembunyikan kerugian retensi-7.",
            ],
            "metrik": "1 dokumen preseden terpublikasi; metrik guard retensi-7 tercantum di SOP eksperimen onboarding.",
            "pemilik": "Data Analyst (lead dokumentasi) + Product Manager",
        },
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
        {
            "aksi": "Ambil keputusan HANYA dari baris dengan signifikan_adj = True.",
            "langkah": [
                "Filter tabel pada kolom signifikan_adj=True → pada eksperimen ini hanya retensi-7 "
                "(p_adj=0.0047) yang lolos.",
                "Abaikan retensi-1 (p_adj=0.112) dan ronde (p_adj=0.647) sebagai dasar keputusan.",
                "Tandai baris non-signifikan sebagai 'belum ada bukti', bukan 'menang/kalah'.",
                "Turunkan keputusan ini ke decision engine (skor + tier) agar konsisten.",
            ],
            "metrik": "100% keputusan merujuk hanya pada baris signifikan_adj=True; 0 keputusan dari baris p_adj>0.05.",
            "pemilik": "Experiment Owner / Data Scientist",
        },
        {
            "aksi": "Untuk metrik non-signifikan, jangan simpulkan 'tidak ada efek' — kata yang benar: 'belum ada bukti cukup' (cek power di tab Power).",
            "langkah": [
                "Cek power untuk retensi-1: dengan ≈44rb/grup, eksperimen mampu mendeteksi efek "
                "~5% relatif → 'tidak signifikan' berarti efeknya kecil, bukan kurang data.",
                "Tulis ulang kalimat laporan: ganti 'tidak ada efek' → 'belum ada bukti cukup pada "
                "n ini'.",
                "Cantumkan MDE yang terdeteksi di samping tiap p-value.",
                "Simpan hasil power bersama tabel agar pembaca paham batas deteksi.",
            ],
            "metrik": "Setiap metrik non-signifikan disertai pernyataan power/MDE; 0 frasa 'tidak ada efek' di laporan.",
            "pemilik": "Data Analyst (penulis laporan)",
        },
        {
            "aksi": "Laporkan p_adj, bukan hanya p mentah, di setiap ringkasan ke stakeholder.",
            "langkah": [
                "Ganti semua tampilan p mentah → p_adj Benjamini-Hochberg (contoh: retensi-7 p=0.0016 → "
                "p_adj=0.0047).",
                "Jelaskan 18 uji otomatis yang dikoreksi FDR agar p_adj dipahami.",
                "Tambahkan kolom signifikan_adj di ringkasan eksekutif.",
                "Audit deck/README agar tidak ada p mentah tanpa p_adj.",
            ],
            "metrik": "100% laporan menampilkan p_adj; 0 slide menampilkan p mentah tanpa koreksi.",
            "pemilik": "Data Analyst + Reviewer (QA analitik)",
        },
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
        {
            "aksi": "Gunakan lebar CI untuk menilai kesiapan keputusan: CI sempit & jauh dari 0 = aman memutuskan; CI lebar = perpanjang/perbesar sampel.",
            "langkah": [
                "Baca CI retensi-7 (seluruhnya < 0, tidak melewati nol) → aman menyatakan efek negatif → "
                "putuskan 'no-go' untuk gate_40.",
                "Baca CI retensi-1 dan ronde (melewati nol) → belum dapat diputuskan → jangan bertindak.",
                "Bila lebar CI > ambang yang berguna bisnis, jadwalkan penambahan sampel / ulangi dengan n lebih besar.",
                "Simpan plot CI sebagai lampiran bukti keputusan no-go.",
            ],
            "metrik": "Keputusan hanya untuk metrik dengan CI menjauhi nol; metrik CI-melewati-nol = 0 tindakan.",
            "pemilik": "Experiment Owner / Data Scientist",
        },
        {
            "aksi": "Sampaikan ke stakeholder dalam bahasa rentang: 'retensi-7 turun antara X% dan Y%', bukan satu angka tunggal yang terlihat pasti.",
            "langkah": [
                "Ambil batas bawah & atas CI 95% retensi-7 dan ubah ke persen relatif.",
                "Tulis kalimat: 'retensi-7 turun antara X% dan Y%' (bukan hanya '-4.31%').",
                "Tambahkan catatan bahwa ujung bawah CI bisa lebih buruk dari estimasi titik.",
                "Latih presenter agar selalu menyebut rentang, bukan titik.",
            ],
            "metrik": "100% slide menampilkan rentang CI; 0 klaim berbasis titik tunggal.",
            "pemilik": "Data Analyst + Product Manager (presenter)",
        },
        {
            "aksi": "Untuk metrik dengan CI melewati 0, jalankan eksperimen lanjutan sebelum memutuskan apa pun.",
            "langkah": [
                "Identifikasi metrik CI-melewati-nol: retensi-1 (0.4423 vs 0.4482) dan ronde.",
                "Tetapkan n & MDE lanjutan lewat power analysis (power 80%) sebelum mulai.",
                "Jangan rilis/menolak fitur apa pun atas dasar metrik ini sekarang.",
                "Catat sebagai 'perlu data tambahan' di decision log.",
            ],
            "metrik": "0 keputusan diambil dari metrik CI-melewati-nol; rencana eksperimen lanjutan terdokumentasi.",
            "pemilik": "Experiment Owner",
        },
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
        {
            "aksi": "Fokus investigasi produk pada pengguna engagement menengah: apa yang membuat mereka berhenti saat mencapai gate level 40?",
            "langkah": [
                "Isolasi segmen Q3 (engagement menengah) yang jatuh −10.5% — jauh di bawah rata-rata −4.31%.",
                "Analisis funnel mereka di sekitar gate level 40: di mana drop-off terbesar terjadi?",
                "A/B-kan perbaikan onboarding khusus Q3 (mis. gate lebih awal/longgar untuk membangun kebiasaan).",
                "Ukur ulang retensi-7 khusus segmen Q3 setelah intervensi.",
            ],
            "metrik": "Retensi-7 segmen Q3 kembali ke ≥ level kontrol (0.1902); drop-off gate_40 pada Q3 turun ≥50%.",
            "pemilik": "Product Manager (onboarding) + Data Analyst",
        },
        {
            "aksi": "Jika tetap ingin menguji gate, pertimbangkan rollout HANYA ke segmen berisiko rendah (Q1) sebagai pembelajaran, bukan ke semua orang.",
            "langkah": [
                "Batasi rollout gate_40 hanya ke segmen Q1 yang menunjukkan efek sedikit positif.",
                "Sisihkan Q2–Q4 dari uji ini untuk menghindari kerugian −10.5% pada Q3.",
                "Tetapkan guardrail: hentikan bila retensi-7 Q1 turun > 1% relatif.",
                "Jalankan dengan alokasi 50:50 di dalam segmen Q1 saja.",
            ],
            "metrik": "Efek negatif pada Q3 = 0 (tidak terekspos); retensi-7 Q1 tidak turun >1% relatif.",
            "pemilik": "Experiment Owner + Product Manager",
        },
        {
            "aksi": "Jadikan segmentasi sebagai standar: jangan pernah puas dengan 'efek rata-rata'.",
            "langkah": [
                "Tambahkan analisis per-segmen (mis. per kuartil engagement) ke template analisis wajib.",
                "Cantumkan selisih efek terburuk vs rata-rata: Q3 −10.5% vs rata-rata −4.31%.",
                "Tandai tiap keputusan dengan peringatan bila efek antar-segmen tidak seragam.",
                "Sosialisasi contoh Cookie Cats ini ke tim sebagai pelajaran standar.",
            ],
            "metrik": "100% analisis baru menyertakan breakdown per-segmen; 0 keputusan hanya berbasis rata-rata.",
            "pemilik": "Data Analyst (owner template)",
        },
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
        {
            "aksi": "Percayai hasil 'tidak signifikan' di sini: dengan power tinggi, itu memang bukti ketiadaan efek yang praktis berarti.",
            "langkah": [
                "Konfirmasi n ≥44rb/grup (total 90.189 pemain) → power 80% sudah tercapai untuk efek ~5% relatif.",
                "Simpulkan retensi-1 (0.4423 vs 0.4482) dan ronde benar-benar kecil efeknya, bukan kurang data.",
                "Cantumkan pernyataan power di samping hasil non-signifikan.",
                "Gunakan ini sebagai preseden untuk menafsirkan 'tidak signifikan' pada eksperimen besar serupa.",
            ],
            "metrik": "Setiap hasil non-signifikan disertai power/MDE terdokumentasi.",
            "pemilik": "Data Analyst",
        },
        {
            "aksi": "Untuk eksperimen berikutnya, hitung n dibutuhkan SEBELUM mulai (gunakan fungsi power_proportion/power_mean di src/stats.py).",
            "langkah": [
                "Tetapkan α=0.05 dan power=80% sebagai default.",
                "Panggil power_proportion/power_mean di src/stats.py untuk menghitung n per grup dari MDE target.",
                "Bandingkan hasil n dengan ≈44rb/grup yang terbukti cukup di eksperimen gate ini.",
                "Kunci n sebelum eksperimen berjalan (masukkan ke protokol).",
            ],
            "metrik": "Setiap eksperimen baru punya dokumen n per grup dari power analysis sebelum mulai.",
            "pemilik": "Experiment Owner / Data Scientist",
        },
        {
            "aksi": "Tetapkan MDE (minimum detectable effect) yang bermakna bisnis sejak awal, bukan setelah melihat hasil.",
            "langkah": [
                "Tentukan MDE penting bisnis (mis. 2% relatif pada retensi-7) sebelum eksperimen.",
                "Petakan MDE → n lewat power analysis.",
                "Tolak keputusan dari efek di bawah MDE (secara statistik maupun praktis tidak bermakna).",
                "Dokumentasikan MDE di kepala laporan.",
            ],
            "metrik": "100% eksperimen punya MDE tertulis sejak awal; 0 MDE ditentukan pasca-hoc.",
            "pemilik": "Product Manager + Data Scientist",
        },
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
        {
            "aksi": "Jadikan SRM check sebagai langkah WAJIB pertama di setiap analisis eksperimen — sebelum melihat metrik apa pun.",
            "langkah": [
                "Jalankan uji SRM pada 90.189 pemain (gate_30 vs gate_40) dan pastikan p tinggi (bersih).",
                "Baru setelah SRM lolos, buka metrik retensi/ronde.",
                "Blokir analisis bila p<0.001 (hentikan, investigasi randomisasi).",
                "Catat urutan langkah di SOP analisis.",
            ],
            "metrik": "100% analisis dimulai dengan SRM check; 0 metrik dibaca sebelum SRM lolos.",
            "pemilik": "Data Analyst (owner SOP analisis)",
        },
        {
            "aksi": "Catat p-value SRM di laporan; bila suatu saat p<0.001, hentikan analisis.",
            "langkah": [
                "Tambahkan baris 'SRM p-value' di bagian atas tiap laporan eksperimen.",
                "Set ambang aksi: p<0.001 → hentikan & eskalasi ke Experiment Owner.",
                "Simpan log p-value SRM historis untuk memantau stabilitas randomisasi.",
                "Sertakan langkah pemulihan bila SRM gagal (audit assignment).",
            ],
            "metrik": "100% laporan memuat p-value SRM; protokol henti aktif saat p<0.001.",
            "pemilik": "Data Analyst + Experiment Owner",
        },
        {
            "aksi": "Otomatiskan pemeriksaan ini di pipeline agar tidak bisa dilewati.",
            "langkah": [
                "Tambahkan gate SRM otomatis di pipeline analisis (assert p ≥ 0.001).",
                "Bila gagal, pipeline menghentikan proses dan menandai laporan.",
                "Kirim notifikasi otomatis ke Experiment Owner saat gate gagal.",
                "Uji berkala agar gate tetap berjalan.",
            ],
            "metrik": "0 analisis lolos pipeline tanpa melewati gate SRM otomatis.",
            "pemilik": "Data/ML Engineer",
        },
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
        {
            "aksi": "Jalankan item dengan tier prioritas tertinggi lebih dulu.",
            "langkah": [
                "Urutkan item berdasarkan skor keputusan menurun, ambil tier aksi tertinggi.",
                "Mulai eksekusi dari tier teratas (mis. gate_40 dengan sinyal retensi-7 −4.31%, p_adj=0.0047).",
                "Alokasikan resource terbatas ke tier teratas lebih dulu tiap siklus.",
                "Perbarui status item setelah dieksekusi.",
            ],
            "metrik": "≥90% item tier tertinggi dieksekusi sebelum tier lebih rendah dalam tiap siklus.",
            "pemilik": "Product Owner",
        },
        {
            "aksi": "Sesuaikan bobot sinyal & ambang tier di config sesuai kebijakan organisasi.",
            "langkah": [
                "Tinjau bobot sinyal saat ini (mis. bobot retensi-7 tinggi karena signifikan, retensi-1 rendah).",
                "Selaraskan bobot/ambang dengan prioritas (mis. retensi-7 sebagai metrik utama → bobot tertinggi).",
                "Uji ulang pada data 90.189 pemain untuk memastikan tier konsisten.",
                "Dokumentasikan setiap perubahan config beserta alasannya.",
            ],
            "metrik": "Config config ter-versioning; tier konsisten saat diuji ulang pada dataset Cookie Cats.",
            "pemilik": "Data Scientist + Product Owner",
        },
        {
            "aksi": "Audit tiap keputusan lewat skor & justifikasi terukurnya.",
            "langkah": [
                "Untuk tiap item, tampilkan skor + sinyal penyusun + tier yang dihasilkan.",
                "Cross-check justifikasi dengan angka (retensi-7 −4.31%, p_adj=0.0047 → tier kritis).",
                "Catat keputusan no-go gate_40 dengan justifikasi terukurnya.",
                "Lakukan audit berkala atas sampel keputusan.",
            ],
            "metrik": "100% keputusan menyertakan skor + justifikasi yang dapat diaudit; sampel audit lolos.",
            "pemilik": "Reviewer (QA analitik) + Data Analyst",
        },
    ],
    risiko=(
        "Keputusan tanpa skor terukur cenderung subjektif & tidak konsisten. "
        "Namun skor pun bisa salah bila formulasi sinyal keliru — karena itu "
        "setiap keputusan menyertakan justifikasi yang dapat diaudit."),
    tingkat="tinggi",
)


# --------------------------------------------------------------------------
# Chart ECharts (v2) — insight & rekomendasi agar sejajar chart Plotly lain.
# --------------------------------------------------------------------------

register(
    "echarts_boxplot",
    kesimpulan=(
        "Sebaran putaran dimainkan (sum_gamerounds) antar varian. Kedua gerbang "
        "punya median & sebaran serupa, tetapi keduanya berekor sangat panjang: "
        "segelintir pemain bermain ratusan hingga >1.000 putaran (pencilan), "
        "sementara mayoritas hanya puluhan. Artinya rata-rata mudah tertarik ke "
        "atas oleh minoritas 'hardcore', sehingga median/kuartil lebih jujur "
        "daripada mean untuk menilai engagement khas pemain."),
    rekomendasi=[
        {
            "aksi": "Gunakan median & kuartil (bukan rata-rata) saat melaporkan engagement khas; cantumkan pencilan secara terpisah.",
            "langkah": [
                "Laporkan median & kuartil sum_gamerounds per gerbang (gate_30 vs gate_40).",
                "Pisahkan pencilan (>1.000 putaran) dari ringkasan utama agar tidak menarik rata-rata.",
                "Ganti pelaporan 'rata-rata putaran' → 'median putaran' di README/dashboard.",
                "Tandai metrik mana yang memakai median vs mean.",
            ],
            "metrik": "100% laporan engagement memakai median/kuartil; pencilan dilaporkan terpisah.",
            "pemilik": "Data Analyst",
        },
        {
            "aksi": "Segmen pemain hardcore (>~300 putaran) untuk analisis tersendiri — kelompok kecil ini menyumbang sebagian besar total waktu main.",
            "langkah": [
                "Definisikan ambang hardcore (>~300 putaran) dari distribusi ekor panjang.",
                "Analisis terpisah: retensi & perilaku mereka, bandingkan gate_30 vs gate_40.",
                "Cek apakah segmen inti ini juga terdampak negatif (kaitkan dengan Q3 −10.5%).",
                "Laporkan kontribusi mereka terhadap total waktu main.",
            ],
            "metrik": "1 laporan segmen hardcore; kontribusi waktu main segmen inti terkuantifikasi.",
            "pemilik": "Data Analyst + Product Manager",
        },
        {
            "aksi": "Bila menguji perubahan gerbang, uji juga per-segmen (kasual vs hardcore), karena efek bisa berbeda di tiap ekor distribusi.",
            "langkah": [
                "Rancang eksperimen berikutnya dengan analisis pra-terdaftar per-segmen kasual vs hardcore.",
                "Pastikan power cukup di tiap segmen (hitung n per segmen lewat power analysis).",
                "Pantau efek pada ekor distribusi, bukan hanya rata-rata.",
                "Gunakan temuan Q3 (−10.5%) sebagai dasar pentingnya uji per-ekor.",
            ],
            "metrik": "Eksperimen berikutnya menyertakan hasil per-segmen kasual vs hardcore dengan power memadai.",
            "pemilik": "Experiment Owner / Data Scientist",
        },
    ],
    risiko=(
        "Mengambil keputusan dari rata-rata yang terdistorsi pencilan berisiko "
        "menyesatkan: perubahan tampak kecil padahal berdampak pada segmen inti "
        "(atau sebaliknya). Pencilan juga bisa jadi bot/QA, bukan pemain nyata."),
    tingkat="sedang",
)

register(
    "echarts_funnel",
    kesimpulan=(
        "Funnel cakupan sampel membandingkan jumlah pemain tersedia, sampel "
        "aktual per grup, dan sampel yang SECARA STATISTIK dibutuhkan untuk "
        "mendeteksi efek sekecil yang diamati. Bila kebutuhan > aktual untuk "
        "suatu metrik, eksperimen under-powered: efek nyata bisa lolos deteksi "
        "(false negative), bukan berarti efeknya tidak ada."),
    rekomendasi=[
        {
            "aksi": "Sebelum membaca 'tidak signifikan', periksa funnel ini — pastikan sampel aktual ≥ kebutuhan untuk metrik yang diputuskan.",
            "langkah": [
                "Baca funnel: pemain tersedia (90.189) → sampel aktual per grup (≈44rb) → kebutuhan statistik.",
                "Pastikan sampel aktual ≥ kebutuhan untuk metrik primer (retensi-7).",
                "Baru tafsirkan hasil retensi-7 (signifikan, p_adj=0.0047) setelah funnel lolos.",
                "Catat status funnel di tiap laporan.",
            ],
            "metrik": "100% tafsiran 'signifikan/tidak' didahului pemeriksaan funnel (aktual ≥ kebutuhan).",
            "pemilik": "Data Analyst",
        },
        {
            "aksi": "Untuk metrik under-powered, kumpulkan sampel tambahan atau longgarkan efek minimum yang ingin dideteksi (MDE).",
            "langkah": [
                "Identifikasi metrik under-powered di funnel (bila ada yang kebutuhan > aktual).",
                "Opsi A: tambah sampel sampai memenuhi n untuk MDE target (power analysis).",
                "Opsi B: naikkan MDE ke level yang masih bermakna bisnis, lalu hitung ulang n.",
                "Dokumentasikan pilihan dan dampaknya pada keputusan.",
            ],
            "metrik": "Metrik under-powered punya rencana (sampel tambahan atau MDE direvisi) sebelum diputuskan.",
            "pemilik": "Experiment Owner / Data Scientist",
        },
        {
            "aksi": "Jangan menyimpulkan 'aman' dari p-value besar bila power rendah — bedakan 'tidak ada efek' dari 'tidak terdeteksi'.",
            "langkah": [
                "Untuk tiap p-value besar, cek power di tab Power sebelum menyimpulkan.",
                "Bedakan: power tinggi → 'efek praktis tidak ada'; power rendah → 'tidak terdeteksi'.",
                "Terapkan pada retensi-1 (power tinggi → benar-benar kecil) vs metrik under-powered di funnel.",
                "Tulis kesimpulan dengan kata yang tepat di laporan.",
            ],
            "metrik": "0 klaim 'aman/tidak ada efek' dari p besar tanpa konfirmasi power.",
            "pemilik": "Data Analyst (penulis laporan)",
        },
    ],
    risiko=(
        "Menganggap fitur netral hanya karena p-value besar padahal sampel "
        "kurang berisiko merilis perubahan yang sebenarnya merugikan (atau "
        "membatalkan yang menguntungkan)."),
    tingkat="tinggi",
)
