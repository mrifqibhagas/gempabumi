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
st.title('📊 **Visualisasi Data Gempa Indonesia**')

# Sidebar untuk memilih halaman
page = st.sidebar.selectbox("Pilih Halaman", ["Beranda", "Visualisasi Berdasarkan Tahun", "Visualisasi Berdasarkan Pulau"])

if page == "Beranda":
    st.header('Selamat datang di aplikasi Visualisasi Data Gempa Indonesia')
    st.write('Silakan pilih halaman di sidebar untuk memulai analisis.')

# Halaman Visualisasi Berdasarkan Tahun
elif page == "Visualisasi Berdasarkan Tahun":
    st.title('📊 **Visualisasi Data Gempa Berdasarkan Tahun**')

    # Mengambil nilai rentang tahun dari slider
    start_year, end_year = st.slider('Pilih Rentang Tahun:', min_value=2010, max_value=2025, value=(2010, 2015))

    # Filter data berdasarkan rentang tahun
    filtered_data = filter_data_by_year_range(data, start_year, end_year)

    # 1. Distribusi Magnitudo Gempa
    st.subheader('📊 Distribusi Magnitudo Gempa di Indonesia')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=filtered_data, x='magnitude', bins=30, kde=True, color='blue', ax=ax)
    ax.set_title('Distribusi Magnitudo Gempa di Indonesia', fontsize=14)
    ax.set_xlabel('Magnitudo', fontsize=12)
    ax.set_ylabel('Frekuensi', fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    # 2. Time-Series Aktivitas Gempa per Tahun
    st.subheader('📈 Tren Aktivitas Gempa per Tahun')
    activity_per_year = filtered_data.groupby('Year').size()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(activity_per_year.index, activity_per_year.values, marker='o', linestyle='-', color='orange')
    ax.set_title('Tren Aktivitas Gempa per Tahun', fontsize=14)
    ax.set_xlabel('Tahun', fontsize=12)
    ax.set_ylabel('Jumlah Kejadian Gempa', fontsize=12)
    ax.grid(axis='both', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    # 3. Visualisasi berdasarkan wilayah (Latitude & Longitude)
    st.subheader('📍 Distribusi Titik Gempa Berdasarkan Tahun')
    if 'longitude' in filtered_data.columns and 'latitude' in filtered_data.columns:
        if filtered_data.empty:
            st.warning("Tidak ada data gempa yang ditemukan untuk rentang tahun tersebut.")
        else:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.scatter(filtered_data['longitude'], filtered_data['latitude'], color='blue', alpha=0.5, s=10)
            ax.set_title('Distribusi Titik Gempa Berdasarkan Tahun', fontsize=16, fontweight='bold')
            ax.set_xlabel('Longitude', fontsize=14)
            ax.set_ylabel('Latitude', fontsize=14)
            ax.grid(True)
            st.pyplot(fig)
    else:
        st.error("Data tidak mengandung kolom 'longitude' dan 'latitude'.")

# Halaman Visualisasi Berdasarkan Pulau
elif page == "Visualisasi Berdasarkan Pulau":
    st.title('📊 **Visualisasi Data Gempa Berdasarkan Pulau**')

    # Pilih pulau-pulau yang ingin ditampilkan
    islands = ['Sumatera', 'Jawa', 'Kalimantan', 'Sulawesi', 'Papua']
    selected_islands = st.multiselect('Pilih Pulau-pulau yang ingin ditampilkan:', islands, default=['Sumatera', 'Jawa'])

    # Definisikan batas koordinat per pulau
    regions = {
        'Sumatera': ((-6, 6), (95, 105)),
        'Jawa': ((-9, -5), (105, 115)),
        'Kalimantan': ((-4, 3), (108, 119)),
        'Sulawesi': ((-3, 2), (119, 125)),
        'Papua': ((-10, 0), (131, 141))
    }

    # Filter data berdasarkan pilihan pulau
    filtered_island_data = pd.DataFrame()
    for island in selected_islands:
        (lat_min, lat_max), (lon_min, lon_max) = regions[island]
        island_data = data[(data['latitude'] >= lat_min) & (data['latitude'] <= lat_max) & 
                           (data['longitude'] >= lon_min) & (data['longitude'] <= lon_max)]
        filtered_island_data = pd.concat([filtered_island_data, island_data])

    # Visualisasi data gempa berdasarkan pulau yang dipilih
    if filtered_island_data.empty:
        st.warning("Tidak ada data gempa yang ditemukan untuk pulau-pulau yang dipilih.")
    else:
        st.subheader(f'📍 Distribusi Titik Gempa di Pulau: {", ".join(selected_islands)}')
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(filtered_island_data['longitude'], filtered_island_data['latitude'], color='blue', alpha=0.5, s=10)
        ax.set_title(f'Distribusi Titik Gempa di Pulau: {", ".join(selected_islands)}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Longitude', fontsize=14)
        ax.set_ylabel('Latitude', fontsize=14)
        ax.grid(True)
        st.pyplot(fig)
