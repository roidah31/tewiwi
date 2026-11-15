"""Tewiwi Bakehouse: aplikasi monitoring stok bahan baku (opsi A, hanya membaca data yang sudah disimpan)."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "outputs" / "app_data"
BULAN_ID = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

st.set_page_config(
    page_title="Tewiwi Bakehouse | Monitoring Stok", page_icon="🥐", layout="wide")


# ---------- 1. Muat data (sekali, lalu disimpan di cache Streamlit) ----------
@st.cache_data
def muat_data():
    snapshot = pd.read_csv(
        DATA_DIR / "snapshot_test.csv", parse_dates=["date"])
    laporan = pd.read_csv(DATA_DIR / "laporan_final.csv", parse_dates=["date"])
    ringkasan = json.loads(
        (DATA_DIR / "ringkasan_sistem.json").read_text(encoding="utf-8"))
    return snapshot, laporan, ringkasan


def format_tanggal(tgl):
    tgl = pd.Timestamp(tgl)
    return f"{tgl.day} {BULAN_ID[tgl.month - 1]} {tgl.year}"


snapshot, laporan, ringkasan = muat_data()
daftar_tanggal = sorted(laporan["date"].unique())

# ---------- 2. Sidebar: navigasi dan pilihan tanggal ----------
st.sidebar.title("🥐 Tewiwi Bakehouse")
halaman = st.sidebar.radio("Halaman", ["Laporan harian", "Tentang sistem"])

# ====================================================================
# HALAMAN 1: LAPORAN HARIAN (yang dilihat owner)
# ====================================================================
if halaman == "Laporan harian":
    tanggal = st.sidebar.selectbox(
        "Pilih tanggal", daftar_tanggal, index=len(daftar_tanggal) - 1, format_func=format_tanggal)

    snap = snapshot[snapshot["date"] == tanggal]
    lap = laporan[laporan["date"] == tanggal].iloc[0]

    st.title("Laporan Stok Bahan Baku")
    st.caption(
        f"Kondisi pagi hari, {format_tanggal(tanggal)}. Perkiraan untuk 7 hari ke depan.")

    # Ringkasan angka per bagian
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🔴 Perlu dibeli", int((snap["bagian"] == "Perlu dibeli").sum()))
    k2.metric("🟠 Berpotensi berlebih", int(
        (snap["bagian"] == "Berpotensi berlebih").sum()))
    k3.metric("🟡 Perlu dipantau", int(
        (snap["bagian"] == "Perlu dipantau").sum()))
    k4.metric("🟢 Aman", int((snap["bagian"] == "-").sum()))

    # Laporan untuk owner (narasi dari GenAI, sudah lolos validasi)
    st.subheader("Ringkasan untuk owner")
    with st.container(border=True):
        st.markdown(lap["laporan"])
    sumber = {"llm": "GenAI",
              "llm_ulang": "GenAI (percobaan ulang)", "template": "template otomatis"}
    st.caption(f"Narasi: {sumber.get(lap['sumber'], lap['sumber'])} · "
               f"Lolos validasi fakta: {'ya' if lap['lolos'] else 'tidak'}")

    # Tabel kondisi stok lengkap
    st.subheader("Kondisi stok per bahan")
    tabel = snap[["bahan", "satuan", "stok_gudang", "sedang_dikirim", "perkiraan_pakai_7_hari",
                  "sisa_setelah_7_hari", "kurang_jika_tidak_pesan", "status", "bagian"]].rename(columns={
                      "bahan": "Bahan", "satuan": "Satuan", "stok_gudang": "Stok gudang", "sedang_dikirim": "Sedang dikirim",
                      "perkiraan_pakai_7_hari": "Perkiraan pakai 7 hari", "sisa_setelah_7_hari": "Sisa setelah 7 hari",
                      "kurang_jika_tidak_pesan": "Kurang jika tidak pesan", "status": "Status model", "bagian": "Bagian laporan",
                  })
    tabel["Bagian laporan"] = tabel["Bagian laporan"].replace("-", "Aman")
    st.dataframe(tabel, hide_index=True, width="stretch")
    st.caption(
        "Sisa negatif berarti stok diperkirakan kurang. Telur dalam butir, bahan lain dalam kg.")

# ====================================================================
# HALAMAN 2: TENTANG SISTEM (untuk penilai dan presentasi)
# ====================================================================
else:
    st.title("Tentang Sistem")
    st.info("Data yang dipakai adalah **data simulasi** berbasis penjualan bakery publik (Kaggle), "
            "bukan data asli Tewiwi Bakehouse.")

    st.subheader("Alur sistem")
    st.markdown("""
1. **ML Prediction**: model memperkirakan pemakaian bahan 7 hari ke depan.
2. **Inventory Snapshot**: stok gudang, bahan dalam pengiriman, dan perkiraan pemakaian disusun per bahan.
3. **Rule-Based Classification**: kode Python menentukan bagian laporan, angka, dan satuan.
4. **GenAI Explanation**: LLM menulis kalimat pembuka dan saran, dan hanya menyalin daftar dari langkah 3.
5. **Deterministic Validation**: pemeriksa otomatis mencocokkan setiap baris, angka, satuan, dan saran.
6. **Final Inventory Report**: jika validasi gagal, LLM diminta ulang. Jika tetap gagal, dipakai laporan template.
""")

    st.subheader("Model prediksi (periode test)")
    metrik = pd.DataFrame(ringkasan["model_ml"]["metrik_test"]).T
    metrik = metrik.rename(columns={
        "meleset_hari": "Rata-rata meleset (hari)", "recall_restock": "Recall Restock",
        "f1_restock": "F1 Restock", "f1_excess": "F1 Excess", "f1_macro": "F1 macro"})
    st.dataframe(metrik.style.format("{:.3f}"), width="stretch")
    st.caption(ringkasan["model_ml"]["nama"])

    st.subheader("Evaluasi GenAI")
    g = ringkasan["genai"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Patuh pada percobaan pertama", f"{g['kepatuhan_percobaan_pertama'] * 100:.0f}%",
              help=f"Dari {g['n_sampel_evaluasi']} tanggal sampel acak")
    c2.metric("Laporan final lolos validasi",
              f"{g['laporan_final_lolos'] * 100:.0f}%")
    c3.metric("Laporan dengan narasi GenAI", f"{(laporan['sumber'] != 'template').mean() * 100:.0f}%",
              help=f"Dari {len(laporan)} tanggal periode test")
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
        f"Dari {o['panggilan']} panggilan LLM. Data dibuat {ringkasan['dibuat_pada']} WIB.")
