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

    # Membuat heatmap menggunakan Folium
    st.subheader(f"Heatmap Gempa Bumi ({start_year} - {end_year})")
    
    # Inisialisasi peta
    m = folium.Map(location=[-2.5, 118], zoom_start=5)
    
    # Menyiapkan data untuk heatmap
    heat_data = [[row['latitude'], row['longitude']] for index, row in filtered_data.iterrows() if not pd.isnull(row['latitude']) and not pd.isnull(row['longitude'])]
    
        # Menambahkan heatmap ke peta
        if heat_data:
            HeatMap(heat_data, radius=10).add_to(m)
            # Tampilkan peta di Streamlit
            st_folium(m, width=700, height=500)
        else:
            st.warning("Tidak ada data gempa untuk rentang tahun yang dipilih.")
    
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
