import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi halaman Streamlit agar lebih lebar dan memberikan judul pada tab browser
st.set_page_config(layout="wide", page_title="Dashboard Analisis SIPA")

# --- FUNGSI UNTUK MEMUAT DATA ---
# Menggunakan cache agar data tidak perlu dimuat ulang setiap kali ada interaksi
@st.cache_data
def load_data():
    # Membaca file CSV
    df = pd.read_csv('Data_cleaning_sipa.csv')
    
    # --- PROSES PEMBERSIHAN DATA SEDERHANA ---
    # Menghapus spasi ekstra dari nama kolom
    df.columns = df.columns.str.strip()

    # Standarisasi nama Domisili/Provinsi yang tidak konsisten
    # Ini penting agar grouping berdasarkan provinsi menjadi akurat
    df['DOMISILI'] = df['DOMISILI'].str.replace('Bppn', 'Balikpapan', case=False)
    df['DOMISILI'] = df['DOMISILI'].str.replace('Bpp', 'Balikpapan', case=False)
    df['DOMISILI'] = df['DOMISILI'].str.replace('Bjrmasin', 'Banjarmasin', case=False)
    df['DOMISILI'] = df['DOMISILI'].str.replace('Palangkaraya', 'Palangka Raya', case=False)
    df['DOMISILI'] = df['DOMISILI'].str.replace('Plangkary', 'Palangka Raya', case=False)
    
    # Memastikan kolom 'PROVINSI' konsisten berdasarkan DOMISILI yang telah dibersihkan
    # Contoh: jika ada Domisili 'Bekasi' dengan Provinsi 'Kalimantan Timur' yang salah, ini bisa diperbaiki di sini
    # Untuk contoh ini, kita anggap provinsi di Kalimantan Timur konsisten
    kalimantan_timur_cities = ['Balikpapan', 'Samarinda', 'Bogor', 'Bekasi', 'Bengkulu']
    df.loc[df['DOMISILI'].isin(kalimantan_timur_cities), 'PROVINSI'] = 'Kalimantan Timur'
    
    return df

# Memanggil fungsi untuk memuat data
df = load_data()

# --- SIDEBAR UNTUK FILTER ---
st.sidebar.header("Filter Data")
kategori_filter = st.sidebar.selectbox(
    "Pilih Kategori:",
    options=['Semua Kategori', 'menerima bansos', 'Tidak menerima bansos'],
    index=0 # Default pilihan adalah 'Semua Kategori'
)

# --- FILTERING DATA FRAME BERDASARKAN PILIHAN DI SIDEBAR ---
if kategori_filter == 'Semua Kategori':
    df_filtered = df.copy()
else:
    df_filtered = df[df['KATEGORI'] == kategori_filter]

# --- JUDUL UTAMA DASHBOARD ---
st.title("📊 Dashboard Analisis Data SIPA")
st.markdown("Gunakan filter di samping untuk mengubah data yang ditampilkan.")
st.markdown("---")

# --- 1. JUMLAH PENERIMA BANSOS PER PROVINSI BERDASARKAN KSE ---
st.header("1. Jumlah Penduduk per Provinsi Berdasarkan KSE")
if not df_filtered.empty:
    # Mengelompokkan data berdasarkan provinsi dan KSE, lalu menghitung jumlahnya
    provinsi_kse_count = df_filtered.groupby(['PROVINSI', 'KSE']).size().reset_index(name='Jumlah')

    # Membuat bar chart dengan Plotly
    fig1 = px.bar(
        provinsi_kse_count,
        x='PROVINSI',
        y='Jumlah',
        color='KSE',
        title='Jumlah Penduduk per Provinsi dan Skor KSE',
        labels={'PROVINSI': 'Provinsi', 'Jumlah': 'Jumlah Penduduk', 'KSE': 'Skor KSE'},
        barmode='group' # Menampilkan bar berdampingan untuk perbandingan mudah
    )
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)

    # Menampilkan data dalam bentuk tabel
    st.write("Data Tabel:")
    st.dataframe(provinsi_kse_count)
else:
    st.warning("Tidak ada data untuk kategori yang dipilih.")
