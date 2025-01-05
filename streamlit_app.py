import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import folium
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import numpy as np

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
page = st.sidebar.selectbox("Pilih Halaman", [
    "Beranda", 
    "Visualisasi Berdasarkan Tahun", 
    "Visualisasi Berdasarkan Pulau",
    "Clustering Lokasi Gempa",
    "Prediksi Risiko Wilayah"
])


if page == "Beranda":
    st.header('Selamat datang di aplikasi Visualisasi Data Gempa Indonesia')
    st.write('Silakan pilih halaman di sidebar untuk memulai analisis.')

# Halaman Visualisasi Berdasarkan Tahun
elif page == "Visualisasi Berdasarkan Tahun":
    # Input rentang tahun dari pengguna
    st.title('📊 **Visualisasi Data Gempa Bumi**')

    # Menentukan rentang tahun
    min_year = int(data['datetime'].min()[:4])
    max_year = int(data['datetime'].max()[:4])
    start_year, end_year = st.slider(
        'Pilih Rentang Tahun:',
        min_value=min_year,
        max_value=max_year,
        value=(2008, 2024)
    )

    # Filter data berdasarkan input rentang tahun
    filtered_data = filter_data_by_year_range(data, start_year, end_year)

    # Slider Magnitudo
    min_mag, max_mag = st.slider(
    'Pilih Rentang Magnitudo:',
    min_value=float(data['magnitude'].min()),
    max_value=float(data['magnitude'].max()),
    value=(0.64, 7.92)
    )

    # Filder data magnitudo
    filtered_data = filtered_data[(filtered_data['magnitude'] >= min_mag) & (filtered_data['magnitude'] <= max_mag)]


    # Visualisasi distribusi titik gempa berdasarkan wilayah
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

    # Tren aktivitas gempa per tahun
    st.subheader('📈 Tren Aktivitas Gempa per Tahun')
    activity_per_year = filtered_data.groupby('Year').size()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(activity_per_year.index, activity_per_year.values, marker='o', linestyle='-', color='#FF6347')
    ax.set_title('Tren Aktivitas Gempa per Tahun', fontsize=16, fontweight='bold')
    ax.set_xlabel('Tahun', fontsize=14)
    ax.set_ylabel('Jumlah Kejadian Gempa', fontsize=14)
    ax.grid(axis='both', linestyle='--', alpha=0.7)
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

    # Scatter Plot Magnitudo vs Kedalaman
    st.subheader('📊 Scatter Plot Magnitudo vs Kedalaman')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=filtered_data, x='depth', y='magnitude', alpha=0.7, color='red', ax=ax)
    ax.set_title('Magnitudo vs Kedalaman', fontsize=16, fontweight='bold')
    ax.set_xlabel('Kedalaman (km)', fontsize=14)
    ax.set_ylabel('Magnitudo', fontsize=14)
    ax.grid(True)
    st.pyplot(fig)



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

    # Pilih pulau-pulau yang ingin ditampilkan
    islands = ['Sumatera', 'Jawa', 'Kalimantan', 'Sulawesi', 'Papua']
    selected_island = st.selectbox('Pilih Pulau:', islands)

    # Tentukan rentang tahun
    min_year = int(data['datetime'].min()[:4])
    max_year = int(data['datetime'].max()[:4])
    start_year, end_year = st.slider(
        'Pilih Rentang Tahun:',
        min_value=min_year,
        max_value=max_year,
        value=(2008, 2024)
    )

    # Definisikan batas koordinat per pulau
    regions = {
        'Sumatera': ((-6, 6), (95, 105)),
        'Jawa': ((-9, -5), (105, 115)),
        'Kalimantan': ((-4, 3), (108, 119)),
        'Sulawesi': ((-3, 2), (119, 125)),
        'Papua': ((-10, 0), (131, 141))
    }

    # Filter data berdasarkan pilihan pulau dan rentang tahun
    (lat_min, lat_max), (lon_min, lon_max) = regions[selected_island]
    filtered_island_data = data[
        (data['latitude'] >= lat_min) & 
        (data['latitude'] <= lat_max) &
        (data['longitude'] >= lon_min) &
        (data['longitude'] <= lon_max)
    ]
    filtered_island_data = filter_data_by_year_range(filtered_island_data, start_year, end_year)

    # Slider Magnitudo
    min_mag, max_mag = st.slider(
        'Pilih Rentang Magnitudo:',
        min_value=float(data['magnitude'].min()),
        max_value=float(data['magnitude'].max()),
        value=(0.64, 7.92)
    )
    
    # Filter data magnitudo
    filtered_island_data = filtered_island_data[
        (filtered_island_data['magnitude'] >= min_mag) & 
        (filtered_island_data['magnitude'] <= max_mag)
    ]
    
    # Visualisasi rata-rata magnitudo per tahun
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

    # Visualisasi Gempa Berdasarkan tahun
    st.subheader(f'📊 Frekuensi Gempa per Tahun di Pulau {selected_island}')
    freq_per_year = filtered_island_data.groupby('Year').size()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(freq_per_year.index, freq_per_year.values, color='orange')
    ax.set_title(f'Frekuensi Gempa per Tahun di Pulau {selected_island}', fontsize=16, fontweight='bold')
    ax.set_xlabel('Tahun', fontsize=14)
    ax.set_ylabel('Jumlah Gempa', fontsize=14)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    st.subheader(f'🗺️ Heatmap Magnitudo di Pulau {selected_island}')
    
    # Filter data dengan menghapus baris yang memiliki NaN di latitude, longitude, atau magnitude
    filtered_island_data_cleaned = filtered_island_data.dropna(subset=['latitude', 'longitude', 'magnitude'])
    
    # Menyiapkan peta
    m = folium.Map(location=[(lat_min + lat_max) / 2, (lon_min + lon_max) / 2], zoom_start=6)
    
    # Menyiapkan data untuk heatmap
    heat_data = [[row['latitude'], row['longitude'], row['magnitude']] for index, row in filtered_island_data_cleaned.iterrows()]
    
    # Menambahkan heatmap ke peta
    if heat_data:
        HeatMap(heat_data, radius=15).add_to(m)
        st_folium(m, width=700, height=500)
    else:
        st.warning(f"Tidak ada data gempa di Pulau {selected_island}.")


