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

# Definisi wilayah lebih rinci berdasarkan pulau utama dengan cakupan penuh tanpa jeda
regions_detailed = {
    'Sumatera': {'lat_min': -6.5, 'lat_max': 6.5, 'lon_min': 94.5, 'lon_max': 106.5},
    'Jawa': {'lat_min': -9.5, 'lat_max': -4.5, 'lon_min': 105.5, 'lon_max': 115.5},
    'Kalimantan': {'lat_min': -4.5, 'lat_max': 3.5, 'lon_min': 108.5, 'lon_max': 119.5},
    'Sulawesi': {'lat_min': -5.5, 'lat_max': 2.5, 'lon_min': 118.5, 'lon_max': 125.5},
    'Papua': {'lat_min': -11.5, 'lat_max': 0.5, 'lon_min': 130.5, 'lon_max': 141.5},
    'Bali dan Nusa Tenggara': {'lat_min': -10.5, 'lat_max': -7.5, 'lon_min': 114.5, 'lon_max': 119.5},
    'Maluku': {'lat_min': -8.5, 'lat_max': 2.5, 'lon_min': 125.5, 'lon_max': 135.5}
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
    st.title('📊 **Visualisasi Data Gempa Berdasarkan Tahun**')

    min_year = int(data['datetime'].min()[:4])
    max_year = int(data['datetime'].max()[:4])
    start_year, end_year = st.slider('Pilih Rentang Tahun:', min_value=min_year, max_value=max_year, value=(2008, 2024))

    filtered_data = filter_data_by_year_range(data, start_year, end_year)

    if filtered_data.empty:
        st.warning("Tidak ada data gempa untuk rentang tahun yang dipilih.")
    else:
        st.subheader(f'📈 Tren Aktivitas Gempa dari Tahun {start_year} hingga {end_year}')
        activity_per_year = filtered_data.groupby('Year').size()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(activity_per_year.index, activity_per_year.values, marker='o', linestyle='-', color='#FF6347')
        ax.set_title(f'Tren Aktivitas Gempa {start_year}-{end_year}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Tahun', fontsize=14)
        ax.set_ylabel('Jumlah Kejadian Gempa', fontsize=14)
        ax.grid(axis='both', linestyle='--', alpha=0.7)
        st.pyplot(fig)

        st.subheader(f'📉 Rata-rata Magnitudo Gempa dari Tahun {start_year} hingga {end_year}')
        average_magnitude = filtered_data.groupby('Year')['magnitude'].mean()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(average_magnitude.index, average_magnitude.values, marker='o', color='#32CD32')
        ax.set_title(f'Rata-rata Magnitudo Gempa {start_year}-{end_year}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Tahun', fontsize=14)
        ax.set_ylabel('Rata-rata Magnitudo', fontsize=14)
        ax.grid(True)
        st.pyplot(fig)

elif page == "Distribusi Berdasarkan Pulau":
    st.title('📊 **Distribusi Gempa Berdasarkan Pulau**')

    selected_region = st.selectbox('Pilih Pulau:', list(regions_detailed.keys()))
    bounds = regions_detailed[selected_region]
    filtered_region_data = data[(data['latitude'] >= bounds['lat_min']) &
                                (data['latitude'] <= bounds['lat_max']) &
                                (data['longitude'] >= bounds['lon_min']) &
                                (data['longitude'] <= bounds['lon_max'])]

    min_year = int(data['datetime'].min()[:4])
    max_year = int(data['datetime'].max()[:4])
    start_year, end_year = st.slider('Pilih Rentang Tahun:', min_value=min_year, max_value=max_year, value=(2008, 2024))
    filtered_region_data = filter_data_by_year_range(filtered_region_data, start_year, end_year)

    if filtered_region_data.empty:
        st.warning(f"Tidak ada data gempa untuk wilayah {selected_region}.")
    else:
        st.subheader(f'📉 Rata-rata Magnitudo Gempa di Pulau {selected_region} ({start_year}-{end_year})')
        avg_magnitude = filtered_region_data.groupby('Year')['magnitude'].mean()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(avg_magnitude.index, avg_magnitude.values, marker='o', color='orange')
        ax.set_title(f'Rata-rata Magnitudo Gempa di Pulau {selected_region}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Tahun', fontsize=14)
        ax.set_ylabel('Rata-rata Magnitudo', fontsize=14)
        ax.grid(True)
        st.pyplot(fig)

        st.subheader(f'📊 Frekuensi Gempa per Tahun di Pulau {selected_region}')
        freq_per_year = filtered_region_data.groupby('Year').size()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(freq_per_year.index, freq_per_year.values, color='cyan')
        ax.set_title(f'Frekuensi Gempa per Tahun di Pulau {selected_region}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Tahun', fontsize=14)
        ax.set_ylabel('Jumlah Gempa', fontsize=14)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)

        st.subheader(f'🗺️ Heatmap Gempa di Pulau {selected_region}')
        m = folium.Map(location=[(bounds['lat_min'] + bounds['lat_max']) / 2, (bounds['lon_min'] + bounds['lon_max']) / 2], zoom_start=6)
        heat_data = [[row['latitude'], row['longitude']] for _, row in filtered_region_data.iterrows() if not pd.isnull(row['latitude']) and not pd.isnull(row['longitude'])]
        if heat_data:
            HeatMap(heat_data, radius=15).add_to(m)
            st_folium(m, width=700, height=500)
        else:
            st.warning("Tidak ada data untuk heatmap pada wilayah ini.")

elif page == "Distribusi Wilayah Detail":
    st.title('📊 **Distribusi Gempa Berdasarkan Wilayah Detail**')

    selected_region = st.selectbox('Pilih Wilayah:', list(regions_detailed.keys()))
    bounds = regions_detailed[selected_region]
    filtered_region_data = data[(data['latitude'] >= bounds['lat_min']) &
                                (data['latitude'] <= bounds['lat_max']) &
                                (data['longitude'] >= bounds['lon_min']) &
                                (data['longitude'] <= bounds['lon_max'])]

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
        ax.plot(avg_magnitude.index, avg_magnitude.values, marker='o', color='green')
        ax.set_title(f'Rata-rata Magnitudo Gempa di Wilayah {selected_region}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Tahun', fontsize=14)
