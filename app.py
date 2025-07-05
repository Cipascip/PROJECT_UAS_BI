import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Konfigurasi Halaman Streamlit
st.set_page_config(layout="wide", page_title="Dashboard Analisis Bansos")

# Judul Dashboard
st.title("Dashboard Analisis Penerima Bantuan Sosial (Bansos)")
st.markdown("Dashboard interaktif untuk menganalisis data penerima bansos.")

# --- MEMUAT DATA YANG SUDAH DIPROSES ---
@st.cache_data
def load_data():
    """Memuat data bersih dari file Parquet."""
    try:
        df = pd.read_parquet("processed_data/bansos_data_cleaned.parquet")
        return df
    except FileNotFoundError:
        return None

# Memuat data dan menangani error jika file tidak ada
df = load_data()

if df is None:
    st.error(
        "File data yang telah diproses (processed_data/bansos_data_cleaned.parquet) tidak ditemukan. "
        "Mohon jalankan skrip `preprocess.py` terlebih dahulu di terminal dengan perintah: `python preprocess.py`"
    )
    st.stop()

st.markdown("---")

# --- KONTEN ANALISIS ---

# 1. Jumlah Penerima per Provinsi berdasarkan KSE
st.subheader("1. Jumlah Penerima Bansos per Provinsi Berdasarkan Kelayakan (KSE)")
kse_per_provinsi = df.groupby(['Provinsi', 'Status_KSE']).size().reset_index(name='Jumlah')

fig1 = px.bar(
    kse_per_provinsi,
    x='Provinsi',
    y='Jumlah',
    color='Status_KSE',
    barmode='stack', 
    title='Komposisi Kelayakan Penerima Bansos per Provinsi',
    labels={'Jumlah': 'Jumlah Penerima', 'Provinsi': 'Provinsi', 'Status_KSE': 'Status KSE'},
    color_discrete_map={
        'Sangat Layak': '#2980B9',
        'Layak': '#5DADE2',
        'Dipertimbangkan': '#AED6F1'
    },
    text_auto=False, 
    height=600 
)
fig1.update_xaxes(categoryorder='total descending') 
st.plotly_chart(fig1, use_container_width=True)


# 2. Urutan Penerima Tertinggi Berdasarkan Skor KSE per Provinsi
st.subheader("2. Peringkat Provinsi Berdasarkan Skor KSE Tertinggi")
st.markdown("Skor KSE yang lebih rendah menunjukkan kelayakan yang lebih tinggi. Grafik ini menampilkan rata-rata skor KSE per provinsi, diurutkan dari yang paling layak (skor terendah).")

avg_skor_provinsi = df.groupby('Provinsi')['Skor_KSE'].mean().reset_index().sort_values(by='Skor_KSE', ascending=True)

fig2 = px.bar(
    avg_skor_provinsi,
    x='Skor_KSE',
    y='Provinsi',
    orientation='h',
    title='Rata-Rata Skor KSE per Provinsi (Terendah = Terbaik)',
    labels={'Skor_KSE': 'Rata-Rata Skor KSE', 'Provinsi': 'Provinsi'},
    text_auto='.2f',
    height=700 # Menambah tinggi karena lebih banyak provinsi
)
fig2.update_layout(yaxis={'categoryorder':'total ascending'}) 
st.plotly_chart(fig2, use_container_width=True)

with st.expander("Lihat 10 Penerima dengan Skor Tertinggi di Provinsi Tertentu"):
    prov_terpilih = st.selectbox("Pilih Provinsi untuk detail:", sorted(df['Provinsi'].unique()), key='skor_prov')
    df_skor_sorted = df[df['Provinsi'] == prov_terpilih].sort_values(by='Skor_KSE', ascending=True).head(10)
    st.write(f"Detail 10 penerima di **{prov_terpilih}**:")
    st.dataframe(df_skor_sorted[['Nama_Penerima', 'Skor_KSE', 'Status_KSE']], use_container_width=True)


# 3. Distribusi per Jenis Pekerjaan
st.subheader("3. Distribusi Penerima Bansos per Jenis Pekerjaan")
provinsi_list_pie = ["Semua Provinsi"] + sorted(df['Provinsi'].unique().tolist())
selected_province_pie = st.selectbox("Pilih Provinsi:", provinsi_list_pie, key='pekerjaan_prov')

if selected_province_pie == "Semua Provinsi":
    df_pie = df
    judul_pie = 'Distribusi Pekerjaan Penerima (Semua Provinsi)'
else:
    df_pie = df[df['Provinsi'] == selected_province_pie]
    judul_pie = f'Distribusi Pekerjaan Penerima di {selected_province_pie}'

pekerjaan_count = df_pie['Jenis_Pekerjaan'].value_counts().reset_index()
pekerjaan_count.columns = ['Jenis_Pekerjaan', 'Jumlah']

fig3 = px.pie(
    pekerjaan_count,
    names='Jenis_Pekerjaan',
    values='Jumlah',
    title=judul_pie,
    hole=0.3
)
fig3.update_traces(textposition='inside', textinfo='percent+label', sort=True)
st.plotly_chart(fig3, use_container_width=True)


# 4. Urutan Jumlah Pengangguran Usia Produktif
st.subheader("4. Jumlah Pengangguran Usia Produktif per Provinsi")
col1, col2, col3 = st.columns(3)
with col1:
    min_age = st.slider("Batas Usia Produktif Minimum:", 0, 80, 18, key='min_age_slider') 
with col2:
    max_age_value = max(min_age + 1, 55)
    max_age = st.slider("Batas Usia Produktif Maksimum:", min_age, 80, max_age_value, key='max_age_slider')
with col3:
    provinsi_pengangguran = st.selectbox("Pilih Provinsi:", provinsi_list_pie, key='pengangguran_prov')

if provinsi_pengangguran == "Semua Provinsi":
    df_unemployed_filtered = df
    judul_unemployed = f'Pengangguran Usia {min_age}-{max_age} tahun per Provinsi'
else:
    df_unemployed_filtered = df[df['Provinsi'] == provinsi_pengangguran]
    judul_unemployed = f'Pengangguran Usia {min_age}-{max_age} tahun di {provinsi_pengangguran}'
    
df_produktif_unemployed = df_unemployed_filtered[
    (df_unemployed_filtered['Usia'] >= min_age) & 
    (df_unemployed_filtered['Usia'] <= max_age) &
    (df_unemployed_filtered['Jenis_Pekerjaan'] == 'Tidak Bekerja')
]

if provinsi_pengangguran == "Semua Provinsi":
    pengangguran_per_provinsi = df_produktif_unemployed.groupby('Provinsi').size().reset_index(name='Jumlah').sort_values(by='Jumlah', ascending=True)

    fig4 = px.bar(
        pengangguran_per_provinsi,
        y='Provinsi',
        x='Jumlah',
        orientation='h',
        title=judul_unemployed,
        labels={'Jumlah': 'Jumlah Pengangguran', 'Provinsi': 'Provinsi'},
        text_auto=True,
        height=700 # Menambah tinggi karena lebih banyak provinsi
    )
    st.plotly_chart(fig4, use_container_width=True)
else:
    jumlah_pengangguran = len(df_produktif_unemployed)
    st.metric(label=judul_unemployed, value=f"{jumlah_pengangguran} orang")
