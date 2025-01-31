import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import folium

# Fungsi untuk memfilter data berdasarkan rentang tahun
def filter_data_by_year_range(data, start_year, end_year):
    data['Year'] = pd.to_datetime(data['datetime'], errors='coerce').dt.year
    return data[(data['Year'] >= start_year) & (data['Year'] <= end_year)]

# Load dataset
file_path = 'katalog_gempa2.csv'  # Ganti dengan path file Anda
data = pd.read_csv(file_path, sep=';', low_memory=False)

# Definisi wilayah lebih rinci berdasarkan provinsi
regions_detailed = {
    'Aceh': ((4, 6), (95, 98)),
    'Sumatera Utara': ((1, 4), (98, 101)),
    'Sumatera Selatan': ((-4, 0), (103, 106)),
    'Jawa Barat': ((-7, -5), (105, 108)),
    'Jawa Timur': ((-9, -7), (112, 115)),
    'Kalimantan Selatan': ((-4, -2), (114, 117)),
    'Kalimantan Timur': ((0, 3), (116, 119)),
    'Sulawesi Selatan': ((-6, -4), (119, 122)),
    'Sulawesi Utara': ((0, 3), (122, 125)),
    'Papua Barat': ((-5, 0), (131, 136)),
    'Papua Tengah': ((-6, -3), (136, 141))
}

# Definisi wilayah berdasarkan pulau
regions_islands = {
    'Sumatera': ['Aceh', 'Sumatera Utara', 'Sumatera Selatan'],
    'Jawa': ['Jawa Barat', 'Jawa Timur'],
    'Kalimantan': ['Kalimantan Selatan', 'Kalimantan Timur'],
    'Sulawesi': ['Sulawesi Selatan', 'Sulawesi Utara'],
    'Papua': ['Papua Barat', 'Papua Tengah']
}

# Streamlit UI
st.title('📊 **Visualisasi Data Gempa Indonesia**')

# Sidebar untuk navigasi
page = st.sidebar.selectbox("Pilih Halaman", [
    "Beranda", 
    "Visualisasi Berdasarkan Tahun", 
    "Distribusi Wilayah Detail",
    "Distribusi Berdasarkan Pulau"
])

if page == "Beranda":
    st.header('Selamat Datang di Aplikasi Visualisasi Data Gempa Indonesia')
    st.write('Silakan pilih halaman di sidebar untuk memulai analisis.')

    # Menampilkan 10 Gempa Terkuat
    if 'magnitude' in data.columns and 'location' in data.columns and not data.empty:
        gempa_terkuat = data.nlargest(10, 'magnitude').reset_index(drop=True)

        st.subheader("🔍 10 Gempa Terkuat di Dataset")
        st.table(gempa_terkuat[['location', 'magnitude', 'datetime']])

        st.subheader("🗺️ Lokasi 10 Gempa Terkuat")
        m = folium.Map(location=[gempa_terkuat['latitude'].mean(), gempa_terkuat['longitude'].mean()], zoom_start=5)
        for _, row in gempa_terkuat.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=(
                    f"<b>Lokasi:</b> {row['location']}<br>"
                    f"<b>Magnitudo:</b> {row['magnitude']}<br>"
                    f"<b>Tahun:</b> {pd.to_datetime(row['datetime']).year}"
                ),
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
        st_folium(m, width=700, height=500)
    else:
        st.warning("Dataset tidak lengkap atau kosong. Periksa kembali file Anda.")

