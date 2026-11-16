"""Tewiwi Bakehouse: aplikasi monitoring stok bahan baku.

Arsitektur Opsi A (Precomputed Static Data Reader): aplikasi HANYA membaca
file yang sudah dihitung di notebook. Tidak ada model ML yang dijalankan dan
tidak ada panggilan LLM saat aplikasi dibuka, sehingga aplikasi ringan,
deterministik, dan tidak butuh API key.

Pembagian file:
    app.py           -> controller: muat data, filter tanggal, arahkan halaman
    ui_components.py -> pembuat HTML/SVG yang bisa dipakai ulang
    ui_styles.css    -> design token, grid bento, media query ponsel
    .streamlit/config.toml -> mengunci tema terang
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

import ui_components as ui

DATA_DIR = Path(__file__).parent / "outputs" / "app_data"

st.set_page_config(
    page_title="Tewiwi Bakehouse | Monitoring Stok",
    # Ikon tab memakai logo resmi; kalau filenya tidak ada, jatuh ke emoji.
    page_icon=str(ui.LOGO_PATH) if ui.LOGO_PATH.exists() else "🥐",
    layout="wide",
    initial_sidebar_state="expanded",
)

ui.muat_styles()


# ====================================================================
# 1. MUAT DATA (sekali, lalu disimpan di cache Streamlit)
# ====================================================================
@st.cache_data
def muat_data():
    snapshot = pd.read_csv(
        DATA_DIR / "snapshot_test.csv", parse_dates=["date"])
    laporan = pd.read_csv(DATA_DIR / "laporan_final.csv", parse_dates=["date"])
    ringkasan = json.loads(
        (DATA_DIR / "ringkasan_sistem.json").read_text(encoding="utf-8"))
    return snapshot, laporan, ringkasan


try:
    snapshot, laporan, ringkasan = muat_data()
except FileNotFoundError as e:
    st.error(
        "Data aplikasi belum tersedia. Jalankan Notebook 3 (Cell 8) terlebih "
        f"dahulu untuk membuat file di `outputs/app_data/`.\n\nFile hilang: `{e.filename}`"
    )
    st.stop()

daftar_tanggal = sorted(laporan["date"].unique())


# ====================================================================
# 2. SIDEBAR: merek, navigasi, pilihan tanggal
# ====================================================================
with st.sidebar:
    ui.sidebar_brand()
    halaman = st.radio("Halaman", ["Laporan harian", "Tentang sistem"])


# ====================================================================
# HALAMAN 1: LAPORAN HARIAN (yang dilihat owner)
# ====================================================================
if halaman == "Laporan harian":
    tanggal = st.sidebar.selectbox(
        "Pilih tanggal",
        daftar_tanggal,
        index=len(daftar_tanggal) - 1,
        format_func=ui.format_tanggal,
    )

    snap = snapshot[snapshot["date"] == tanggal]
    baris_laporan = laporan[laporan["date"] == tanggal]

    st.sidebar.markdown("---")
    st.sidebar.caption(
        f"📅 **Periode pantau:** {ui.format_tanggal(tanggal)}\n\n"
        f"📦 **Total item dipantau:** {len(snap)} bahan baku"
    )

    # Tier 1: konteks waktu
    ui.hero(
        pill="🥐 Tewiwi Bakehouse · Generative AI",
        judul="Laporan Stok Bahan Baku",
        caption_html=(
            f"Kondisi pagi hari, <b>{ui.format_tanggal(tanggal)}</b>. "
            "Perkiraan untuk 7 hari ke depan."
        ),
    )

    if snap.empty:
        st.warning(
            f"Tidak ada data snapshot untuk {ui.format_tanggal(tanggal)}. "
            "Silakan pilih tanggal lain."
        )
        st.stop()

    # Tier 2: ringkasan KPI bento (4 kolom desktop, 2x2 ponsel)
    ui.bento_kpi(
        jml_beli=int((snap["bagian"] == "Perlu dibeli").sum()),
        jml_lebih=int((snap["bagian"] == "Berpotensi berlebih").sum()),
        jml_pantau=int((snap["bagian"] == "Perlu dipantau").sum()),
        jml_aman=int((snap["bagian"] == "-").sum()),
    )

    # Tier 3: narasi GenAI yang sudah lolos validasi deterministik
    LABEL_SUMBER = {
        "llm": "GenAI",
        "llm_ulang": "GenAI (percobaan ulang)",
        "template": "template otomatis",
    }

    if baris_laporan.empty:
        # Guardrail terakhir: tidak ada narasi untuk tanggal ini.
        ui.section_header("✨ Ringkasan untuk owner",
                          [("⚠ Narasi tidak tersedia", "status-pill-warn")])
        with st.container(border=True, key="narasi_owner"):
            st.markdown(
                "Narasi untuk tanggal ini belum dibuat. Angka pada kartu dan "
                "tabel di bawah tetap berasal dari perhitungan Python, jadi "
                "tetap bisa dipakai."
            )
    else:
        lap = baris_laporan.iloc[0]
        label_sumber = LABEL_SUMBER.get(lap["sumber"], lap["sumber"])
        lolos_teks = "ya" if lap["lolos"] else "tidak"
        pill_lolos = "status-pill-ok" if lap["lolos"] else "status-pill-warn"

        ui.section_header(
            "✨ Ringkasan untuk owner",
            [
                (f"🤖 Narasi: {label_sumber}", ""),
                (f"✔ Lolos validasi fakta: {lolos_teks}", pill_lolos),
            ],
        )
        with st.container(border=True, key="narasi_owner"):
            st.markdown(lap["laporan"])
        st.caption(
            f"Narasi: {label_sumber} · Lolos validasi fakta: {lolos_teks}. "
            "Seluruh angka dan kategori dihitung oleh kode Python, bukan oleh LLM."
        )

    # Tier 4: tabel rinci per bahan
    ui.section_header("📦 Kondisi stok per bahan",
                      [("📊 Detail Inventori Harian", "")])

    tabel = snap[[
        "bahan", "satuan", "stok_gudang", "sedang_dikirim",
        "perkiraan_pakai_7_hari", "sisa_setelah_7_hari",
        "kurang_jika_tidak_pesan", "status", "bagian",
    ]].rename(columns={
        "bahan": "Bahan",
        "satuan": "Satuan",
        "stok_gudang": "Stok gudang",
        "sedang_dikirim": "Sedang dikirim",
        "perkiraan_pakai_7_hari": "Perkiraan pakai 7 hari",
        "sisa_setelah_7_hari": "Sisa setelah 7 hari",
        "kurang_jika_tidak_pesan": "Kurang jika tidak pesan",
        "status": "Status model",
        "bagian": "Bagian laporan",
    })
    tabel["Bagian laporan"] = tabel["Bagian laporan"].replace("-", "Aman")

    st.dataframe(
        tabel,
        hide_index=True,
        width="stretch",
        column_config={
            "Bahan": st.column_config.TextColumn("🥖 Bahan", width="medium"),
            "Satuan": st.column_config.TextColumn("Satuan", width="small"),
            "Stok gudang": st.column_config.NumberColumn("Stok gudang", format="%.1f"),
            "Sedang dikirim": st.column_config.NumberColumn("Sedang dikirim", format="%.1f"),
            "Perkiraan pakai 7 hari": st.column_config.NumberColumn("Perkiraan pakai 7 hari", format="%.1f"),
            "Sisa setelah 7 hari": st.column_config.NumberColumn("Sisa setelah 7 hari", format="%.1f"),
            "Kurang jika tidak pesan": st.column_config.NumberColumn("Kurang jika tidak pesan", format="%.1f"),
            "Status model": st.column_config.TextColumn("Status model"),
            "Bagian laporan": st.column_config.TextColumn("Bagian laporan"),
        },
    )
    st.caption(
        "Sisa negatif berarti stok diperkirakan kurang. "
        "Telur dalam butir, bahan lain dalam kg."
    )


# ====================================================================
# HALAMAN 2: TENTANG SISTEM (untuk penilai dan presentasi)
# ====================================================================
else:
    ui.hero(
        pill="⚙️ System Architecture & Evaluation",
        judul="Tentang Sistem",
        caption_html=(
            "Dokumentasi pipeline ML Forecasting, Rule-Based Guardrails, "
            "GenAI Reporting, dan LLM Observability."
        ),
    )

    st.info(
        "Data yang dipakai adalah **data simulasi** berbasis penjualan bakery "
        "publik (Kaggle), bukan data asli Tewiwi Bakehouse."
    )

    st.subheader("Alur sistem")
    ui.pipeline([
        ("Langkah 01", "ML Prediction",
         "Model memperkirakan pemakaian bahan 7 hari ke depan."),
        ("Langkah 02", "Inventory Snapshot",
         "Stok gudang, bahan dalam pengiriman, dan perkiraan pemakaian disusun per bahan."),
        ("Langkah 03", "Rule-Based Classification",
         "Kode Python menentukan bagian laporan, angka, dan satuan."),
        ("Langkah 04", "GenAI Explanation",
         "LLM menulis kalimat pembuka dan saran, dan hanya menyalin daftar dari langkah 3."),
        ("Langkah 05", "Deterministic Validation",
         "Pemeriksa otomatis mencocokkan setiap baris, angka, satuan, dan saran."),
        ("Langkah 06", "Final Inventory Report",
         "Jika validasi gagal, LLM diminta ulang. Jika tetap gagal, dipakai laporan template."),
    ])

    st.subheader("Model prediksi (periode test)")
    metrik = pd.DataFrame(ringkasan["model_ml"]["metrik_test"]).T.rename(columns={
        "meleset_hari": "Rata-rata meleset (hari)",
        "recall_restock": "Recall Restock",
        "f1_restock": "F1 Restock",
        "f1_excess": "F1 Excess",
        "f1_macro": "F1 macro",
    })
    st.dataframe(metrik.style.format("{:.3f}"), width="stretch")
    st.caption(ringkasan["model_ml"]["nama"])

    st.subheader("Evaluasi GenAI")
    g = ringkasan["genai"]
    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Patuh pada percobaan pertama",
        f"{g['kepatuhan_percobaan_pertama'] * 100:.0f}%",
        help=f"Dari {g['n_sampel_evaluasi']} tanggal sampel acak",
    )
    c2.metric("Laporan final lolos validasi",
              f"{g['laporan_final_lolos'] * 100:.0f}%")
    c3.metric(
        "Laporan dengan narasi GenAI",
        f"{(laporan['sumber'] != 'template').mean() * 100:.0f}%",
        help=f"Dari {len(laporan)} tanggal periode test",
    )
    st.caption(f"Model: {g['model']} · Prompt: {g['versi_prompt']}")

    st.subheader("Observability LLM")
    o = ringkasan["observability"]
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Latency median", f"{o['latency_median_detik']} detik")
    d2.metric("Latency p90", f"{o['latency_p90_detik']} detik")
    d3.metric("Error rate", f"{o['error_rate'] * 100:.1f}%")
    d4.metric("Token rata-rata",
              f"{o['token_input_rata2']} masuk / {o['token_output_rata2']} keluar")
    st.caption(
        f"Dari {o['panggilan']} panggilan LLM. "
        f"Data dibuat {ringkasan['dibuat_pada']} WIB."
    )
