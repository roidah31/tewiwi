Tewiwi Bakehouse: Smart Inventory & Stock Monitoring

Capstone Project Dicoding Bootcamp Batch 15, learning path Generative AI (ID Grup: DB15-I011).

Tewiwi Bakehouse Smart Inventory & Stock Monitoring adalah aplikasi yang membantu owner bakery memantau stok bahan baku. Setiap pagi, sistem memperkirakan kebutuhan bahan untuk 7 hari ke depan dan menunjukkan bahan mana yang perlu dibeli, cukup, atau berlebih. Hasilnya dijelaskan oleh AI dalam ringkasan berbahasa sederhana, sehingga owner bisa memutuskan pembelian dengan cepat tanpa cek stok manual.

Link penting
	Link
Aplikasi	https://tewiwibakehouse.streamlit.app
Slide presentasi	docs/Presentation Tewiwi Bakehouse.pdf
Video presentasi	[TEMPEL LINK YOUTUBE DI SINI]
Dataset	https://www.kaggle.com/datasets/matthieugimbert/french-bakery-daily-sales
Cara menggunakan aplikasi

Aplikasi tidak memerlukan username atau password.

Buka https://tewiwibakehouse.streamlit.app dari browser laptop atau smartphone.
Pada sidebar, pilih halaman Laporan harian, lalu pilih tanggal laporan (periode uji 1 Juni sampai 24 September 2022).
Baca empat kartu ringkas di bagian atas: Perlu dibeli (label Prioritas), Berpotensi berlebih (Overstock), Perlu dipantau (Pantau), dan Aman (Optimal). Angka di setiap kartu adalah jumlah bahan dengan status tersebut.
Baca Ringkasan untuk owner: daftar bahan per bagian beserta saran tindakan. Label di sebelah kanan judul menunjukkan sumber narasi (GenAI atau template) dan status lolos validasi fakta.
Gulir ke tabel Kondisi stok per bahan untuk melihat stok gudang, bahan yang sedang dikirim, perkiraan pemakaian, dan sisa setelah tujuh hari.
Buka halaman Tentang sistem untuk melihat alur kerja, metrik model, metrik GenAI, dan metrik observability.

Aplikasi berjalan di Streamlit Community Cloud versi gratis. Jika aplikasi lama tidak dibuka, halaman akan meminta aplikasi dibangunkan. Klik tombol yang tersedia dan tunggu kurang dari satu menit.

Cara kerja sistem

Prinsip utamanya: kode menjaga angka, AI menulis bahasa.

Data (RQ1). Data penjualan harian bakery dari Kaggle dipetakan ke lima produk serupa Tewiwi lewat resep, diubah menjadi pemakaian 10 bahan baku, lalu disimulasikan pemesanan, waktu kirim, bahan terbuang, dan bulk order. Fitur hanya memakai informasi yang tersedia pagi hari.
Model (RQ2). HistGradientBoostingRegressor dengan quantile 0,7 memperkirakan pemakaian 7 hari ke depan. Hasilnya masuk ke inventory policy yang memberi status Restock, Sufficient, atau Excess.
Generative AI (RQ3). Kode rule-based menentukan bagian laporan, angka, dan satuan. LLM openai/gpt-oss-120b melalui Groq menulis ringkasan untuk owner. Validator deterministik mencocokkan setiap baris; laporan yang gagal ditulis ulang satu kali, lalu diganti template yang disusun langsung dari data bila tetap gagal.
Aplikasi. Streamlit menampilkan laporan yang sudah dibuat dan divalidasi di notebook, sehingga aplikasi selalu cepat dan owner hanya menerima laporan yang lolos validasi.
Hasil utama

Data uji: 1.160 baris, Juni sampai September 2022. Baseline: rata-rata pemakaian 30 hari terakhir × 7.

Metrik	Baseline	Model
F1 macro	0,434	0,828
Recall Restock	0,516	0,897
F1 Excess	0,000	0,731
Rata-rata meleset (hari pemakaian)	2,65	1,31


Struktur folder
├── app.py                 # aplikasi Streamlit
├── ui_components.py       # komponen tampilan (kartu, header)
├── ui_styles.css          # gaya tampilan aplikasi
├── requirements.txt       # dependensi aplikasi
├── .streamlit/            # konfigurasi tema aplikasi
├── assets/                # logo dan foto produk Tewiwi
├── docs/                  # slide presentasi (PDF)
├── notebooks/             # 1. data prep, 2. modeling, 3. GenAI
├── data/processed/        # data hasil olahan notebook 1
├── models/                # model final dan hasil evaluasi di data uji
└── outputs/app_data/      # snapshot, laporan final, dan ringkasan yang dibaca aplikasi
Cara menjalankan
Aplikasi di komputer sendiri

Membutuhkan Python 3.12.

bash
pip install -r requirements.txt
streamlit run app.py

Aplikasi membaca file di outputs/app_data/, jadi tidak membutuhkan API key.

Notebook

Notebook dijalankan berurutan di Google Colab: 1. Tewiwi_bakehouse.ipynb → 2. Tewiwi_bakehouse_modeling.ipynb → 3. Tewiwi_bakehouse_genai.ipynb.

Unduh dataset dari Kaggle (link di atas). Data mentah tidak diunggah ke repository ini untuk menghormati lisensi dataset.
Buat folder Tewiwi-Bakehouse di Google Drive, lalu letakkan file dataset di Tewiwi-Bakehouse/data/raw/Bakery sales.csv. Jika memakai lokasi lain, ubah PROJECT_DIR di cell pertama setiap notebook.
Notebook 3 membutuhkan API key yang disimpan di Colab Secrets (ikon kunci di sidebar Colab, aktifkan Notebook access):
groq: API key Groq
langfuse_public dan langfuse_secret: key Langfuse untuk observability
Jangan menulis API key langsung di kode atau di markdown.
Keterbatasan
Stok masih simulasi dari data penjualan publik, sehingga hasil belum mewakili kondisi Tewiwi yang sesungguhnya.
Status Restock, Sufficient, dan Excess berasal dari aturan inventory, bukan catatan kejadian nyata.
Hasil model bergantung pada periode (F1 macro validasi 0,565, uji 0,828).
Aplikasi menampilkan laporan tersimpan, belum membuat laporan baru secara langsung.
Tech stack

Python, pandas, NumPy, Matplotlib, Seaborn, scikit-learn, joblib, Groq API (openai/gpt-oss-120b), OpenAI Python SDK, Langfuse, Streamlit, Streamlit Community Cloud, Google Colab.


