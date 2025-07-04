import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Konfigurasi Halaman Streamlit
st.set_page_config(layout="wide", page_title="Dashboard Analisis Bansos")

# Judul Dashboard
st.title("Dashboard Analisis Penerima Bantuan Sosial (Bansos)")
st.markdown("Dashboard interaktif untuk menganalisis data penerima bansos.")

# --- MEMBUAT DATA SAMPEL (MOCK DATA) ---
# @st.cache_data digunakan agar data hanya dibuat sekali dan tidak berubah saat ada interaksi
@st.cache_data
def create_mock_data():
    """Membuat DataFrame sampel untuk analisis."""
    np.random.seed(42) # Agar hasil random selalu sama
    jumlah_data = 5000
    
    provinsi = ['DKI Jakarta', 'Jawa Barat', 'Jawa Tengah', 'Jawa Timur', 'Banten', 'Sumatera Utara']
    status_kse = ['Sangat Layak', 'Layak', 'Dipertimbangkan']
    jenis_pekerjaan = [
        'Petani', 'Buruh Harian', 'Nelayan', 'Pedagang Kecil', 
        'Tidak Bekerja', 'Guru Honorer', 'Lainnya'
    ]
    
    data = {
        'Nama_Penerima': [f'Penerima_{i}' for i in range(jumlah_data)],
        'Usia': np.random.randint(18, 70, size=jumlah_data),
        'Provinsi': np.random.choice(provinsi, jumlah_data),
        'Jenis_Pekerjaan': np.random.choice(jenis_pekerjaan, jumlah_data, p=[0.2, 0.2, 0.1, 0.2, 0.1, 0.1, 0.1]),
        'Status_KSE': np.random.choice(status_kse, jumlah_data, p=[0.3, 0.5, 0.2]),
        'Skor_KSE': np.random.randint(40, 100, size=jumlah_data)
    }
    df = pd.DataFrame(data)
    return df

# Memuat data
df = create_mock_data()


# --- FILTER GLOBAL PER PROVINSI ---
st.markdown("---")
provinsi_list = ["Semua Provinsi"] + sorted(df['Provinsi'].unique().tolist())
selected_province = st.selectbox("Pilih Provinsi untuk disorot:", provinsi_list, help="Pilih provinsi untuk memfilter data pada chart di bawah.")


# --- PENYESUAIAN DATA BERDASARKAN FILTER ---
if selected_province == "Semua Provinsi":
    df_filtered = df.copy()
else:
    df_filtered = df[df['Provinsi'] == selected_province]


# --- KONTEN ANALISIS ---

# 1. Jumlah Penerima per Provinsi berdasarkan KSE
st.subheader("1. Jumlah Penerima Bansos per Provinsi Berdasarkan Kelayakan (KSE)")
kse_per_provinsi = df.groupby(['Provinsi', 'Status_KSE']).size().reset_index(name='Jumlah')
fig1 = px.bar(
    kse_per_provinsi,
    x='Provinsi',
    y='Jumlah',
    color='Status_KSE',
    barmode='group',
    title='Jumlah Penerima per Provinsi dan Status KSE',
    labels={'Jumlah': 'Jumlah Penerima', 'Provinsi': 'Provinsi', 'Status_KSE': 'Status KSE'},
    color_discrete_map={
        'Sangat Layak': '#2E86C1',
        'Layak': '#5DADE2',
        'Dipertimbangkan': '#AED6F1'
    },
    text_auto=True
)
fig1.update_traces(textposition='outside')
# Menambahkan highlight berdasarkan filter provinsi global
if selected_province != "Semua Provinsi":
    fig1.for_each_trace(lambda t: t.update(opacity=0.3) if t.name not in df_filtered['Status_KSE'].unique() else None)
    
    kse_selected = df_filtered.groupby(['Provinsi', 'Status_KSE']).size().reset_index(name='Jumlah')
    for status in kse_selected['Status_KSE'].unique():
        data_trace = kse_selected[kse_selected['Status_KSE'] == status]
        fig1.add_bar(x=data_trace['Provinsi'], y=data_trace['Jumlah'], name=f"{status} ({selected_province})")
st.plotly_chart(fig1, use_container_width=True)


# 2. Urutan Penerima Tertinggi Berdasarkan Skor KSE per Provinsi
st.subheader("2. Urutan Penerima Bansos Tertinggi Berdasarkan Skor KSE")
# Kontrol (widget) langsung di bawah judul, bukan di sidebar
provinsi_for_skor = st.selectbox("Pilih Provinsi untuk melihat skor tertinggi:", sorted(df['Provinsi'].unique()))

if provinsi_for_skor:
    df_skor_sorted = df[df['Provinsi'] == provinsi_for_skor].sort_values(by='Skor_KSE', ascending=True).head(10)
    df_skor_sorted.rename(columns={'Skor_KSE': 'Skor KSE (Terendah lebih baik)'}, inplace=True)
    st.write(f"10 Penerima dengan Skor KSE Tertinggi (skor terendah) di Provinsi **{provinsi_for_skor}**:")
    st.dataframe(df_skor_sorted[['Nama_Penerima', 'Usia', 'Jenis_Pekerjaan', 'Status_KSE', 'Skor KSE (Terendah lebih baik)']], use_container_width=True)


# 3. Distribusi per Jenis Pekerjaan
st.subheader("3. Distribusi Penerima Bansos per Jenis Pekerjaan")
st.write(f"Distribusi untuk: **{selected_province}**")
pekerjaan_count = df_filtered['Jenis_Pekerjaan'].value_counts().reset_index()
pekerjaan_count.columns = ['Jenis_Pekerjaan', 'Jumlah']
fig3 = px.bar(
    pekerjaan_count,
    x='Jumlah',
    y='Jenis_Pekerjaan',
    orientation='h',
    title=f'Distribusi Pekerjaan Penerima di {selected_province}',
    labels={'Jumlah': 'Jumlah Penerima', 'Jenis_Pekerjaan': 'Jenis Pekerjaan'},
    text_auto=True
)
fig3.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig3, use_container_width=True)


# 4. Urutan Pengangguran Usia Produktif
st.subheader("4. Urutan Jumlah Pengangguran Usia Produktif Terbesar per Provinsi")
# Kontrol/filter kategori usia produktif langsung di sini
col1, col2 = st.columns(2)
with col1:
    min_age = st.slider("Batas Usia Produktif Minimum:", 18, 40, 18)
with col2:
    max_age = st.slider("Batas Usia Produktif Maksimum:", 41, 65, 55)

# Analisis dilakukan berdasarkan filter usia di atas
df_produktif_unemployed = df[
    (df['Usia'] >= min_age) & 
    (df['Usia'] <= max_age) &
    (df['Jenis_Pekerjaan'] == 'Tidak Bekerja')
]
pengangguran_per_provinsi = df_produktif_unemployed.groupby('Provinsi').size().reset_index(name='Jumlah').sort_values(by='Jumlah', ascending=False)
fig4 = px.bar(
    pengangguran_per_provinsi,
    x='Provinsi',
    y='Jumlah',
    title=f'Jumlah Pengangguran Usia {min_age}-{max_age} tahun per Provinsi',
    labels={'Jumlah': 'Jumlah Pengangguran', 'Provinsi': 'Provinsi'},
    text_auto=True
)
st.plotly_chart(fig4, use_container_width=True)