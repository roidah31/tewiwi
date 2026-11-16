"""Komponen tampilan Tewiwi Bakehouse: SVG ilustrasi dan pembuat HTML.

Aturan penting (lihat design system pasal 10):
semua string HTML/SVG di file ini ditulis MENEMPEL di tepi kiri, tanpa indentasi.
CommonMark menganggap indentasi 4 spasi atau lebih sebagai blok kode, sehingga
HTML yang menjorok akan muncul sebagai teks mentah di dalam kotak abu-abu,
bukan sebagai elemen yang dirender.
"""
import base64
from functools import lru_cache
from pathlib import Path

import pandas as pd
import streamlit as st

ASSET_DIR = Path(__file__).parent
LOGO_PATH = ASSET_DIR / "assets" / "logo_tewiwi.png"
# Foto banner. Tersedia dua pilihan di folder assets:
#   hero_roti_3.webp -> 3 roti (dipakai sekarang)
#   hero_roti_2.webp -> 2 roti (alternatif, tinggal ganti nama di baris ini)
HERO_PHOTO_PATH = ASSET_DIR / "assets" / "hero_roti_3.webp"
BULAN_ID = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"]


# ====================================================================
# LOGO RESMI
# ====================================================================
@lru_cache(maxsize=1)
def logo_data_uri() -> str:
    """Logo resmi Tewiwi Bakehouse sebagai data URI.

    Dibaca sekali lalu disimpan di memori. Dipakai sebagai data URI karena
    logonya ditempatkan di dalam HTML kustom (kartu merek sidebar), dan
    Streamlit tidak menyajikan file lokal lewat tag <img src="..."> biasa.
    """
    data = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


@lru_cache(maxsize=1)
def hero_photo_data_uri() -> str:
    """Foto produk Tewiwi untuk banner, sebagai data URI.

    Sama seperti logo: dibaca sekali lalu disimpan di memori, karena
    dipasang lewat background-image di HTML kustom.
    """
    data = base64.b64encode(HERO_PHOTO_PATH.read_bytes()).decode("ascii")
    return f"data:image/webp;base64,{data}"


# ====================================================================
# UTILITAS
# ====================================================================
def muat_styles(nama_file: str = "ui_styles.css") -> None:
    """Suntikkan design token dan seluruh style dari file CSS eksternal."""
    css = (ASSET_DIR / nama_file).read_text(encoding="utf-8")
    st.markdown(f"<style>\n{css}\n</style>", unsafe_allow_html=True)


def format_tanggal(tgl) -> str:
    """2022-09-24 -> '24 September 2022'."""
    tgl = pd.Timestamp(tgl)
    return f"{tgl.day} {BULAN_ID[tgl.month - 1]} {tgl.year}"


