"""Tewiwi Bakehouse: aplikasi monitoring stok bahan baku (opsi A, hanya membaca data yang sudah disimpan)."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "outputs" / "app_data"
BULAN_ID = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

st.set_page_config(
    page_title="Tewiwi Bakehouse | Monitoring Stok",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================================================================
# ILUSTRASI SVG CUSTOM (GAYA BLUE DOODLE TEWIWI BAKEHOUSE)
# ====================================================================
SVG_BAKERY_SCENE = """
<svg viewBox="0 0 320 150" width="100%" height="140" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="breadGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#DBEAFE" stop-opacity="0.9"/>
    </linearGradient>
  </defs>
  <!-- Dekorasi Bintang / Tepung -->
  <circle cx="35" cy="30" r="3" fill="#FFFFFF" opacity="0.8"/>
  <circle cx="280" cy="25" r="4" fill="#FFFFFF" opacity="0.7"/>
  <circle cx="150" cy="18" r="2.5" fill="#FFFFFF" opacity="0.6"/>
  <path d="M70 20 L73 27 L80 30 L73 33 L70 40 L67 33 L60 30 L67 27 Z" fill="#FFFFFF" opacity="0.85"/>
  <path d="M245 15 L247 20 L252 22 L247 24 L245 29 L243 24 L238 22 L243 20 Z" fill="#FFFFFF" opacity="0.75"/>

  <!-- Tangkai Gandum Kiri -->
  <g stroke="#FFFFFF" stroke-width="2.2" fill="none" stroke-linecap="round">
    <path d="M25 125 Q45 80 65 45"/>
    <ellipse cx="42" cy="85" rx="7" ry="4" transform="rotate(-30 42 85)" fill="#93C5FD" stroke="#1E3A8A"/>
    <ellipse cx="52" cy="68" rx="7" ry="4" transform="rotate(-30 52 68)" fill="#93C5FD" stroke="#1E3A8A"/>
    <ellipse cx="53" cy="92" rx="7" ry="4" transform="rotate(25 53 92)" fill="#93C5FD" stroke="#1E3A8A"/>
    <ellipse cx="62" cy="75" rx="7" ry="4" transform="rotate(25 62 75)" fill="#93C5FD" stroke="#1E3A8A"/>
  </g>

  <!-- Baguette Doodle (Belakang) -->
  <g transform="rotate(-14 195 75)">
    <rect x="130" y="45" width="145" height="44" rx="22" fill="url(#breadGrad)" stroke="#1E3A8A" stroke-width="3"/>
    <path d="M155 52 Q165 65 158 78" stroke="#1E40AF" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <path d="M185 52 Q195 65 188 78" stroke="#1E40AF" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <path d="M215 52 Q225 65 218 78" stroke="#1E40AF" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <path d="M245 52 Q255 65 248 78" stroke="#1E40AF" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  </g>

  <!-- Sourdough Artisan Loaf (Tengah Utama) -->
  <g>
    <path d="M65 125 C60 72, 195 72, 190 125 Z" fill="url(#breadGrad)" stroke="#1E3A8A" stroke-width="3.2" stroke-linejoin="round"/>
    <!-- Sourdough Scoring / Slash Marks -->
    <path d="M100 92 Q125 82 155 95" stroke="#1E3A8A" stroke-width="2.8" fill="none" stroke-linecap="round"/>
    <path d="M95 103 Q125 94 160 105" stroke="#2563EB" stroke-width="2.2" fill="none" stroke-linecap="round"/>
    <!-- Wajah Karakter Cute ala Tewiwi -->
    <circle cx="115" cy="113" r="3" fill="#1E3A8A"/>
    <circle cx="140" cy="113" r="3" fill="#1E3A8A"/>
    <ellipse cx="107" cy="116" rx="4" ry="2.2" fill="#60A5FA" opacity="0.7"/>
    <ellipse cx="148" cy="116" rx="4" ry="2.2" fill="#60A5FA" opacity="0.7"/>
    <path d="M123 114 Q127.5 119 132 114" stroke="#1E3A8A" stroke-width="2.2" fill="none" stroke-linecap="round"/>
  </g>

  <!-- Croissant Doodle (Kanan Depan) -->
  <g transform="translate(185, 82)">
    <path d="M15 35 C5 20, 20 5, 45 8 C70 5, 85 20, 75 35 C65 42, 58 28, 45 28 C32 28, 25 42, 15 35 Z" fill="#EFF6FF" stroke="#1E3A8A" stroke-width="2.8" stroke-linejoin="round"/>
    <path d="M30 10 Q45 22 33 32" stroke="#1E3A8A" stroke-width="2.2" fill="none"/>
    <path d="M60 10 Q45 22 57 32" stroke="#1E3A8A" stroke-width="2.2" fill="none"/>
  </g>

  <!-- Alas / Papan Roti -->
  <line x1="40" y1="126" x2="285" y2="126" stroke="#1E3A8A" stroke-width="3.5" stroke-linecap="round"/>