elif page == "Visualisasi Berdasarkan Tahun":
    st.title('📊 **Visualisasi Data Berdasarkan Tahun**')

    min_year = int(data['datetime'].min()[:4])
    max_year = int(data['datetime'].max()[:4])
    start_year, end_year = st.slider('Pilih Rentang Tahun:', min_value=min_year, max_value=max_year, value=(2008, 2024))

    filtered_data = filter_data_by_year_range(data, start_year, end_year)

    min_mag, max_mag = st.slider('Pilih Rentang Magnitudo:', min_value=float(data['magnitude'].min()), max_value=float(data['magnitude'].max()), value=(0.64, 7.92))
    filtered_data = filtered_data[(filtered_data['magnitude'] >= min_mag) & (filtered_data['magnitude'] <= max_mag)]

    st.subheader('📉 Rata-rata Magnitudo Gempa per Tahun')
    avg_magnitude = filtered_data.groupby('Year')['magnitude'].mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(avg_magnitude.index, avg_magnitude.values, marker='o', color='blue')
    ax.set_title('Rata-rata Magnitudo Gempa per Tahun', fontsize=16, fontweight='bold')
    ax.set_xlabel('Tahun', fontsize=14)
    ax.set_ylabel('Rata-rata Magnitudo', fontsize=14)
    ax.grid(True)
    st.pyplot(fig)

    st.subheader('📈 Tren Aktivitas Gempa per Tahun')
    activity_per_year = filtered_data.groupby('Year').size()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(activity_per_year.index, activity_per_year.values, marker='o', linestyle='-', color='#FF6347')
    ax.set_title('Tren Aktivitas Gempa per Tahun', fontsize=16, fontweight='bold')
    ax.set_xlabel('Tahun', fontsize=14)
    ax.set_ylabel('Jumlah Kejadian Gempa', fontsize=14)
    ax.grid(axis='both', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    st.subheader('📉 Tren Kedalaman Gempa per Tahun')
    avg_depth_per_year = filtered_data.groupby('Year')['depth'].mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(avg_depth_per_year.index, avg_depth_per_year.values, marker='o', color='green')
    ax.set_title('Tren Kedalaman Gempa per Tahun', fontsize=16, fontweight='bold')
    ax.set_xlabel('Tahun', fontsize=14)
    ax.set_ylabel('Rata-rata Kedalaman (km)', fontsize=14)
    ax.grid(True)
    st.pyplot(fig)

    st.subheader('🌍 Distribusi Kedalaman Gempa')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=filtered_data, x='depth', bins=30, kde=True, color='purple', ax=ax)
    ax.set_title('Distribusi Kedalaman Gempa', fontsize=16, fontweight='bold')
    ax.set_xlabel('Kedalaman (km)', fontsize=14)
    ax.set_ylabel('Frekuensi', fontsize=14)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    st.subheader('📍 Distribusi Titik Gempa Berdasarkan Wilayah')
    region_counts = {}
    for island, provinces in regions_islands.items():
        total_count = 0
        for province in provinces:
            (lat_min, lat_max), (lon_min, lon_max) = regions_detailed[province]
            count = filtered_data[(filtered_data['latitude'] >= lat_min) & 
                                  (filtered_data['latitude'] <= lat_max) & 
                                  (filtered_data['longitude'] >= lon_min) & 
                                  (filtered_data['longitude'] <= lon_max)].shape[0]
            total_count += count
        region_counts[island] = total_count

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(region_counts.keys(), region_counts.values(), color=['#FF6347', '#1E90FF', '#32CD32', '#FFD700', '#8A2BE2'])
    ax.set_title('Distribusi Titik Gempa Berdasarkan Wilayah', fontsize=16, fontweight='bold')
    ax.set_xlabel('Wilayah', fontsize=14)
    ax.set_ylabel('Jumlah Kejadian Gempa', fontsize=14)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    st.subheader(f"🌍 Heatmap Gempa Bumi ({start_year} - {end_year})")
    m = folium.Map(location=[-2.5, 118], zoom_start=5)
    heat_data = [[row['latitude'], row['longitude']] for _, row in filtered_data.iterrows() if not pd.isnull(row['latitude']) and not pd.isnull(row['longitude'])]
    if heat_data:
        HeatMap(heat_data, radius=10).add_to(m)
        st_folium(m, width=700, height=500)
    else:
        st.warning("Tidak ada data gempa untuk rentang tahun yang dipilih.")

