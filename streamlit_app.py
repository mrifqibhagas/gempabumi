import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import DBSCAN
import numpy as np
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
st.title('Analisis Data Gempa Bumi')

# Input rentang tahun dari pengguna
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

# Visualisasi rata-rata magnitude per tahun
average_magnitude = filtered_data.groupby('Year')['magnitude'].mean()

st.subheader(f'Rata-rata Magnitudo Gempa dari Tahun {start_year} hingga {end_year}')
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(average_magnitude, marker='o')
ax.set_title(f'Rata-rata Magnitudo Gempa dari Tahun {start_year} hingga {end_year}')
ax.set_xlabel('Tahun')
ax.set_ylabel('Rata-rata Magnitudo')
ax.grid(True)
st.pyplot(fig)

st.write('Jumlah Data yang Difilter:', len(filtered_data))