</svg>
"""

SVG_SIDEBAR_LOGO = """
<svg viewBox="0 0 120 110" width="95" height="85" xmlns="http://www.w3.org/2000/svg">
  <!-- Topi Roti / Sourdough Beret ala Maskot Tewiwi -->
  <path d="M18 65 C10 30, 110 30, 102 65 C95 72, 25 72, 18 65 Z" fill="#EFF6FF" stroke="#1E3A8A" stroke-width="3.2"/>
  <path d="M38 42 Q50 35 62 44" stroke="#2563EB" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <path d="M65 39 Q77 35 85 45" stroke="#2563EB" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <!-- Wajah Maskot -->
  <path d="M35 64 C35 92, 85 92, 85 64" fill="#FFFFFF" stroke="#1E3A8A" stroke-width="3"/>
  <circle cx="49" cy="73" r="3" fill="#1E3A8A"/>
  <circle cx="71" cy="73" r="3" fill="#1E3A8A"/>
  <ellipse cx="42" cy="76" rx="3.5" ry="2" fill="#93C5FD"/>
  <ellipse cx="78" cy="76" rx="3.5" ry="2" fill="#93C5FD"/>
  <path d="M56 75 Q60 79 64 75" stroke="#1E3A8A" stroke-width="2.2" fill="none" stroke-linecap="round"/>
