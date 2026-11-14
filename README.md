# 🚲 Capital Bikeshare Performance Dashboard

Proyek analisis data ini menganalisis pola penyewaan sepeda pada sistem **Capital Bikeshare** (Washington D.C., USA) sepanjang tahun 2011 hingga 2012. Proyek ini mencakup seluruh tahapan analisis data mulai dari *Data Wrangling*, *Exploratory Data Analysis (EDA)*, *Data Visualization*, *Advanced Clustering Analysis*, hingga pengembangan dashboard interaktif menggunakan **Streamlit**.

🔗 **Live Dashboard (Streamlit Cloud):** [https://bikeshare-dashboard-astroxxii.streamlit.app/](https://bikeshare-dashboard-astroxxii.streamlit.app/)

---

## 📁 Struktur Direktori Proyek

```text
submission/
├── dashboard/
│   ├── main_data.csv        # Dataset harian bersih
│   ├── hour_data.csv        # Dataset per jam bersih
│   ├── all_data.csv         # Salinan dataset bersih (kompatibilitas)
│   └── dashboard.py         # Aplikasi dashboard Streamlit
├── data/
│   ├── day.csv              # Dataset mentah harian
│   ├── hour.csv             # Dataset mentah per jam
│   └── Readme.txt           # Dokumentasi dataset Capital Bikeshare
├── notebook.ipynb           # Jupyter Notebook yang telah tereksekusi
├── Proyek_Analisis_Data.ipynb # Berkas template notebook asli yang telah tereksekusi
├── README.md                # Dokumentasi & panduan menjalankan dashboard
├── requirements.txt         # Daftar pustaka Python yang dibutuhkan
└── url.txt                  # Tautan dashboard di Streamlit Cloud
```

---

## 🎯 Pertanyaan Bisnis
1. **Pertanyaan 1 (Pola Jam & Pengguna):**  
   Bagaimana perbedaan pola volume penyewaan sepeda antara pengguna biasa (*casual*) dan pengguna terdaftar (*registered*) berdasarkan jam dalam sehari pada hari kerja (*working day*) dibandingkan hari libur (*non-working day*) sepanjang periode 2011–2012 untuk mengoptimalkan ketersediaan armada sepeda di stasiun transit?
2. **Pertanyaan 2 (Pengaruh Musim & Cuaca):**  
   Seberapa signifikan dampak kondisi cuaca (*weather situation*) dan pergantian musim (*season*) terhadap rata-rata total volume penyewaan sepeda harian selama 2011–2012, serta bagaimana strategi operasional untuk memitigasi penurunan permintaan saat kondisi cuaca buruk?

---

## 🌐 Tautan Aplikasi Dashboard (Streamlit Cloud)
Aplikasi dashboard interaktif telah aktif dan dapat diakses publik melalui tautan:  
👉 **[https://bikeshare-dashboard-astroxxii.streamlit.app/](https://bikeshare-dashboard-astroxxii.streamlit.app/)**

---

## 🚀 Panduan Menyiapkan Lingkungan (*Setup Environment*) & Menjalankan Dashboard Lokal

### 1. Setup Environment - Anaconda
```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

### 2. Setup Environment - Shell/Terminal (Pipenv)
```bash
pip install pipenv
pipenv install
pipenv shell
pip install -r requirements.txt
```

### 3. Setup Environment - Terminal / Command Prompt Standar (Virtual Environment)
```bash
# Membuat virtual environment
python -m venv venv

# Mengaktifkan di Windows
venv\Scripts\activate

# Mengaktifkan di macOS/Linux
source venv/bin/activate

# Memasang dependensi
pip install -r requirements.txt
```

---

## ▶️ Menjalankan Dashboard Streamlit di Lokal

Jalankan perintah berikut di terminal dari direktori utama proyek:

```bash
streamlit run dashboard/dashboard.py
```

*Atau jika perintah `streamlit` belum terdaftar di PATH:*
```bash
python -m streamlit run dashboard/dashboard.py
```

*Atau berpindah ke folder `dashboard/`:*
```bash
cd dashboard
streamlit run dashboard.py
# atau
python -m streamlit run dashboard.py
```

Buka peramban (*web browser*) Anda di:
`http://localhost:8501`

---

## 📊 Fitur-Fitur Utama Dashboard
- **Sidebar Filter Dinamis**: Filter rentang tanggal, pilihan musim (*season*), kondisi cuaca (*weather*), dan jenis hari (*working day* vs *weekend/holiday*).
- **KPI Metrics Cards**: Total penyewaan, kontribusi pengguna *registered* vs *casual* (% dari total), dan rata-rata sewa harian.
- **Tab 1 (Pola Jam & Pengguna)**: Visualisasi kurva per jam membandingkan komuter kerja vs rekreasi akhir pekan.
- **Tab 2 (Cuaca & Musim)**: Visualisasi dampak 4 musim dan penurunan permintaan sewa akibat cuaca basah/salju (-63%).
- **Tab 3 (Analisis Lanjutan)**: *Time-Slot Binning* perjalanan dan *Weather Comfort Clustering* untuk elastisitas permintaan.
- **Tab 4 (Rekomendasi Bisnis)**: 3 pilar aksi strategis berbasis data untuk armada dan operasional.
- **Tab 5 (Raw Data Explorer)**: Tabel data terfilter dengan tombol unduh berkas CSV (*Download Filtered Data*).
