# -*- coding: utf-8 -*-
"""
Capital Bikeshare Analytics Dashboard
Dashboard interaktif untuk analisis penyewaan sepeda (Capital Bikeshare Dataset).
Mengikuti standar struktur dan konvensi resmi Dicoding.
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. Konfigurasi Halaman Streamlit
# ==========================================
st.set_page_config(
    page_title="Capital Bikeshare Analytics Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling visualisasi
sns.set_theme(style='whitegrid')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'


# ==========================================
# 2. Helper Functions (Konvensi Resmi Dicoding)
# ==========================================

def create_daily_rentals_df(df):
    """Menyiapkan agregasi data sewa harian."""
    daily_rentals_df = df.groupby('dteday').agg({
        'cnt': 'sum',
        'registered': 'sum',
        'casual': 'sum'
    }).reset_index()
    return daily_rentals_df

def create_hourly_rentals_df(df):
    """Menyiapkan agregasi pola penyewaan per jam berdasarkan jenis hari."""
    hourly_rentals_df = df.groupby(['workingday_label', 'hr']).agg(
        avg_casual=('casual', 'mean'),
        avg_registered=('registered', 'mean'),
        avg_total=('cnt', 'mean')
    ).reset_index()
    return hourly_rentals_df

def create_season_rentals_df(df):
    """Menyiapkan agregasi rata-rata sewa per musim."""
    season_order = ['Spring', 'Summer', 'Fall', 'Winter']
    existing_seasons = [s for s in season_order if s in df['season_label'].unique()]
    season_rentals_df = df.groupby('season_label')['cnt'].mean().reindex(existing_seasons).reset_index()
    return season_rentals_df

def create_weather_rentals_df(df):
    """Menyiapkan agregasi rata-rata sewa per kondisi cuaca."""
    weather_order = ['Clear/Partly Cloudy', 'Misty/Cloudy', 'Light Snow/Rain']
    existing_weathers = [w for w in weather_order if w in df['weather_label'].unique()]
    weather_rentals_df = df.groupby('weather_label')['cnt'].mean().reindex(existing_weathers).reset_index()
    return weather_rentals_df

def create_time_slot_df(df):
    """Segmentasi fungsional jam perjalanan perkotaan (Time-Slot Binning)."""
    def get_time_slot(hour):
        if 0 <= hour <= 5:
            return 'Early Morning (00-05)'
        elif 6 <= hour <= 9:
            return 'Morning Rush (06-09)'
        elif 10 <= hour <= 15:
            return 'Midday / Daytime (10-15)'
        elif 16 <= hour <= 19:
            return 'Evening Rush (16-19)'
        else:
            return 'Night Leisure (20-23)'

    slot_df = df.copy()
    slot_df['time_slot'] = slot_df['hr'].apply(get_time_slot)
    slot_order = ['Early Morning (00-05)', 'Morning Rush (06-09)', 'Midday / Daytime (10-15)', 'Evening Rush (16-19)', 'Night Leisure (20-23)']
    
    time_slot_df = slot_df.groupby(['time_slot', 'workingday_label'])['cnt'].mean().reindex(slot_order, level=0).reset_index()
    return time_slot_df

def create_weather_comfort_df(df):
    """Analisis sensivitas dan klaster kenyamanan cuaca."""
    def get_comfort_cluster(row):
        if row['weathersit'] == 3 or row['weathersit'] == 4 or row['temp_celsius'] < 10:
            return 'Harsh / Cold / Wet'
        elif row['weathersit'] == 2 or (10 <= row['temp_celsius'] < 18):
            return 'Moderate'
        else:
            return 'Optimal / Pleasant'

    comfort_df = df.copy()
    comfort_df['comfort_cluster'] = comfort_df.apply(get_comfort_cluster, axis=1)
    comfort_order = ['Optimal / Pleasant', 'Moderate', 'Harsh / Cold / Wet']
    
    weather_comfort_df = comfort_df.groupby('comfort_cluster')[['casual', 'registered', 'cnt']].mean().reindex(comfort_order).reset_index()
    return weather_comfort_df


# ==========================================
# 3. Pemuatan Data Utama
# ==========================================
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_path = os.path.join(current_dir, 'main_data.csv')
    hour_path = os.path.join(current_dir, 'hour_data.csv')

    # Fallback paths
    if not os.path.exists(main_path):
        main_path = 'dashboard/main_data.csv'
    if not os.path.exists(hour_path):
        hour_path = 'dashboard/hour_data.csv'

    day_df = pd.read_csv(main_path)
    hour_df = pd.read_csv(hour_path)

    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

    return day_df, hour_df

day_df, hour_df = load_data()


# ==========================================
# 4. Sidebar Filter Interaktif
# ==========================================
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80", use_container_width=True)
    st.title("🚲 Capital Bikeshare")
    st.markdown("### Filter Data")

    min_date = day_df['dteday'].min().date()
    max_date = day_df['dteday'].max().date()

    # Filter Rentang Tanggal
    date_range = st.date_input(
        label="Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # Filter Musim
    all_seasons = ['Spring', 'Summer', 'Fall', 'Winter']
    selected_seasons = st.multiselect(
        label="Pilih Musim (Season)",
        options=all_seasons,
        default=all_seasons
    )

    # Filter Kondisi Cuaca
    all_weathers = ['Clear/Partly Cloudy', 'Misty/Cloudy', 'Light Snow/Rain']
    selected_weathers = st.multiselect(
        label="Kondisi Cuaca (Weather)",
        options=all_weathers,
        default=all_weathers
    )

    # Filter Tipe Hari
    day_type_option = st.radio(
        label="Kategori Hari",
        options=['Semua Hari', 'Hari Kerja (Working Day)', 'Hari Libur / Akhir Pekan']
    )

    st.markdown("---")
    st.info("""
    **Proyek Analisis Data**  
    Dataset: Capital Bikeshare (2011–2012)
    """)

# Aplikasi Filter ke Data
filtered_day = day_df[
    (day_df['dteday'].dt.date >= start_date) &
    (day_df['dteday'].dt.date <= end_date) &
    (day_df['season_label'].isin(selected_seasons)) &
    (day_df['weather_label'].isin(selected_weathers))
]

filtered_hour = hour_df[
    (hour_df['dteday'].dt.date >= start_date) &
    (hour_df['dteday'].dt.date <= end_date) &
    (hour_df['season_label'].isin(selected_seasons)) &
    (hour_df['weather_label'].isin(selected_weathers))
]

if day_type_option == 'Hari Kerja (Working Day)':
    filtered_day = filtered_day[filtered_day['workingday'] == 1]
    filtered_hour = filtered_hour[filtered_hour['workingday'] == 1]
elif day_type_option == 'Hari Libur / Akhir Pekan':
    filtered_day = filtered_day[filtered_day['workingday'] == 0]
    filtered_hour = filtered_hour[filtered_hour['workingday'] == 0]


# ==========================================
# 5. Header & KPI Metrics (Ringkasan Performa)
# ==========================================
st.title("🚲 Capital Bikeshare Performance Dashboard")
st.markdown("Dashboard interaktif untuk menganalisis dinamika permintaan sewa sepeda, perilaku pengguna, dan faktor eksternal lingkungan.")

col1, col2, col3, col4 = st.columns(4)

total_rentals = filtered_day['cnt'].sum()
total_registered = filtered_day['registered'].sum()
total_casual = filtered_day['casual'].sum()
avg_daily = filtered_day['cnt'].mean() if len(filtered_day) > 0 else 0

reg_share = (total_registered / total_rentals * 100) if total_rentals > 0 else 0
cas_share = (total_casual / total_rentals * 100) if total_rentals > 0 else 0

with col1:
    st.metric(
        label="Total Penyewaan (Unit)",
        value=f"{total_rentals:,.0f}".replace(",", ".")
    )

with col2:
    st.metric(
        label="Pengguna Terdaftar (Registered)",
        value=f"{total_registered:,.0f}".replace(",", "."),
        delta=f"{reg_share:.1f}% dari total"
    )

with col3:
    st.metric(
        label="Pengguna Biasa (Casual)",
        value=f"{total_casual:,.0f}".replace(",", "."),
        delta=f"{cas_share:.1f}% dari total"
    )

with col4:
    st.metric(
        label="Rata-rata Sewa Harian",
        value=f"{avg_daily:,.0f} Unit/Hari".replace(",", ".")
    )

st.markdown("---")


# ==========================================
# 6. Tab Navigasi Visualisasi & Insight
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🕒 Pola Jam & Pengguna (Q1)",
    "🌤️ Dampak Cuaca & Musim (Q2)",
    "📊 Analisis Lanjutan (Clustering)",
    "🎯 Rekomendasi Bisnis",
    "📁 Raw Data Explorer"
])

# ------------------------------------------
# TAB 1: Pola Jam Sewa & Pengguna (Pertanyaan 1)
# ------------------------------------------
with tab1:
    st.subheader("Pola Volume Penyewaan Berdasarkan Jam dalam Sehari")
    st.caption("Menjawab Pertanyaan Bisnis 1: Membandingkan pola penyewaan per jam antara hari kerja dan hari libur.")

    if len(filtered_hour) == 0:
        st.warning("Tidak ada data yang memenuhi kriteria filter saat ini.")
    else:
        hourly_summary = create_hourly_rentals_df(filtered_hour)

        fig, axes = plt.subplots(1, 2, figsize=(16, 5), sharey=True)

        work_data = hourly_summary[hourly_summary['workingday_label'] == 'Working Day']
        nonwork_data = hourly_summary[hourly_summary['workingday_label'] == 'Weekend/Holiday']

        # Plot Hari Kerja
        if len(work_data) > 0:
            axes[0].plot(work_data['hr'], work_data['avg_registered'], marker='o', color='#1f77b4', linewidth=2.5, label='Registered')
            axes[0].plot(work_data['hr'], work_data['avg_casual'], marker='s', color='#ff7f0e', linewidth=2, label='Casual')
            axes[0].plot(work_data['hr'], work_data['avg_total'], marker='^', color='#2ca02c', linewidth=2, linestyle='--', label='Total')
            axes[0].set_title('Pola Hari Kerja (Working Day)', fontsize=13, fontweight='bold', pad=12)
            axes[0].set_xlabel('Jam (00:00 - 23:00)', fontsize=11)
            axes[0].set_ylabel('Rata-rata Sepeda Disewa', fontsize=11)
            axes[0].set_xticks(range(0, 24, 2))
            axes[0].set_ylim(0, 650)
            axes[0].legend(loc='upper left')
            axes[0].grid(True, linestyle=':', alpha=0.6)

        # Plot Hari Libur
        if len(nonwork_data) > 0:
            axes[1].plot(nonwork_data['hr'], nonwork_data['avg_registered'], marker='o', color='#1f77b4', linewidth=2.5, label='Registered')
            axes[1].plot(nonwork_data['hr'], nonwork_data['avg_casual'], marker='s', color='#ff7f0e', linewidth=2, label='Casual')
            axes[1].plot(nonwork_data['hr'], nonwork_data['avg_total'], marker='^', color='#2ca02c', linewidth=2, linestyle='--', label='Total')
            axes[1].set_title('Pola Hari Libur / Akhir Pekan (Weekend/Holiday)', fontsize=13, fontweight='bold', pad=12)
            axes[1].set_xlabel('Jam (00:00 - 23:00)', fontsize=11)
            axes[1].set_xticks(range(0, 24, 2))
            axes[1].set_ylim(0, 650)
            axes[1].legend(loc='upper left')
            axes[1].grid(True, linestyle=':', alpha=0.6)

        plt.tight_layout()
        st.pyplot(fig)

        # Temuan Utama
        c1, c2 = st.columns(2)
        with c1:
            st.info("""
            **Pola Hari Kerja (*Working Day*):**
            - Memiliki **dua puncak (*bimodal*)** yang tajam pada pukul **08:00 pagi** (rata-rata 477 unit) dan **17:00–18:00 sore** (rata-rata 525 unit).
            - Didominasi penuh oleh pengguna *registered*, mencerminkan kebutuhan komuter harian.
            """)
        with c2:
            st.success("""
            **Pola Hari Libur (*Weekend/Holiday*):**
            - Memiliki **satu puncak (*unimodal*)** yang terpusat di tengah hari, yaitu pukul **12:00–14:00 siang** (rata-rata 373 unit).
            - Proporsi sewa pengguna *casual* meningkat signifikan untuk tujuan rekreasi akhir pekan.
            """)

# ------------------------------------------
# TAB 2: Pengaruh Musim & Cuaca (Pertanyaan 2)
# ------------------------------------------
with tab2:
    st.subheader("Dampak Pergantian Musim dan Kondisi Cuaca terhadap Volume Sewa")
    st.caption("Menjawab Pertanyaan Bisnis 2: Mengukur seberapa besar perubahan musim dan cuaca memengaruhi sewa.")

    if len(filtered_day) == 0:
        st.warning("Tidak ada data yang memenuhi kriteria filter saat ini.")
    else:
        fig, axes = plt.subplots(1, 2, figsize=(16, 5))

        # Plot 1: Musim
        season_avg = create_season_rentals_df(filtered_day)
        if len(season_avg) > 0:
            sns.barplot(data=season_avg, x='season_label', y='cnt', palette='Blues_r', ax=axes[0])
            axes[0].set_title('Rata-rata Penyewaan Harian per Musim', fontsize=13, fontweight='bold', pad=12)
            axes[0].set_xlabel('Musim', fontsize=11)
            axes[0].set_ylabel('Rata-rata Sewa (Unit)', fontsize=11)
            axes[0].grid(True, linestyle=':', alpha=0.6)
            for p in axes[0].patches:
                h = p.get_height()
                if not np.isnan(h) and h > 0:
                    axes[0].annotate(f'{h:.0f}', (p.get_x() + p.get_width() / 2., h),
                                     ha='center', va='bottom', fontsize=10, fontweight='bold', xytext=(0, 3), textcoords='offset points')

        # Plot 2: Cuaca
        weather_avg = create_weather_rentals_df(filtered_day)
        if len(weather_avg) > 0:
            sns.barplot(data=weather_avg, x='weather_label', y='cnt', palette='Greens_r', ax=axes[1])
            axes[1].set_title('Rata-rata Penyewaan Harian per Kondisi Cuaca', fontsize=13, fontweight='bold', pad=12)
            axes[1].set_xlabel('Kondisi Cuaca', fontsize=11)
            axes[1].set_ylabel('Rata-rata Sewa (Unit)', fontsize=11)
            axes[1].grid(True, linestyle=':', alpha=0.6)
            for p in axes[1].patches:
                h = p.get_height()
                if not np.isnan(h) and h > 0:
                    axes[1].annotate(f'{h:.0f}', (p.get_x() + p.get_width() / 2., h),
                                     ha='center', va='bottom', fontsize=10, fontweight='bold', xytext=(0, 3), textcoords='offset points')

        plt.tight_layout()
        st.pyplot(fig)

        st.warning("""
        **Kesimpulan Analisis Lingkungan:**
        - **Musim Gugur (*Fall*)** mencatat performa sewa tertinggi (**5.644 unit/hari**), disusul Musim Panas (**4.992 unit/hari**), Musim Dingin (**4.728 unit/hari**), dan Musim Semi (**2.604 unit/hari**).
        - **Cuaca Hujan/Salju (*Light Snow/Rain*)** menurunkan permintaan harian hingga **63.02%** dibandingkan saat cuaca cerah (dari 4.877 unit/hari menjadi hanya 1.803 unit/hari).
        """)

# ------------------------------------------
# TAB 3: Analisis Lanjutan Non-ML (Clustering)
# ------------------------------------------
with tab3:
    st.subheader("Analisis Lanjutan: Time-Slot Binning & Weather Comfort Clustering")
    st.caption("Penerapan teknik segmentasi fungsional dan pengelompokan elastisitas permintaan tanpa algoritma Machine Learning.")

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    # Visualisasi Time-Slot Binning
    slot_avg = create_time_slot_df(hour_df)
    sns.barplot(data=slot_avg, x='time_slot', y='cnt', hue='workingday_label', 
                palette={'Working Day': '#1f77b4', 'Weekend/Holiday': '#aec7e8'}, ax=axes[0])
    axes[0].set_title('Rata-rata Sewa per Jam Berdasarkan Segmen Waktu', fontsize=12, fontweight='bold', pad=12)
    axes[0].set_xlabel('Segmen Waktu', fontsize=10)
    axes[0].set_ylabel('Rata-rata Sewa per Jam', fontsize=10)
    axes[0].tick_params(axis='x', rotation=20)
    axes[0].grid(True, linestyle=':', alpha=0.6)

    # Visualisasi Weather Comfort Clustering
    comfort_avg = create_weather_comfort_df(day_df)
    comfort_melt = pd.melt(comfort_avg, id_vars=['comfort_cluster'], value_vars=['casual', 'registered'], 
                           var_name='User_Type', value_name='Avg_Rentals')
    comfort_melt['User_Type'] = comfort_melt['User_Type'].map({'casual': 'Pengguna Casual', 'registered': 'Pengguna Registered'})

    sns.barplot(data=comfort_melt, x='comfort_cluster', y='Avg_Rentals', hue='User_Type', 
                palette={'Pengguna Casual': '#ff7f0e', 'Pengguna Registered': '#1f77b4'}, ax=axes[1])
    axes[1].set_title('Sensitivitas Tipe Pengguna terhadap Klaster Cuaca', fontsize=12, fontweight='bold', pad=12)
    axes[1].set_xlabel('Klaster Cuaca', fontsize=10)
    axes[1].set_ylabel('Rata-rata Sewa Harian', fontsize=10)
    axes[1].grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    st.pyplot(fig)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        **Temuan Segmentasi Waktu:**
        - **Evening Rush (16:00–19:00)** menghasilkan intensitas sewa tertinggi di hari kerja (**462 unit/jam**).
        - **Midday / Daytime (10:00–15:00)** mendominasi pada akhir pekan (**341 unit/jam**).
        """)
    with c2:
        st.markdown("""
        **Temuan Elastisitas Permintaan Cuaca:**
        - Pengguna **Casual** sangat sensitif (**-72.77% drop**) saat kondisi berubah dari *Optimal* ke *Harsh*.
        - Pengguna **Registered** lebih tahan banting (**-43.14% drop**), karena menggunakan sepeda sebagai sarana mobilitas primer.
        """)

