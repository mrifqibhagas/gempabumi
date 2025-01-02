import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Fungsi untuk memfilter data berdasarkan pulau
def filter_data_by_region(data, region):
    regions = {
        'Sumatera': ((-6, 6), (95, 105)),
        'Jawa': ((-9, -5), (105, 115)),
        'Kalimantan': ((-4, 3), (108, 119)),
        'Sulawesi': ((-3, 2), (119, 125)),
        'Papua': ((-10, 0), (131, 141))
    }

    # Mengambil koordinat latitude dan longitude untuk wilayah yang dipilih
    if region in regions:
        (lat_min, lat_max), (lon_min, lon_max) = regions[region]
        filtered_data = data[(data['latitude'] >= lat_min) & (data['latitude'] <= lat_max) &
                             (data['longitude'] >= lon_min) & (data['longitude'] <= lon_max)]
        return filtered_data
    else:
        return data

# Load dataset
file_path = 'katalog_gempa2.csv'  # Ganti dengan path file Anda
data = pd.read_csv(file_path, sep=';', low_memory=False)

# Streamlit UI
st.set_page_config(page_title='Analisis Data Gempa Bumi', layout='wide')

# Sidebar untuk navigasi
st.sidebar.title("Navigasi")
page = st.sidebar.radio("Pilih Halaman", ["Beranda", "Visualisasi Berdasarkan Tahun", "Visualisasi Berdasarkan Pulau"])

if page == "Beranda":
    st.title('📊 **Analisis Data Gempa Bumi**')
    st.markdown("""
    **Selamat datang di aplikasi analisis data gempa bumi Indonesia!**
    Di sini, Anda dapat melihat berbagai visualisasi tentang data kejadian gempa di Indonesia berdasarkan wilayah dan tahun.
    """)
    st.image('header_image.png', use_container_width=True)

elif page == "Visualisasi Berdasarkan Tahun":
    # Halaman visualisasi berdasarkan tahun yang sudah ada sebelumnya
    st.title('📊 **Visualisasi Data Gempa Berdasarkan Tahun**')
    start_year = st.slider('Pilih Rentang Tahun:', min_value=2010, max_value=2025, value=(2010, 2015))
    
    # Filter data berdasarkan rentang tahun
    filtered_data = filter_data_by_year_range(data, start_year[0], start_year[1])

    # Visualisasi distribusi titik gempa berdasarkan tahun
    st.subheader('📍 Distribusi Titik Gempa Berdasarkan Tahun')
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(filtered_data['longitude'], filtered_data['latitude'], color='blue', alpha=0.5, s=10)
    ax.set_title('Distribusi Titik Gempa Berdasarkan Tahun', fontsize=16, fontweight='bold')
    ax.set_xlabel('Longitude', fontsize=14)
    ax.set_ylabel('Latitude', fontsize=14)
    ax.grid(True)
    st.pyplot(fig)

elif page == "Visualisasi Berdasarkan Pulau":
    # Halaman visualisasi berdasarkan pulau
    st.title('📊 **Visualisasi Data Gempa Berdasarkan Pulau**')
    
    # Pilihan pulau dari pengguna
    region = st.selectbox('Pilih Pulau:', ['Sumatera', 'Jawa', 'Kalimantan', 'Sulawesi', 'Papua'])
    
    # Filter data berdasarkan pilihan pulau
    filtered_data = filter_data_by_region(data, region)

    # Visualisasi distribusi titik gempa berdasarkan pulau
    st.subheader(f'📍 Distribusi Titik Gempa di Pulau {region}')
    
    # Menghitung jumlah kejadian gempa per wilayah (pulau)
    region_counts = filtered_data.shape[0]

    # Plot distribusi titik gempa
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(filtered_data['longitude'], filtered_data['latitude'], color='orange', alpha=0.5, s=10)
    ax.set_title(f'Distribusi Titik Gempa di Pulau {region}', fontsize=16, fontweight='bold')
    ax.set_xlabel('Longitude', fontsize=14)
    ax.set_ylabel('Latitude', fontsize=14)
    ax.grid(True)
    st.pyplot(fig)

    st.write(f'Jumlah Kejadian Gempa di Pulau {region}: {region_counts}')
