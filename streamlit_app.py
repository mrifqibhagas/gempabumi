import pandas as pd
import streamlit as st

# Fungsi untuk memfilter data berdasarkan pulau
def filter_data_by_region(data, regions_to_include):
    # Koordinat untuk masing-masing pulau
    regions = {
        'Sumatera': ((-6, 6), (95, 105)),
        'Jawa': ((-9, -5), (105, 115)),
        'Kalimantan': ((-4, 3), (108, 119)),
        'Sulawesi': ((-3, 2), (119, 125)),
        'Papua': ((-10, 0), (131, 141))
    }

    # Memilih data yang sesuai dengan pulau yang dipilih oleh pengguna
    filtered_data = pd.DataFrame()
    for region in regions_to_include:
        if region in regions:
            (lat_min, lat_max), (lon_min, lon_max) = regions[region]
            region_data = data[(data['latitude'] >= lat_min) & (data['latitude'] <= lat_max) &
                               (data['longitude'] >= lon_min) & (data['longitude'] <= lon_max)]
            filtered_data = pd.concat([filtered_data, region_data])

    return filtered_data

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
    #st.image('header_image.png', use_container_width=True)

elif page == "Visualisasi Berdasarkan Tahun":
    # Halaman visualisasi berdasarkan tahun yang sudah ada sebelumnya
    st.title('📊 **Visualisasi Data Gempa Berdasarkan Tahun**')
    start_year = st.slider('Pilih Rentang Tahun:', min_value=2010, max_value=2024, value=(2010, 2015))
    
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
    selected_regions = st.multiselect(
        'Pilih Pulau untuk Visualisasi:', 
        ['Sumatera', 'Jawa', 'Kalimantan', 'Sulawesi', 'Papua'], 
        default=['Sumatera', 'Jawa']  # Defaultnya Sumatera dan Jawa dipilih
    )

    # Filter data berdasarkan pilihan pulau
    filtered_data = filter_data_by_region(data, selected_regions)

    # Menampilkan jumlah data yang terpilih
    st.write(f'Jumlah Kejadian Gempa di Pulau-pulau yang Dipilih: {filtered_data.shape[0]}')

    # Menampilkan preview data terpilih (optional)
    st.write(filtered_data.head())
