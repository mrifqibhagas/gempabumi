import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Fungsi untuk memfilter data berdasarkan rentang tahun
def filter_data_by_year_range(data, start_year, end_year):
    data['Year'] = pd.to_datetime(data['datetime'], errors='coerce').dt.year
    filtered_data = data[(data['Year'] >= start_year) & (data['Year'] <= end_year)]
    return filtered_data

# Load dataset
file_path = 'katalog_gempa2.csv'  # Ganti dengan path file Anda
data = pd.read_csv(file_path, sep=';', low_memory=False)

# Streamlit UI
st.set_page_config(page_title='Analisis Data Gempa Bumi', layout='wide')

# Sidebar untuk navigasi
st.sidebar.title("Navigasi")
page = st.sidebar.radio("Pilih Halaman", ["Beranda", "Visualisasi Berdasarkan Tahun"])

if page == "Beranda":
    st.title('📊 **Analisis Data Gempa Bumi**')
    st.markdown("""
    **Selamat datang di aplikasi analisis data gempa bumi Indonesia!**
    Di sini, Anda dapat melihat berbagai visualisasi tentang data kejadian gempa di Indonesia berdasarkan wilayah dan tahun.
    """)
    #st.image('header_image.png', use_column_width=True)

elif page == "Visualisasi Berdasarkan Tahun":
    # Input rentang tahun dari pengguna
    st.title('📊 **Visualisasi Data Gempa Bumi**')
    
    # Menempatkan rentang tahun kembali ke atas
    min_year = int(data['datetime'].min()[:4])
    max_year = int(data['datetime'].max()[:4])
    start_year, end_year = st.slider(
        'Pilih Rentang Tahun:',
        min_value=min_year,
        max_value=max_year,
        value=(2010, 2015)
    )

    # Filter data berdasarkan input rentang tahun
    filtered_data = filter_data_by_year_range(data, start_year, end_year)

    # Visualisasi distribusi titik gempa berdasarkan wilayah
    st.subheader('📍 Distribusi Titik Gempa Berdasarkan Wilayah')

    # Menghitung jumlah kejadian gempa per wilayah
    regions = {
        'Sumatera': ((-6, 6), (95, 105)),
        'Jawa': ((-9, -5), (105, 115)),
        'Kalimantan': ((-4, 3), (108, 119)),
        'Sulawesi': ((-3, 2), (119, 125)),
        'Papua': ((-10, 0), (131, 141))
    }

    region_counts = {}
    for region, ((lat_min, lat_max), (lon_min, lon_max)) in regions.items():
        count = filtered_data[(filtered_data['latitude'] >= lat_min) & (filtered_data['latitude'] <= lat_max) &
                              (filtered_data['longitude'] >= lon_min) & (filtered_data['longitude'] <= lon_max)].shape[0]
        region_counts[region] = count

    # Plot distribusi menggunakan Streamlit
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(region_counts.keys(), region_counts.values(), color=['#FF6347', '#1E90FF', '#32CD32', '#FFD700', '#8A2BE2'])
    ax.set_title('Distribusi Titik Gempa Berdasarkan Wilayah', fontsize=16, fontweight='bold')
    ax.set_xlabel('Wilayah', fontsize=14)
    ax.set_ylabel('Jumlah Kejadian Gempa', fontsize=14)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    st.write(f'Jumlah Wilayah yang Tercatat: {len(region_counts)}')

    # Visualisasi rata-rata magnitude per tahun
    average_magnitude = filtered_data.groupby('Year')['magnitude'].mean()

    st.subheader(f'📉 Rata-rata Magnitudo Gempa dari Tahun {start_year} hingga {end_year}')
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(average_magnitude, marker='o', color='#32CD32')
    ax.set_title(f'Rata-rata Magnitudo Gempa dari Tahun {start_year} hingga {end_year}', fontsize=16, fontweight='bold')
    ax.set_xlabel('Tahun', fontsize=14)
    ax.set_ylabel('Rata-rata Magnitudo', fontsize=14)
    ax.grid(True)
    st.pyplot(fig)

    # 2. Time-Series Aktivitas Gempa per Tahun
    st.subheader('📈 Tren Aktivitas Gempa per Tahun')
    activity_per_year = filtered_data.groupby('Year').size()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(activity_per_year.index, activity_per_year.values, marker='o', linestyle='-', color='#FF6347')
    ax.set_title('Tren Aktivitas Gempa per Tahun', fontsize=16, fontweight='bold')
    ax.set_xlabel('Tahun', fontsize=14)
    ax.set_ylabel('Jumlah Kejadian Gempa', fontsize=14)
    ax.grid(axis='both', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    # 1. Distribusi Magnitudo Gempa
    st.subheader('🌍 Distribusi Magnitudo Gempa di Indonesia')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=filtered_data, x='magnitude', bins=30, kde=True, color='#1E90FF', ax=ax)
    ax.set_title('Distribusi Magnitudo Gempa di Indonesia', fontsize=16, fontweight='bold')
    ax.set_xlabel('Magnitudo', fontsize=14)
    ax.set_ylabel('Frekuensi', fontsize=14)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    st.write(f'Jumlah Data yang Difilter: {len(filtered_data)}')