# ------------------------------------------
# TAB 4: Rekomendasi Bisnis Strategis
# ------------------------------------------
with tab4:
    st.subheader("Rekomendasi Action Items untuk Manajemen & Operasional")
    st.caption("Rencana aksi strategis yang dapat dieksekusi berdasarkan bukti analisis data (*evidence-based action plan*).")

    r1, r2, r3 = st.columns(3)

    with r1:
        st.markdown("""
        ### 🚚 1. Fleet Rebalancing
        **Optimalisasi Alokasi Armada**
        - Terapkan jadwal mobilisasi truk penyeimbang sepeda dua kali sehari pada hari kerja:
          - *Pagi (06:30)*: Pastikan pasokan penuh di stasiun residensial / suburban.
          - *Sore (16:00)*: Pindahkan unit ke kawasan perkantoran dan stasiun transit MRT.
        - Pindahkan unit cadangan ke stasiun area taman dan wisata sebelum pukul 11:00 di akhir pekan.
        """)

    with r2:
        st.markdown("""
        ### 🎟️ 2. Membership Conversion
        **Konversi Pengguna Kasual**
        - Manfaatkan puncak pengguna *casual* di akhir pekan dan musim gugur dengan memberikan penawaran langganan tahunan (*in-app prompt*).
        - Luncurkan paket berlangganan *"Weekend Leisure Pass"* atau *"Commuter Flex"* untuk mengikat loyalitas segmen kasual yang sering sewa ulang.
        """)

    with r3:
        st.markdown("""
        ### 🔧 3. Weather & Safety Plan
        **Mitigasi Cuaca & Perawatan**
        - Jadwalkan pemeliharaan besar (*major overhaul*) di Musim Semi dan Musim Dingin saat permintaan alami sedang turun 40-60%.
        - Sediakan notifikasi prakiraan cuaca otomatis dan program reward proteksi cuaca bagi pengguna setia di hari hujan.
        """)

# ------------------------------------------
# TAB 5: Raw Data Explorer
# ------------------------------------------
with tab5:
    st.subheader("Eksplorasi Data Terfilter")
    st.dataframe(filtered_day[['dteday', 'season_label', 'weather_label', 'workingday_label', 'temp_celsius', 'humidity_pct', 'windspeed_kmh', 'casual', 'registered', 'cnt']].head(100))

    csv_data = filtered_day.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Unduh Data Terfilter (.csv)",
        data=csv_data,
        file_name='filtered_bikeshare_data.csv',
        mime='text/csv'
    )

st.caption("Copyright © 2026 - Proyek Analisis Data Dicoding")