# ====================================================================
# KOMPONEN TAMPILAN
# ====================================================================
def sidebar_brand() -> None:
    """Identitas merek di puncak sidebar: logo resmi dan tagline.

    Sengaja tanpa kotak, border, atau bayangan. Sidebar sudah berlatar putih
    dan logonya pun berlatar putih, jadi logo menyatu langsung dengan
    halaman. Pemisah ke menu di bawahnya cukup satu garis rambut.

    Nama toko TIDAK ditulis ulang sebagai teks, karena logo resminya sudah
    memuat wordmark "tewiwi bakehouse".
    """
    st.markdown(
        '<div class="sidebar-brand">'
        f'<img src="{logo_data_uri()}" alt="Logo Tewiwi Bakehouse" class="brand-logo">'
        '<div class="brand-sub">Smart Inventory &amp; Stock Monitoring</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def hero(pill: str, judul: str, caption_html: str) -> None:
    """Banner utama: teks di kiri, foto produk menyatu di tepi kanan.

    Fotonya dipasang sebagai lapisan terpisah (bukan di dalam kotak) supaya
    bisa memudar ke kiri dan menyatu dengan gradien banner. Di layar
    <= 768px foto turun menjadi pita penuh di bawah teks; lihat
    ui_styles.css pasal 10.

    Kalau file fotonya tidak ada, banner tetap tampil rapi tanpa foto.
    """
    foto = (
        f'<div class="hero-photo" style="background-image:url({hero_photo_data_uri()})"></div>'
        if HERO_PHOTO_PATH.exists() else ''
    )
    st.markdown(
        '<div class="tewiwi-hero">'
        '<div class="tewiwi-hero-body">'
        '<div class="hero-text-col">'
        f'<div class="hero-pill">{pill}</div>'
        f'<h1 class="hero-title">{judul}</h1>'
        f'<p class="hero-caption">{caption_html}</p>'
        '</div>'
        '</div>'
        f'{foto}'
        '</div>',
        unsafe_allow_html=True,
    )


def _bento_card(varian: str, label: str, badge: str, badge_style: str,
                nilai: int, foot: str, nilai_style: str = "",
                foot_style: str = "") -> str:
    """Satu kartu KPI. Dikembalikan sebagai string agar bisa digabung ke grid."""
    return (
        f'<div class="bento-card {varian}">'
        '<div class="bento-top">'
        f'<span class="bento-label">{label}</span>'
        f'<span class="bento-badge" style="{badge_style}">{badge}</span>'
        '</div>'
        f'<div class="bento-value" style="{nilai_style}">{nilai}</div>'
        f'<div class="bento-foot" style="{foot_style}">{foot}</div>'
        '</div>'
    )


def bento_kpi(jml_beli: int, jml_lebih: int, jml_pantau: int, jml_aman: int) -> None:
    """Empat kartu KPI dalam satu CSS Grid.

    Sengaja TIDAK memakai st.columns(4): di ponsel, st.columns menumpuk
    menjadi empat baris setinggi layar. Grid sendiri tetap 2x2 di ponsel,
    sehingga keempat angka terlihat tanpa scroll.

    Setiap status memakai tiga penanda sekaligus (warna, emoji, label teks)
    agar tetap terbaca tanpa bergantung pada persepsi warna.
    """
    kartu = (
        _bento_card(
            "bento-urgent", "🔴 Perlu dibeli", "Prioritas",
            "background:#EF4444;color:#FFF;", jml_beli,
            "Bahan wajib segera direstok",
        )
        + _bento_card(
            "bento-excess", "🟠 Berpotensi berlebih", "Overstock",
            "background:rgba(255,255,255,0.22);color:#FFF;", jml_lebih,
            "Stok melebihi proyeksi 7 hari",
        )
        + _bento_card(
            "bento-watch", "🟡 Perlu dipantau", "Pantau",
            "background:#FEF3C7;color:#92400E;", jml_pantau,
            "Sisa menipis setelah 7 hari",
        )
        + _bento_card(
            "bento-safe", "🟢 Aman", "Optimal",
            "background:#DCFCE7;color:#166534;", jml_aman,
            "Cukup untuk produksi 7 hari",
            nilai_style="color:#1E3A8A;", foot_style="color:#64748B;",
        )
    )
    st.markdown(f'<div class="tw-bento-grid">{kartu}</div>',
                unsafe_allow_html=True)


def section_header(judul: str, pills: list[tuple[str, str]] | None = None) -> None:
    """Judul bagian dengan deretan pill di sisi kanan.

    pills: daftar (teks, kelas_css_tambahan). Kelas kosong = pill netral.
    """
    isi_pill = "".join(
        f'<span class="status-pill {kelas}">{teks}</span>'
        for teks, kelas in (pills or [])
    )
    st.markdown(
        '<div class="section-header">'
        f'<div class="section-title">{judul}</div>'
        f'<div class="pill-group">{isi_pill}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def pipeline(langkah: list[tuple[str, str, str]]) -> None:
    """Kartu langkah pipeline. langkah: daftar (nomor, judul, deskripsi)."""
    kartu = "".join(
        '<div class="pipeline-step">'
        f'<div class="step-num">{nomor}</div>'
        f'<div class="step-title">{judul}</div>'
        f'<p class="step-desc">{desc}</p>'
        '</div>'
        for nomor, judul, desc in langkah
    )
    st.markdown(f'<div class="pipeline-grid">{kartu}</div>',
                unsafe_allow_html=True)
