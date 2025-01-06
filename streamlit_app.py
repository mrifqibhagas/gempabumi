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

# Streamlit UI
st.title('📊 **Visualisasi Data Gempa Indonesia**')

# Sidebar untuk navigasi
page = st.sidebar.selectbox("Pilih Halaman", [
    "Beranda", 
    "Visualisasi Berdasarkan Tahun", 
    "Visualisasi Berdasarkan Pulau"
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

    st.subheader('📍 Distribusi Titik Gempa Berdasarkan Wilayah')
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

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(region_counts.keys(), region_counts.values(), color=['#FF6347', '#1E90FF', '#32CD32', '#FFD700', '#8A2BE2'])
    ax.set_title('Distribusi Titik Gempa Berdasarkan Wilayah', fontsize=16, fontweight='bold')
    ax.set_xlabel('Wilayah', fontsize=14)
    ax.set_ylabel('Jumlah Kejadian Gempa', fontsize=14)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    st.subheader('📈 Tren Aktivitas Gempa per Tahun')
    activity_per_year = filtered_data.groupby('Year').size()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(activity_per_year.index, activity_per_year.values, marker='o', color='#FF6347')
    ax.set_title('Tren Aktivitas Gempa per Tahun', fontsize=16, fontweight='bold')
    ax.set_xlabel('Tahun', fontsize=14)
    ax.set_ylabel('Jumlah Kejadian Gempa', fontsize=14)
    ax.grid(True)
    st.pyplot(fig)

    st.subheader(f"🌍 Heatmap Gempa Bumi ({start_year} - {end_year})")
    m = folium.Map(location=[-2.5, 118], zoom_start=5)
    heat_data = [[row['latitude'], row['longitude']] for _, row in filtered_data.iterrows() if not pd.isnull(row['latitude']) and not pd.isnull(row['longitude'])]
    if heat_data:
        HeatMap(heat_data, radius=10).add_to(m)
        st_folium(m, width=700, height=500)
    else:
        st.warning("Tidak ada data gempa untuk rentang tahun yang dipilih.")

elif page == "Visualisasi Berdasarkan Pulau":
    st.title('📊 **Visualisasi Berdasarkan Pulau**')

    islands = ['Sumatera', 'Jawa', 'Kalimantan', 'Sulawesi', 'Papua']
    selected_island = st.selectbox('Pilih Pulau:', islands)

    min_year = int(data['datetime'].min()[:4])
    max_year = int(data['datetime'].max()[:4])
    start_year, end_year = st.slider('Pilih Rentang Tahun:', min_value=min_year, max_value=max_year, value=(2008, 2024))

    regions = {
        'Sumatera': ((-6, 6), (95, 105)),
        'Jawa': ((-9, -5), (105, 115)),
        'Kalimantan': ((-4, 3), (108, 119)),
        'Sulawesi': ((-3, 2), (119, 125)),
        'Papua': ((-10, 0), (131, 141))
    }

    (lat_min, lat_max), (lon_min, lon_max) = regions[selected_island]
    filtered_island_data = data[(data['latitude'] >= lat_min) & (data['latitude'] <= lat_max) &
                                (data['longitude'] >= lon_min) & (data['longitude'] <= lon_max)]
    filtered_island_data = filter_data_by_year_range(filtered_island_data, start_year, end_year)

    min_mag, max_mag = st.slider('Pilih Rentang Magnitudo:', min_value=float(data['magnitude'].min()), max_value=float(data['magnitude'].max()), value=(0.64, 7.92))
    filtered_island_data = filtered_island_data[(filtered_island_data['magnitude'] >= min_mag) & (filtered_island_data['magnitude'] <= max_mag)]

    if filtered_island_data.empty:
        st.warning(f"Tidak ada data gempa untuk Pulau {selected_island} dalam rentang tahun yang dipilih.")
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

        st.subheader(f'🗺️ Heatmap Magnitudo di Pulau {selected_island}')
        filtered_island_data_cleaned = filtered_island_data.dropna(subset=['latitude', 'longitude', 'magnitude'])
        m = folium.Map(location=[(lat_min + lat_max) / 2, (lon_min + lon_max) / 2], zoom_start=6)
        heat_data = [[row['latitude'], row['longitude'], row['magnitude']] for _, row in filtered_island_data_cleaned.iterrows()]
        if heat_data:
            HeatMap(heat_data, radius=15).add_to(m)
            st_folium(m, width=700, height=500)
        else:
            st.warning(f"Tidak ada data gempa di Pulau {selected_island}.")
