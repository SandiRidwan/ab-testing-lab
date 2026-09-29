"""
dashboard.py — Streamlit: A/B Testing & Causal Inference Lab.

Menampilkan hasil eksperimen Cookie Cats dengan rigor statistik:
KPI, tabel hasil uji (p-value + koreksi), plot efek + CI, power analysis,
SRM, efek per segmen, dan kesimpulan berbasis bukti.

Data dari DuckDB (marts). Jalankan: streamlit run app/dashboard.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from config import ALPHA, COLORS as C, DB_FILE, MARTS  # noqa: E402
import explanations as X  # noqa: E402
import insights_content  # noqa: E402,F401  (daftarkan konten insight)
import insight as INS  # noqa: E402

st.set_page_config(page_title="A/B Testing Lab", page_icon="🧪", layout="wide")


def _src() -> str:
    if DB_FILE.exists():
        return "db"
    if (MARTS / "mart_test_results.parquet").exists():
        return "marts"
    return "none"


_S = _src()


@st.cache_data(show_spinner="Membaca hasil eksperimen...")
def load(name: str) -> pd.DataFrame:
    if _S == "db":
        con = duckdb.connect(str(DB_FILE), read_only=True)
        df = con.execute(f"SELECT * FROM {name}").df()
        con.close()
        return df
    p = MARTS / f"{name}.parquet"
    return pd.read_parquet(p) if p.exists() else pd.DataFrame()


def style(fig, h=430):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=54, b=10),
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#D5DBE1"),
                      title=dict(font=dict(size=16, color="#fff")),
                      legend=dict(bgcolor="rgba(0,0,0,0)"))
    fig.update_xaxes(gridcolor="#2A3038", zeroline=False)
    fig.update_yaxes(gridcolor="#2A3038", zeroline=False)
    return fig


def kpi(col, label, value, sub, color):
    col.markdown(
        f"""<div style="background:#1A1F2B;border-left:4px solid {color};
        padding:14px 16px;border-radius:10px;height:120px;">
        <div style="color:#9AA7B4;font-size:.76rem;text-transform:uppercase;
        letter-spacing:.06em;">{label}</div>
        <div style="color:{color};font-size:1.6rem;font-weight:700;
        margin-top:6px;">{value}</div>
        <div style="color:#6B7885;font-size:.75rem;">{sub}</div></div>""",
        unsafe_allow_html=True)


if _S == "none":
    st.error("Data eksperimen belum ada. Jalankan: `python src/run_pipeline.py`")
    st.stop()

tests = load("mart_test_results")
power = load("mart_power")
srm = load("mart_srm")
segs = load("mart_segment_effects")
metrics = load("mart_variant_metrics")

# ---- header --------------------------------------------------------------
st.markdown(
    f"""<div style="background:linear-gradient(100deg,{C['primary']},{C['purple']});
    padding:22px 26px;border-radius:14px;margin-bottom:18px;">
    <div style="font-size:1.7rem;font-weight:800;color:white;">
    🧪 A/B Testing & Causal Inference Lab</div>
    <div style="color:#D7E4DC;font-size:.9rem;margin-top:4px;">
    Cookie Cats: gate level 30 vs 40 · 90.189 pemain · statistik inferensial &
    causal inference · by <b>Sandi Ridwan</b></div></div>""",
    unsafe_allow_html=True)

# ---- KPI -----------------------------------------------------------------
X.render("kpi", st=st)
n_total = int(srm["n"].sum()) if len(srm) else 0
ret7 = tests[tests["metric"] == "retention_7"]
sig = int(tests["signifikan_adj"].sum()) if len(tests) else 0
k1, k2, k3, k4 = st.columns(4)
kpi(k1, "Total pemain", f"{n_total:,}", "2 varian", C["primary"])
kpi(k2, "Metrik diuji", f"{len(tests)}", "dengan koreksi FDR", C["purple"])
kpi(k3, "Signifikan (adj)", f"{sig}", f"p_adj < {ALPHA}", C["accent"])
if len(ret7):
    r = ret7.iloc[0]
    kpi(k4, "Efek retensi-7", f"{r['rel_lift_pct']:+.2f}%",
        "p_adj=" + f"{r['p_value_adj']:.3f}",
        C["red"] if r["rel_lift_pct"] < 0 else C["primary"])
INS.box("kpi", st=st)
st.write("")

t1, t2, t3, t4 = st.tabs(["📊 Hasil Uji", "📉 Efek + CI", "⚡ Power & SRM",
                          "🔬 Metodologi"])

with t1:
    st.markdown("#### Hasil uji statistik per metrik")
    X.render("result_table", st=st)
    disp = tests.copy()
    for c in ["kontrol", "treatment", "abs_lift", "rel_lift_pct"]:
        disp[c] = disp[c].round(4)
    for c in ["ci_low", "ci_high", "p_value", "p_value_adj"]:
        disp[c] = disp[c].round(5)
    st.dataframe(disp[["metric", "kontrol", "treatment", "rel_lift_pct",
                       "ci_low", "ci_high", "p_value", "p_value_adj",
                       "signifikan_adj", "test_used"]],
                 use_container_width=True, hide_index=True)
    INS.box("result_table", st=st)

    st.markdown("#### Tingkat retensi per varian")
    rv = metrics[metrics["metric"].str.startswith("retention")]
    fig = px.bar(rv, x="variant", y="nilai_rata", color="variant",
                 facet_col="metric",
                 color_discrete_map={"gate_30": C["control"],
                                     "gate_40": C["treatment"]},
                 text=rv["nilai_rata"].round(4))
    fig.update_traces(textposition="outside")
    style(fig, 380).update_layout(showlegend=False,
                                  title="Retensi Hari-1 & Hari-7 per Varian",
                                  yaxis_title="proporsi")
    st.plotly_chart(fig, use_container_width=True)

with t2:
    st.markdown("#### Efek + Confidence Interval 95% (per metrik)")
    X.render("ci_plot", st=st)
    t = tests.copy()
    t["signif"] = t["signifikan_adj"].map({True: "signifikan", False: "tidak"})
    fig = go.Figure()
    for _, r in t.iterrows():
        color = C["red"] if r["abs_lift"] < 0 else C["primary"]
        fig.add_trace(go.Scatter(
            x=[r["abs_lift"]], y=[r["metric"]], mode="markers",
            marker=dict(size=12, color=color), showlegend=False,
            error_x=dict(type="data", symmetric=False,
                         array=[r["ci_high"] - r["abs_lift"]],
                         arrayminus=[r["abs_lift"] - r["ci_low"]],
                         color=color, thickness=2.5, width=8)))
    fig.add_vline(x=0, line_dash="dash", line_color="#8B9AA6")
    style(fig, 340).update_layout(title="Estimasi Efek (absolut) dgn CI 95%",
                                  xaxis_title="selisih (treatment − kontrol)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Batang CI tidak melewati 0 → efek signifikan. Perhatikan "
               "RETENSI-7: efek negatif signifikan (CI seluruhnya < 0).")
    INS.box("ci_plot", st=st)

    st.markdown("#### Efek heterogen per segmen engagement (retensi-7)")
    X.render("segments", st=st)
    fig = px.bar(segs, x="segmen", y="rel_lift_pct", color="rel_lift_pct",
                 color_continuous_scale="RdYlGn", text=segs["rel_lift_pct"].round(1))
    fig.update_traces(textposition="outside")
    fig.add_hline(y=0, line_dash="dash", line_color="#8B9AA6")
    style(fig, 380).update_layout(coloraxis_showscale=False,
                                  title="Lift Retensi-7 per Segmen (%)",
                                  yaxis_title="rel-lift %", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    INS.box("segments", st=st)

with t3:
    X.render("power", st=st)
    pw = power.copy()
    pw["cukup"] = pw["cukup"].map({True: "cukup", False: "kurang"})
    st.dataframe(pw, use_container_width=True, hide_index=True)
    fig = px.bar(pw, x="metric", y=["n_per_group_req", "n_actual_min"],
                 barmode="group", title="Sampel Dibutuhkan vs Aktual")
    style(fig, 360).update_layout(yaxis_title="n per grup")
    st.plotly_chart(fig, use_container_width=True)
    INS.box("power", st=st)

    X.render("srm", st=st)
    st.dataframe(srm, use_container_width=True, hide_index=True)
    st.caption("SRM p-value tinggi (tidak ada mismatch) → eksperimen valid.")
    INS.box("srm", st=st)

with t4:
    X.render("method", st=st)
    st.markdown("#### Arsitektur")
    st.code("""
 ingest.py ─► staging (Parquet) ─► load_db.py ─► DuckDB
                                      │
                                      ▼
                     stats.py (uji, CI, power, BH, SRM, CUPED)
                                      │
                                analyze.py ─► marts
                                      │
        ┌─────────────────────────────┼──────────────────┐
        ▼                             ▼                  ▼
  dashboard.py              tests/test_data_quality.py   make_charts.py
    """, language="text")
    st.markdown("#### Metode statistik yang dipakai")
    st.markdown(
        "- **2-proporsi z-test** (retensi, biner) & **Welch t-test** (ronde, kontinu)\n"
        "- **Confidence interval 95%** (analitis) + **bootstrap** (verifikasi)\n"
        "- **Power analysis** (n dibutuhkan & power tercapai)\n"
        "- **Koreksi Benjamini-Hochberg** (FDR) untuk multiple-testing\n"
        "- **SRM check** (chi-square) — gerbang validitas eksperimen\n"
        "- **Efek heterogen** per segmen engagement\n"
        "- **CUPED** (variance reduction) tersedia bila ada kovariat pra-periode")

    X.render("conclusion", st=st)
    st.markdown(
        f"**Temuan utama:** memindahkan gate dari level 30 → 40 "
        f"**menurunkan retensi hari-7 sebesar "
        f"{abs(ret7.iloc[0]['rel_lift_pct']):.2f}%** "
        f"(p={ret7.iloc[0]['p_value']:.4f}; tetap signifikan setelah koreksi, "
        f"p_adj={ret7.iloc[0]['p_value_adj']:.4f}).\n\n"
        f"**Rekomendasi:** **jangan** pindahkan gate ke level 40. Pertahankan "
        f"di level 30, atau uji posisi lain yang tidak mengganggu onboarding.")

    X.render("limitations", st=st)
    st.markdown(
        "- **Satu dataset, satu domain** (mobile game). Generalisasi ke domain "
        "lain perlu replikasi (dataset Udacity disiapkan untuk itu).\n"
        "- **Uji dua-sisi** dipakai; bila arah efek sudah diketahui, uji satu-sisi "
        "lebih kuat — tetapi lebih rentan penyalahgunaan.\n"
        "- **Trade-off koreksi FDR**: BH mengendalikan false discovery, tetapi "
        "kurang konservatif dibanding Bonferroni.\n"
        "- **Efek segmen bersifat eksploratif** — p-value segmen tidak dikoreksi "
        "terpisah; jangan jadikan klaim konfirmatori tanpa praregistrasi.\n"
        "- **Kausalitas** valid selama randomisasi berjalan (SRM bersih) — "
        "yang terverifikasi di sini.")

st.markdown(
    f"""<hr style="border-color:#2A3038;">
    <div style="color:#8B9AA6;font-size:.8rem;text-align:center;">
    🧪 A/B Testing & Causal Inference Lab · dataset Cookie Cats (publik) ·
    DuckDB + scipy/statsmodels · oleh <b>Sandi Ridwan</b><br>
    Analisis edukasional. Metode statistik standar industri; keputusan
    bisnis nyata memerlukan pertimbangan konteks.</div>""",
    unsafe_allow_html=True)