</svg>
"""

# ====================================================================
# CUSTOM CSS (TEMA TEWIWI BLUE DOODLE + MODERN BENTO DASHBOARD)
# ====================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Background Utama Soft Bakery Cream-Blue */
.stApp {
    background: linear-gradient(135deg, #F0F6FF 0%, #F8FAFC 55%, #E8F1FF 100%);
    color: #0F172A;
}

/* Hilangkan padding berlebih di atas */
.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 3rem !important;
    max-width: 1380px;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 2px solid #DBEAFE;
}

.sidebar-brand-box {
    background: linear-gradient(180deg, #DBEAFE 0%, #EFF6FF 100%);
    border: 2px solid #1E3A8A;
    border-radius: 20px;
    padding: 16px 12px 14px 12px;
    text-align: center;
    margin-bottom: 18px;
    box-shadow: 0 6px 0 #1E3A8A;
    position: relative;
    overflow: hidden;
}

.sidebar-awning {
    height: 12px;
    margin: -16px -12px 12px -12px;
    background: repeating-linear-gradient(
        90deg,
        #1E3A8A,
        #1E3A8A 12px,
        #FFFFFF 12px,
        #FFFFFF 24px
    );
    border-bottom: 2px solid #1E3A8A;
}

.brand-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #1E3A8A;
    letter-spacing: -0.02em;
    margin-top: 4px;
}

.brand-sub {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #2563EB;
    text-transform: uppercase;
    margin-top: 2px;
}

/* Hero Banner dengan Motif Awning Kemasan Tewiwi */
.tewiwi-hero {
    background: linear-gradient(125deg, #1E40AF 0%, #2563EB 55%, #3B82F6 100%);
    border-radius: 24px;
    border: 2.5px solid #1E3A8A;
    box-shadow: 0 12px 28px -8px rgba(30, 64, 175, 0.35), 0 6px 0 #1E3A8A;
    color: #FFFFFF;
    margin-bottom: 24px;
    overflow: hidden;
    position: relative;
}

.tewiwi-awning-top {
    height: 16px;
    width: 100%;
    background: repeating-linear-gradient(
        90deg,
        #1E3A8A,
        #1E3A8A 18px,
        #FFFFFF 18px,
        #FFFFFF 36px
    );
    border-bottom: 2.5px solid #1E3A8A;
}

.tewiwi-hero-body {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 22px 30px;
    gap: 20px;
    flex-wrap: wrap;
}

.hero-text-col {
    flex: 1 1 420px;
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.18);
    border: 1.5px solid rgba(255, 255, 255, 0.45);
    color: #FFFFFF;
    padding: 4px 13px;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.hero-title {
    font-size: 2.05rem;
    font-weight: 800;
    color: #FFFFFF !important;
    margin: 0 0 6px 0;
    letter-spacing: -0.02em;
    line-height: 1.15;
}

.hero-caption {
    font-size: 0.95rem;
    color: #DBEAFE;
    font-weight: 500;
    margin: 0;
}

.hero-art-col {
    flex: 0 0 290px;
    background: rgba(255, 255, 255, 0.12);
    border: 1.5px solid rgba(255, 255, 255, 0.28);
    border-radius: 18px;
    padding: 6px 12px;
    backdrop-filter: blur(6px);
}

/* Bento KPI Cards (Inspirasi dari Tablet UI) */
.bento-card {
    border-radius: 22px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    height: 156px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    margin-bottom: 12px;
}

.bento-card:hover {
    transform: translateY(-3px);
}

/* Variasi Warna Kartu Bento */
.bento-urgent {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    color: #FFFFFF;
    border: 2px solid #0F172A;
    box-shadow: 0 10px 24px -6px rgba(15, 23, 42, 0.35);
}

.bento-excess {
    background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%);
    color: #FFFFFF;
    border: 2px solid #1E3A8A;
    box-shadow: 0 10px 24px -6px rgba(37, 99, 235, 0.35);
}

.bento-watch {
    background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
    color: #1E3A8A;
    border: 2px solid #93C5FD;
    box-shadow: 0 8px 20px -6px rgba(30, 58, 138, 0.12);
}

.bento-safe {
    background: #FFFFFF;
    color: #0F172A;
    border: 2px solid #BFDBFE;
    box-shadow: 0 8px 20px -6px rgba(30, 58, 138, 0.08);
}

.bento-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.bento-label {
    font-size: 0.88rem;
    font-weight: 700;
    letter-spacing: -0.01em;
}

.bento-badge {
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 999px;
}

.bento-value {
    font-size: 2.65rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.03em;
    margin: 8px 0 4px 0;
}

.bento-foot {
    font-size: 0.76rem;
    opacity: 0.85;
    font-weight: 500;
}

/* Section Headers */
.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 22px 0 12px 0;
    flex-wrap: wrap;
    gap: 10px;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #1E3A8A;
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0;
}

.pill-group {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 700;
    border: 1.5px solid #BFDBFE;
    background: #FFFFFF;
    color: #1E3A8A;
}

.status-pill-ok {
    background: #DCFCE7;
    border-color: #86EFAC;
    color: #166534;
}

.status-pill-warn {
    background: #FEF3C7;
    border-color: #FDE68A;
    color: #92400E;
}

/* Styling Container Berborder Streamlit (Untuk Narasi Owner) */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border: 2px solid #93C5FD !important;
    border-radius: 20px !important;
    padding: 8px 12px !important;
    box-shadow: 0 10px 25px -8px rgba(30, 58, 138, 0.1) !important;
}

/* Step Cards pada Halaman Tentang Sistem */
.pipeline-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 12px;
    margin-top: 8px;
    margin-bottom: 16px;
}

.pipeline-step {
    background: #FFFFFF;
    border: 1.5px solid #BFDBFE;
    border-left: 5px solid #2563EB;
    border-radius: 14px;
    padding: 14px 16px;
    box-shadow: 0 4px 12px rgba(30, 58, 138, 0.05);
}

.step-num {
    font-size: 0.72rem;
    font-weight: 800;
    color: #2563EB;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.step-title {
    font-size: 0.96rem;
    font-weight: 800;
    color: #0F172A;
    margin: 2px 0 4px 0;
}

.step-desc {
    font-size: 0.83rem;
    color: #475569;
    margin: 0;
    line-height: 1.45;
}

/* Metric Standard Override (Halaman 2) */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1.8px solid #BFDBFE;
    border-radius: 18px;
    padding: 16px 18px;
    box-shadow: 0 6px 16px -6px rgba(30, 58, 138, 0.08);
}

[data-testid="stMetricLabel"] {
    font-weight: 700 !important;
    color: #475569 !important;
}

[data-testid="stMetricValue"] {
    font-weight: 800 !important;
    color: #1E3A8A !important;
}
</style>
""", unsafe_allow_html=True)


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
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-brand-box">
        <div class="sidebar-awning"></div>
        {SVG_SIDEBAR_LOGO}
        <div class="brand-title">Téwiwi Bakehouse</div>
        <div class="brand-sub">Sourdough Based · Smart Inventory</div>
    </div>
    """, unsafe_allow_html=True)

    halaman = st.radio("Halaman", ["Laporan harian", "Tentang sistem"])

# ====================================================================
# HALAMAN 1: LAPORAN HARIAN (yang dilihat owner)
# ====================================================================
if halaman == "Laporan harian":
    tanggal = st.sidebar.selectbox(
        "Pilih tanggal", daftar_tanggal, index=len(daftar_tanggal) - 1, format_func=format_tanggal)

    snap = snapshot[snapshot["date"] == tanggal]
    lap = laporan[laporan["date"] == tanggal].iloc[0]

    # Info tambahan di sidebar agar rapi & informatif
    st.sidebar.markdown("---")
    st.sidebar.caption(
        f"📅 **Periode pantau:** {format_tanggal(tanggal)}\n\n"
        f"📦 **Total item dipantau:** {len(snap)} bahan baku"
    )

    # Hero Banner dengan Ilustrasi Roti Sourdough & Croissant Doodle
    st.markdown(f"""
    <div class="tewiwi-hero">
        <div class="tewiwi-awning-top"></div>
        <div class="tewiwi-hero-body">
            <div class="hero-text-col">
                <div class="hero-pill">🥐 Tewiwi Bakehouse · AI Stock Monitoring</div>
                <h1 class="hero-title">Laporan Stok Bahan Baku</h1>
                <p class="hero-caption">Kondisi pagi hari, <b>{format_tanggal(tanggal)}</b>. Perkiraan untuk 7 hari ke depan.</p>
            </div>
            <div class="hero-art-col">
                {SVG_BAKERY_SCENE}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Ringkasan angka per bagian (Bento UI Cards)
    jml_beli = int((snap["bagian"] == "Perlu dibeli").sum())
    jml_lebih = int((snap["bagian"] == "Berpotensi berlebih").sum())
    jml_pantau = int((snap["bagian"] == "Perlu dipantau").sum())
    jml_aman = int((snap["bagian"] == "-").sum())

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(f"""
        <div class="bento-card bento-urgent">
            <div class="bento-top">
                <span class="bento-label">🔴 Perlu dibeli</span>
                <span class="bento-badge" style="background:#EF4444;color:#FFF;">Prioritas</span>
            </div>
            <div class="bento-value">{jml_beli}</div>
            <div class="bento-foot">Bahan wajib segera direstok</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="bento-card bento-excess">
            <div class="bento-top">
                <span class="bento-label">🟠 Berpotensi berlebih</span>
                <span class="bento-badge" style="background:rgba(255,255,255,0.22);color:#FFF;">Overstock</span>
            </div>
            <div class="bento-value">{jml_lebih}</div>
            <div class="bento-foot">Stok melebihi proyeksi 7 hari</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="bento-card bento-watch">
            <div class="bento-top">
                <span class="bento-label">🟡 Perlu dipantau</span>
                <span class="bento-badge" style="background:#FEF3C7;color:#92400E;">Pantau</span>
            </div>
            <div class="bento-value">{jml_pantau}</div>
            <div class="bento-foot">Sisa menipis setelah 7 hari</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="bento-card bento-safe">
            <div class="bento-top">
                <span class="bento-label">🟢 Aman</span>
                <span class="bento-badge" style="background:#DCFCE7;color:#166534;">Optimal</span>
            </div>
            <div class="bento-value" style="color:#1E3A8A;">{jml_aman}</div>
            <div class="bento-foot" style="color:#64748B;">Cukup untuk produksi 7 hari</div>
        </div>
        """, unsafe_allow_html=True)

    # Laporan untuk owner (narasi dari GenAI, sudah lolos validasi)
    sumber = {"llm": "GenAI",
              "llm_ulang": "GenAI (percobaan ulang)", "template": "template otomatis"}
    label_sumber = sumber.get(lap["sumber"], lap["sumber"])
    lolos_teks = "ya" if lap["lolos"] else "tidak"
    pill_class = "status-pill-ok" if lap["lolos"] else "status-pill-warn"

    st.markdown(f"""
    <div class="section-header">
        <div class="section-title">✨ Ringkasan untuk owner</div>
        <div class="pill-group">
            <span class="status-pill">🤖 Narasi: {label_sumber}</span>
            <span class="status-pill {pill_class}">✔ Lolos validasi fakta: {lolos_teks}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(lap["laporan"])

    st.caption(f"Narasi: {label_sumber} · Lolos validasi fakta: {lolos_teks}")

    # Tabel kondisi stok lengkap
    st.markdown("""
    <div class="section-header">
        <div class="section-title">📦 Kondisi stok per bahan</div>
        <div class="pill-group">
            <span class="status-pill">📊 Detail Inventori Harian</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabel = snap[["bahan", "satuan", "stok_gudang", "sedang_dikirim", "perkiraan_pakai_7_hari",
                  "sisa_setelah_7_hari", "kurang_jika_tidak_pesan", "status", "bagian"]].rename(columns={
                      "bahan": "Bahan", "satuan": "Satuan", "stok_gudang": "Stok gudang", "sedang_dikirim": "Sedang dikirim",
                      "perkiraan_pakai_7_hari": "Perkiraan pakai 7 hari", "sisa_setelah_7_hari": "Sisa setelah 7 hari",
                      "kurang_jika_tidak_pesan": "Kurang jika tidak pesan", "status": "Status model", "bagian": "Bagian laporan",
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
        }
    )
    st.caption(
        "Sisa negatif berarti stok diperkirakan kurang. Telur dalam butir, bahan lain dalam kg.")

# ====================================================================
# HALAMAN 2: TENTANG SISTEM (untuk penilai dan presentasi)
# ====================================================================
else:
    st.markdown(f"""
    <div class="tewiwi-hero">
        <div class="tewiwi-awning-top"></div>
        <div class="tewiwi-hero-body">
            <div class="hero-text-col">
                <div class="hero-pill">⚙️ System Architecture & Evaluation</div>
                <h1 class="hero-title">Tentang Sistem</h1>
                <p class="hero-caption">Dokumentasi pipeline ML Forecasting, Rule-Based Guardrails, GenAI Reporting, dan LLM Observability.</p>
            </div>
            <div class="hero-art-col">
                {SVG_BAKERY_SCENE}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.info("Data yang dipakai adalah **data simulasi** berbasis penjualan bakery publik (Kaggle), "
            "bukan data asli Tewiwi Bakehouse.")

    st.subheader("Alur sistem")
    st.markdown("""
    <div class="pipeline-grid">
        <div class="pipeline-step">
            <div class="step-num">Langkah 01</div>
            <div class="step-title">ML Prediction</div>
            <p class="step-desc">Model memperkirakan pemakaian bahan 7 hari ke depan.</p>
        </div>
        <div class="pipeline-step">
            <div class="step-num">Langkah 02</div>
            <div class="step-title">Inventory Snapshot</div>
            <p class="step-desc">Stok gudang, bahan dalam pengiriman, dan perkiraan pemakaian disusun per bahan.</p>
        </div>
        <div class="pipeline-step">
            <div class="step-num">Langkah 03</div>
            <div class="step-title">Rule-Based Classification</div>
            <p class="step-desc">Kode Python menentukan bagian laporan, angka, dan satuan.</p>
        </div>
        <div class="pipeline-step">
            <div class="step-num">Langkah 04</div>
            <div class="step-title">GenAI Explanation</div>
            <p class="step-desc">LLM menulis kalimat pembuka dan saran, dan hanya menyalin daftar dari langkah 3.</p>
        </div>
        <div class="pipeline-step">
            <div class="step-num">Langkah 05</div>
            <div class="step-title">Deterministic Validation</div>
            <p class="step-desc">Pemeriksa otomatis mencocokkan setiap baris, angka, satuan, dan saran.</p>
        </div>
        <div class="pipeline-step">
            <div class="step-num">Langkah 06</div>
            <div class="step-title">Final Inventory Report</div>
            <p class="step-desc">Jika validasi gagal, LLM diminta ulang. Jika tetap gagal, dipakai laporan template.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
