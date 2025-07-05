import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide", page_title="Dashboard Analisis Bansos")
st.title("Dashboard Analisis Penerima Bantuan Sosial (Bansos)")
st.markdown("Dashboard interaktif untuk menganalisis data penerima bansos.")

@st.cache_data
def load_data():
    try:
        df = pd.read_parquet("processed_data/bansos_data_cleaned.parquet")
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error(
        "File `bansos_data_cleaned.parquet` tidak ditemukan. "
        "Pastikan Anda telah menjalankan `preprocess.py` di terminal Anda "
        "dengan perintah: `python preprocess.py`"
    )
    st.stop()

# ... (Kode sisanya dari jawaban sebelumnya sudah benar, salin dari sana) ...

# [Letakkan seluruh sisa kode app.py dari jawaban sebelumnya di sini]
# (Dimulai dari bagian "VALIDASI KOLOM PENTING")

# --- VALIDASI KOLOM (MENGGUNAKAN NAMA HURUF KECIL) ---
required_columns = ['provinsi', 'status_kse', 'skor_kse', 'jenis_pekerjaan', 'usia']
if not all(col in df.columns for col in required_columns):
    st.error(f"Kolom yang dibutuhkan tidak ditemukan. Pastikan kolom ini ada: {required_columns}")
    st.stop()

st.markdown("---")

# --- KONTEN ANALISIS ---

# 1. Jumlah Penerima per Provinsi berdasarkan KSE
st.subheader("1. Jumlah Penerima Bansos per Provinsi Berdasarkan Kelayakan (KSE)")
df['status_kse'] = df['status_kse'].replace({
    'menerima bansos': 'Layak (Menerima)',
    'Tidak menerima bansos': 'Tidak Layak'
})
kse_per_provinsi = df.groupby(['provinsi', 'status_kse']).size().reset_index(name='Jumlah')

fig1 = px.bar(kse_per_provinsi, x='provinsi', y='Jumlah', color='status_kse', barmode='stack',
              title='Komposisi Kelayakan Penerima Bansos per Provinsi',
              labels={'Jumlah': 'Jumlah Penerima', 'provinsi': 'Provinsi', 'status_kse': 'Status Kelayakan'},
              color_discrete_map={'Layak (Menerima)': '#2980B9', 'Tidak Layak': '#E74C3C'},
              height=600)
fig1.update_xaxes(categoryorder='total descending')
st.plotly_chart(fig1, use_container_width=True)

# 2. Peringkat Provinsi Berdasarkan Skor KSE Tertinggi
st.subheader("2. Peringkat Provinsi Berdasarkan Skor KSE Tertinggi")
st.markdown("Skor KSE yang lebih rendah menunjukkan kelayakan yang lebih tinggi.")
avg_skor_provinsi = df.groupby('provinsi')['skor_kse'].mean().reset_index().sort_values(by='skor_kse', ascending=True)
fig2 = px.bar(avg_skor_provinsi, x='skor_kse', y='provinsi', orientation='h',
              title='Rata-Rata Skor KSE per Provinsi (Terendah = Terbaik)',
              labels={'skor_kse': 'Rata-Rata Skor KSE', 'provinsi': 'Provinsi'}, text_auto='.2f', height=700)
fig2.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig2, use_container_width=True)

with st.expander("Lihat 10 Penerima dengan Skor Tertinggi di Provinsi Tertentu"):
    prov_terpilih = st.selectbox("Pilih Provinsi untuk detail:", sorted(df['provinsi'].unique()), key='skor_prov')
    if prov_terpilih:
        df_skor_sorted = df[df['provinsi'] == prov_terpilih].sort_values(by='skor_kse', ascending=True).head(10)
        st.dataframe(df_skor_sorted[['nama_penerima', 'skor_kse', 'status_kse']], use_container_width=True)

# 3. Distribusi per Jenis Pekerjaan
st.subheader("3. Distribusi Penerima Bansos per Jenis Pekerjaan")
provinsi_list_pie = ["Semua Provinsi"] + sorted(df['provinsi'].unique().tolist())
selected_province_pie = st.selectbox("Pilih Provinsi:", provinsi_list_pie, key='pekerjaan_prov')
df_pie = df if selected_province_pie == "Semua Provinsi" else df[df['provinsi'] == selected_province_pie]
judul_pie = f'Distribusi Pekerjaan Penerima ({selected_province_pie})'
pekerjaan_count = df_pie['jenis_pekerjaan'].value_counts().reset_index()
pekerjaan_count.columns = ['jenis_pekerjaan', 'Jumlah']
fig3 = px.pie(pekerjaan_count, names='jenis_pekerjaan', values='Jumlah', title=judul_pie, hole=0.3)
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

df_unemployed_filtered = df if provinsi_pengangguran == "Semua Provinsi" else df[df['provinsi'] == provinsi_pengangguran]
df_produktif_unemployed = df_unemployed_filtered[
    (df_unemployed_filtered['usia'] >= min_age) & 
    (df_unemployed_filtered['usia'] <= max_age) &
    (df_unemployed_filtered['jenis_pekerjaan'] == 'Tidak Bekerja')
]
if provinsi_pengangguran == "Semua Provinsi":
    judul_unemployed = f'Pengangguran Usia {min_age}-{max_age} tahun per Provinsi'
    pengangguran_per_provinsi = df_produktif_unemployed.groupby('provinsi').size().reset_index(name='Jumlah').sort_values(by='Jumlah', ascending=True)
    fig4 = px.bar(pengangguran_per_provinsi, y='provinsi', x='Jumlah', orientation='h', title=judul_unemployed,
                  labels={'Jumlah': 'Jumlah Pengangguran', 'provinsi': 'Provinsi'}, text_auto=True, height=700)
    st.plotly_chart(fig4, use_container_width=True)
else:
    judul_unemployed = f'Pengangguran Usia {min_age}-{max_age} tahun di {provinsi_pengangguran}'
    jumlah_pengangguran = len(df_produktif_unemployed)
    st.metric(label=judul_unemployed, value=f"{jumlah_pengangguran} orang")
