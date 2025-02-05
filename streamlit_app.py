import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import folium
from sklearn.cluster import KMeans
from wordcloud import WordCloud

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

# Definisi pulau dan provinsi
regions_islands = {
    'Sumatera': ['Sumatera'],
    'Jawa': ['Jawa'],
    'Kalimantan': ['Kalimantan'],
    'Sulawesi': ['Sulawesi'],
    'Papua': ['Papua'],
    'Bali dan Nusa Tenggara': ['Bali dan Nusa Tenggara'],
    'Maluku': ['Maluku']
}

# Streamlit UI
st.set_page_config(page_title="Visualisasi Gempa Indonesia", layout="wide")

st.title('📊 **Visualisasi Data Gempa Indonesia**')
st.markdown(
    """
    <style>
    .sidebar .sidebar-content { background-color: #f8f9fa; }
    .css-1d391kg { background-color: #f0f2f6; }
    .css-qbe2hs { color: #333; }
    </style>
    """,
    unsafe_allow_html=True
)


# Sidebar untuk navigasi
page = st.sidebar.selectbox("Pilih Halaman", [
    "Beranda", 
    "Visualisasi Berdasarkan Tahun", 
    "Distribusi Berdasarkan Pulau",
    "Korelasi dan Distribusi",
])

if page == "Beranda":
    st.header('Selamat Datang di Aplikasi Visualisasi Data Gempa Indonesia')
    st.write('Silakan pilih halaman di sidebar untuk memulai analisis.')

    # Menampilkan 10 Gempa Terkuat
    if 'magnitude' in data.columns and 'location' in data.columns and not data.empty:
        gempa_terkuat = data.nlargest(10, 'magnitude').reset_index(drop=True)

        st.subheader("🔍 Gempa di Indonesia")
        # Pastikan kolom 'datetime' dalam format datetime
        data['datetime'] = pd.to_datetime(data['datetime'], errors='coerce')
        
        # Menghitung total jumlah gempa
        total_gempa = len(data)
        
        # Menghitung jumlah gempa per hari
        gempa_per_hari = data['datetime'].dt.date.value_counts()
        
        # Menghitung rata-rata jumlah gempa per hari
        rata_rata_per_hari = gempa_per_hari.mean()

        # Menampilkan informasi di halaman beranda
        st.subheader("📊 Statistik Gempa")
        st.write(f"**Total Jumlah Gempa (2008-2024):** {total_gempa}")
        st.write(f"**Rata-rata Jumlah Gempa per Hari (2008-2024):** {rata_rata_per_hari:.2f}")

        st.subheader("🔍 10 Gempa Terkuat di Dataset")
        st.table(gempa_terkuat[['location', 'magnitude', 'datetime']])

        # Menambahkan kolom baru untuk lokasi dan tahun
        gempa_terkuat['Year_Location'] = gempa_terkuat['location'] + ' (' + pd.to_datetime(gempa_terkuat['datetime']).dt.year.astype(str) + ')'
        
        # Menampilkan Chart Magnitudo terhadap Lokasi (Datetime)
        st.subheader("📊 Chart Magnitudo terhadap Lokasi (Tahun)")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(gempa_terkuat['Year_Location'], gempa_terkuat['magnitude'], color='orange')
        ax.set_title('Magnitudo Gempa Terkuat Berdasarkan Lokasi dan Tahun', fontsize=16, fontweight='bold')
        ax.set_xlabel('Lokasi (Tahun)', fontsize=14)
        ax.set_ylabel('Magnitudo', fontsize=14)
        ax.set_xticklabels(gempa_terkuat['Year_Location'], rotation=45, ha='right')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)

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
        st_folium(m , width=700, height=500)
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

        # Fungsi untuk mengkategorikan gempa berdasarkan magnitudo
        def kategori_gempa(magnitude):
            if magnitude < 4.0:
                return 'Minor'
            elif 4.0 <= magnitude < 5.0:
                return 'Ringan'
            elif 5.0 <= magnitude < 6.0:
                return 'Sedang'
            elif 6.0 <= magnitude < 7.0:
                return 'Kuat'
            else:
                return 'Besar'
        
        # Menambahkan kolom kategori ke DataFrame
        data['Kategori'] = data['magnitude'].apply(kategori_gempa)
        
        # Menghitung jumlah gempa per kategori
        kategori_counts = data['Kategori'].value_counts().reindex(['Minor', 'Ringan', 'Sedang', 'Kuat', 'Besar'], fill_value=0)
        
        # Visualisasi menggunakan bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        kategori_counts.plot(kind='bar', color=['#4CAF50', '#2196F3', '#FFC107', '#FF5722', '#F44336'], ax=ax)
        ax.set_title('Distribusi Kategori Gempa Berdasarkan Magnitudo', fontsize=16, fontweight='bold')
        ax.set_xlabel('Kategori Gempa', fontsize=14)
        ax.set_ylabel('Jumlah Kejadian', fontsize=14)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)


        # Distribusi Titik Gempa Berdasarkan Wilayah
        st.subheader('📍 Distribusi Titik Gempa Berdasarkan Wilayah')
        region_counts = {}
        for island, provinces in regions_islands.items():
            total_count = 0
            for province in provinces:
                bounds = regions_detailed[province]
                count = filtered_data[(filtered_data['latitude'] >= bounds['lat_min']) & 
                                      (filtered_data['latitude'] <= bounds['lat_max']) & 
                                      (filtered_data['longitude'] >= bounds['lon_min']) & 
                                      (filtered_data['longitude'] <= bounds['lon_max'])].shape[0]
                total_count += count
            region_counts[island] = total_count

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(region_counts.keys(), region_counts.values(), color=['#FF6347', '#1E90FF', '#32CD32', '#FFD700', '#8A2BE2'])
        ax.set_title('Distribusi Titik Gempa Berdasarkan Wilayah', fontsize=16, fontweight='bold')
        ax.set_xlabel('Wilayah', fontsize=14)
        ax.set_ylabel('Jumlah Kejadian Gempa', fontsize=14)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)


        # Tren Kedalaman Gempa per Tahun
        st.subheader('📉 Tren Kedalaman Gempa per Tahun')
        avg_depth_per_year = filtered_data.groupby('Year')['depth'].mean()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(avg_depth_per_year.index, avg_depth_per_year.values, marker='o', color='blue')
        ax.set_title('Tren Kedalaman Gempa per Tahun', fontsize=16, fontweight='bold')
        ax.set_xlabel('Tahun', fontsize=14)
        ax.set_ylabel('Rata-rata Kedalaman (km)', fontsize=14)
        ax.grid(True)
        st.pyplot(fig)
    
        # Distribusi Kedalaman Gempa
        st.subheader('🌍 Distribusi Kedalaman Gempa')
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(data=filtered_data, x='depth', bins=30, kde=True, color='purple', ax=ax)
        ax.set_title('Distribusi Kedalaman Gempa', fontsize=16, fontweight='bold')
        ax.set_xlabel('Kedalaman (km)', fontsize=14)
        ax.set_ylabel('Frekuensi', fontsize=14)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)

        # Kategorisasi kedalaman
        data['Depth Category'] = pd.cut(data['depth'], bins=[0, 70, 300, float('inf')], labels=['Dangkal', 'Menengah', 'Dalam'])
    
        # Hitung frekuensi setiap kategori
        depth_freq = data['Depth Category'].value_counts().sort_index()
    
        # Visualisasi
        st.subheader("📊 Histogram Frekuensi Gempa Berdasarkan Kedalaman")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=depth_freq.index, y=depth_freq.values, palette="viridis", ax=ax)
        ax.set_title('Frekuensi Gempa Berdasarkan Kedalaman', fontsize=16, fontweight='bold')
        ax.set_xlabel('Kategori Kedalaman', fontsize=14)
        ax.set_ylabel('Frekuensi', fontsize=14)
        st.pyplot(fig)

        
        # Heatmap
        st.subheader('🗺️ Heatmap Gempa')
        m = folium.Map(location=[(filtered_data['latitude'].mean()), (filtered_data['longitude'].mean())], zoom_start=5)
        heat_data = [[row['latitude'], row['longitude']] for _, row in filtered_data.iterrows() if not pd.isnull(row['latitude']) and not pd.isnull(row['longitude'])]
        if heat_data:
            HeatMap(heat_data, radius=15).add_to(m)
            st_folium(m, width=700, height=500)
        else:
            st.warning("Tidak ada data untuk heatmap pada rentang tahun ini.")

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