# Halaman Clustering Lokasi Gempa
elif page == "Clustering Lokasi Gempa":
    st.subheader('📊 Clustering Lokasi Gempa')

    # Filter data dengan kolom yang relevan dan tanpa NaN
    clustering_data = data[['latitude', 'longitude', 'magnitude']].dropna()

    # Pilih jumlah cluster
    num_clusters = st.slider('Pilih Jumlah Cluster:', min_value=2, max_value=10, value=3)

    # K-Means clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    clustering_data['cluster'] = kmeans.fit_predict(clustering_data)

    # Visualisasi hasil clustering pada scatter plot
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        clustering_data['longitude'], clustering_data['latitude'],
        c=clustering_data['cluster'], cmap='viridis', alpha=0.7
    )
    legend = ax.legend(*scatter.legend_elements(), title="Cluster")
    ax.add_artist(legend)
    ax.set_title('Hasil Clustering Lokasi Gempa', fontsize=16, fontweight='bold')
    ax.set_xlabel('Longitude', fontsize=14)
    ax.set_ylabel('Latitude', fontsize=14)
    st.pyplot(fig)

# Halaman Prediksi Risiko Wilayah
elif page == "Prediksi Risiko Wilayah":
    st.subheader('📈 Prediksi Tingkat Risiko Wilayah')

    # Menambahkan kolom risiko: High (1) jika magnitudo > 6, Low (0) jika magnitudo <= 6
    data['risk'] = np.where(data['magnitude'] > 6, 1, 0)

    # Fitur dan label
    features = ['latitude', 'longitude', 'depth']
    X = data[features].dropna()
    y = data['risk'][X.index]

    # Split data untuk training dan testing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Random Forest Classifier
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    # Prediksi pada data testing
    y_pred = model.predict(X_test)

    # Menampilkan hasil evaluasi model
    st.text('Hasil Evaluasi Model:')
    st.text(classification_report(y_test, y_pred))

    # Visualisasi prediksi pada data test
    st.subheader('Visualisasi Prediksi Risiko')
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        X_test['longitude'], X_test['latitude'],
        c=y_pred, cmap='coolwarm', alpha=0.7
    )
    legend = ax.legend(*scatter.legend_elements(), title="Predicted Risk")
    ax.add_artist(legend)
    ax.set_title('Hasil Prediksi Risiko', fontsize=16, fontweight='bold')
    ax.set_xlabel('Longitude', fontsize=14)
    ax.set_ylabel('Latitude', fontsize=14)
    st.pyplot(fig)