elif page == "Distribusi Wilayah Detail":
    st.title('📊 **Distribusi Gempa Berdasarkan Wilayah Detail**')

    selected_region = st.selectbox('Pilih Wilayah:', list(regions_detailed.keys()))

    (lat_min, lat_max), (lon_min, lon_max) = regions_detailed[selected_region]
    filtered_region_data = data[(data['latitude'] >= lat_min) & (data['latitude'] <= lat_max) &
                                (data['longitude'] >= lon_min) & (data['longitude'] <= lon_max)]

    min_year = int(data['datetime'].min()[:4])
    max_year = int(data['datetime'].max()[:4])
    start_year, end_year = st.slider('Pilih Rentang Tahun:', min_value=min_year, max_value=max_year, value=(2008, 2024))
    filtered_region_data = filter_data_by_year_range(filtered_region_data, start_year, end_year)

    if filtered_region_data.empty:
        st.warning(f"Tidak ada data gempa untuk wilayah {selected_region}.")
    else:
        st.subheader(f'📉 Rata-rata Magnitudo Gempa di Wilayah {selected_region} ({start_year}-{end_year})')
        avg_magnitude = filtered_region_data.groupby('Year')['magnitude'].mean()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(avg_magnitude.index, avg_magnitude.values, marker='o', color='orange')
        ax.set_title(f'Rata-rata Magnitudo Gempa di Wilayah {selected_region}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Tahun', fontsize=14)
        ax.set_ylabel('Rata-rata Magnitudo', fontsize=14)
        ax.grid(True)
        st.pyplot(fig)

        st.subheader(f'📊 Frekuensi Gempa per Tahun di Wilayah {selected_region}')
        freq_per_year = filtered_region_data.groupby('Year').size()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(freq_per_year.index, freq_per_year.values, color='cyan')
        ax.set_title(f'Frekuensi Gempa per Tahun di Wilayah {selected_region}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Tahun', fontsize=14)
        ax.set_ylabel('Jumlah Gempa', fontsize=14)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)

elif page == "Distribusi Berdasarkan Pulau":
    st.title('📊 **Distribusi Gempa Berdasarkan Pulau**')

    selected_island = st.selectbox('Pilih Pulau:', list(regions_islands.keys()))

    provinces = regions_islands[selected_island]
    filtered_island_data = pd.DataFrame()
    for province in provinces:
        (lat_min, lat_max), (lon_min, lon_max) = regions_detailed[province]
        province_data = data[(data['latitude'] >= lat_min) & (data['latitude'] <= lat_max) &
                             (data['longitude'] >= lon_min) & (data['longitude'] <= lon_max)]
        filtered_island_data = pd.concat([filtered_island_data, province_data])

    min_year = int(data['datetime'].min()[:4])
    max_year = int(data['datetime'].max()[:4])
    start_year, end_year = st.slider('Pilih Rentang Tahun:', min_value=min_year, max_value=max_year, value=(2008, 2024))
    filtered_island_data = filter_data_by_year_range(filtered_island_data, start_year, end_year)

    if filtered_island_data.empty:
        st.warning(f"Tidak ada data gempa untuk Pulau {selected_island}.")
    else:
        st.subheader(f'📉 Rata-rata Magnitudo Gempa di Pulau {selected_island} ({start_year}-{end_year})')
        avg_magnitude = filtered_island_data.groupby('Year')['magnitude'].mean()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(avg_magnitude.index, avg_magnitude.values, marker='o', color='green')
        ax.set_title(f'Rata-rata Magnitudo Gempa di Pulau {selected_island}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Tahun', fontsize=14)
        ax.set_ylabel('Rata-rata Magnitudo', fontsize=14)
        ax.grid(True)
        st.pyplot(fig)

        st.subheader(f'📊 Frekuensi Gempa per Tahun di Pulau {selected_island}')
        freq_per_year = filtered_island_data.groupby('Year').size()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(freq_per_year.index, freq_per_year.values, color='lime')
        ax.set_title(f'Frekuensi Gempa per Tahun di Pulau {selected_island}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Tahun', fontsize=14)
        ax.set_ylabel('Jumlah Gempa', fontsize=14)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)