elif page == "Korelasi dan Distribusi":
    st.title('📊 **Korelasi dan Distribusi Data Gempa**')
    st.subheader("📉 Korelasi Kedalaman vs Magnitudo")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=data, x='depth', y='magnitude', alpha=0.6, ax=ax, color='green')
    ax.set_title('Korelasi Kedalaman vs Magnitudo', fontsize=16, fontweight='bold')
    ax.set_xlabel('Kedalaman (km)', fontsize=14)
    ax.set_ylabel('Magnitudo', fontsize=14)
    st.pyplot(fig)

    st.subheader("🌍 Distribusi Waktu Gempa")
    # Pastikan datetime valid dengan errors='coerce'
    data['hour'] = pd.to_datetime(data['datetime'], errors='coerce').dt.hour

    # Filter baris dengan datetime tidak valid
    data = data.dropna(subset=['hour'])

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=data, x='hour', bins=24, kde=False, ax=ax, color='blue')
    ax.set_title('Distribusi Waktu Gempa', fontsize=16, fontweight='bold')
    ax.set_xlabel('Jam (24 Jam)', fontsize=14)
    ax.set_ylabel('Frekuensi', fontsize=14)
    st.pyplot(fig)


#elif page == "Clustering Lokasi":
    #st.title('📊 **Clustering Lokasi Gempa**')

    #st.subheader("🗺️ Clustering dengan K-Means")
    #num_clusters = st.slider('Pilih Jumlah Cluster:', min_value=2, max_value=10, value=4)

    # Preprocessing data
    #clustering_data = data[['latitude', 'longitude']].dropna()
    #kmeans = KMeans(n_clusters=num_clusters, random_state=0)
    #clustering_data['cluster'] = kmeans.fit_predict(clustering_data)

    #fig, ax = plt.subplots(figsize=(10, 6))
    #sns.scatterplot(
        #data=clustering_data, x='longitude', y='latitude', hue='cluster', palette='viridis', ax=ax
    #)
    #ax.set_title('Hasil Clustering Lokasi Gempa', fontsize=16, fontweight='bold')
    #ax.set_xlabel('Longitude', fontsize=14)
    #ax.set_ylabel('Latitude', fontsize=14)
    #st.pyplot(fig)