st.markdown("---")


# --- 2. URUTAN PENERIMA BANSOS TERTINGGI BERDASARKAN SKOR KSE PER PROVINSI ---
st.header("2. Peringkat Provinsi Berdasarkan Rata-Rata Skor KSE")
if not df_filtered.empty:
    # Mengelompokkan data berdasarkan provinsi dan menghitung rata-rata KSE
    provinsi_kse_avg = df_filtered.groupby('PROVINSI')['KSE'].mean().reset_index()
    provinsi_kse_avg = provinsi_kse_avg.sort_values(by='KSE', ascending=False)
    
    # Membuat bar chart dengan Plotly
    fig2 = px.bar(
        provinsi_kse_avg,
        x='PROVINSI',
        y='KSE',
        title='Peringkat Provinsi Berdasarkan Rata-Rata Skor KSE Tertinggi',
        labels={'PROVINSI': 'Provinsi', 'KSE': 'Rata-rata Skor KSE'}
    )
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)
    
    # Menampilkan data dalam bentuk tabel
    st.write("Data Tabel:")
    st.dataframe(provinsi_kse_avg)
else:
    st.warning("Tidak ada data untuk kategori yang dipilih.")
st.markdown("---")


# --- 3. DISTRIBUSI PENERIMA BANSOS PER JENIS PEKERJAAN ---
st.header("3. Distribusi Penduduk Berdasarkan Jenis Pekerjaan")
if not df_filtered.empty:
    pekerjaan_count = df_filtered['PEKERJAAN'].value_counts().reset_index()
    pekerjaan_count.columns = ['Pekerjaan', 'Jumlah']
    
    # Menggunakan kolom untuk menampilkan chart dan tabel berdampingan
    col1, col2 = st.columns(2)

    with col1:
        # Membuat pie chart dengan Plotly
        fig3 = px.pie(
            pekerjaan_count,
            names='Pekerjaan',
            values='Jumlah',
            title='Distribusi Jenis Pekerjaan',
            hole=0.3 # Membuat donut chart
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        # Menampilkan data dalam bentuk tabel
        st.write("Data Tabel:")
        st.dataframe(pekerjaan_count, use_container_width=True)
else:
    st.warning("Tidak ada data untuk kategori yang dipilih.")
st.markdown("---")


# --- 4. URUTAN JUMLAH PENGANGGURAN USIA PRODUKTIF TERBESAR PER PROVINSI ---
st.header("4. Peringkat Provinsi Berdasarkan Jumlah Pengangguran Usia Produktif")
st.markdown("Catatan: Usia produktif didefinisikan sebagai rentang usia 15-64 tahun.")
if not df_filtered.empty:
    # Filter data untuk pengangguran (Tidak Bekerja) dan usia produktif (15-64)
    pengangguran_produktif = df_filtered[
        (df_filtered['PEKERJAAN'] == 'Tidak Bekerja') &
        (df_filtered['USIA'].between(15, 64))
    ]
    
    if not pengangguran_produktif.empty:
        # Menghitung jumlah pengangguran produktif per provinsi
        pengangguran_count_provinsi = pengangguran_produktif.groupby('PROVINSI').size().reset_index(name='Jumlah Pengangguran Produktif')
        pengangguran_count_provinsi = pengangguran_count_provinsi.sort_values(by='Jumlah Pengangguran Produktif', ascending=False)
        
        # Membuat bar chart
        fig4 = px.bar(
            pengangguran_count_provinsi,
            x='PROVINSI',
            y='Jumlah Pengangguran Produktif',
            title='Jumlah Pengangguran Usia Produktif per Provinsi',
            labels={'PROVINSI': 'Provinsi', 'Jumlah Pengangguran Produktif': 'Jumlah Pengangguran'}
        )
        fig4.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig4, use_container_width=True)

        # Menampilkan data dalam bentuk tabel
        st.write("Data Tabel:")
        st.dataframe(pengangguran_count_provinsi)
    else:
        st.info("Tidak ditemukan data pengangguran usia produktif untuk kategori yang dipilih.")
else:
    st.warning("Tidak ada data untuk kategori yang dipilih.")