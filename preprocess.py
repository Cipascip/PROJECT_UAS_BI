import pandas as pd
import os

# --- PENGATURAN NAMA FILE ---
INPUT_CSV_FILE = "Data_cleaning_sipa.csv"
OUTPUT_DIR = "processed_data"
OUTPUT_PARQUET_FILE = f"{OUTPUT_DIR}/bansos_data_cleaned.parquet"

def preprocess_real_data():
    """
    Membaca data asli, membersihkan dan mengubah nama kolom, lalu menyimpannya sebagai Parquet.
    """
    print(f"Memulai proses pre-processing data dari '{INPUT_CSV_FILE}'...")

    if not os.path.exists(INPUT_CSV_FILE):
        print(f"Error: File '{INPUT_CSV_FILE}' tidak ditemukan!")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Direktori '{OUTPUT_DIR}' berhasil dibuat.")

    # Membaca data CSV asli dengan separator titik-koma (;)
    print("Membaca file CSV...")
    try:
        # ----> PERBAIKAN UTAMA ADA DI BARIS INI <----
        # Menambahkan encoding='latin-1' yang lebih toleran terhadap karakter non-UTF8
        df = pd.read_csv(INPUT_CSV_FILE, sep=';', encoding='latin-1')
        print("File CSV berhasil dibaca.")
    except Exception as e:
        print(f"Terjadi error saat membaca file CSV: {e}")
        return
        
    # Membersihkan spasi di awal/akhir nama kolom
    df.columns = df.columns.str.strip()
    print("Nama kolom setelah dibersihkan dari spasi:", df.columns.tolist())

    # --- PENGUBAHAN NAMA KOLOM AGAR SESUAI DENGAN KEBUTUHAN APLIKASI ---
    column_mapping = {
        'NAMA KK': 'Nama_Penerima',
        'PROVINSI': 'Provinsi',
        'USIA': 'Usia',
        'PEKERJAAN': 'Jenis_Pekerjaan',
        'KSE': 'Skor_KSE',
        'KATEGORI': 'Status_KSE'
    }
    df.rename(columns=column_mapping, inplace=True)
    
    # --- PEMBERSIHAN DATA LANJUTAN ---
    if 'PENDAPATAN' in df.columns:
        # Menghapus semua karakter non-numerik sebelum konversi
        df['PENDAPATAN'] = df['PENDAPATAN'].astype(str).replace(r'[^\d]', '', regex=True)
        # Mengisi nilai kosong yang mungkin muncul setelah pembersihan dengan 0
        df['PENDAPATAN'].replace('', '0', inplace=True)
        df['PENDAPATAN'] = pd.to_numeric(df['PENDAPATAN'], errors='coerce').fillna(0)

    # Pastikan tipe data Usia dan Skor KSE adalah numerik
    df['Usia'] = pd.to_numeric(df['Usia'], errors='coerce')
    df['Skor_KSE'] = pd.to_numeric(df['Skor_KSE'], errors='coerce')

    df.dropna(subset=['Usia', 'Skor_KSE'], inplace=True) 
    df['Usia'] = df['Usia'].astype(int)
    
    print(f"Data setelah pembersihan memiliki {df.shape[0]} baris.")

    # Menyimpan DataFrame yang sudah bersih ke format Parquet
    df.to_parquet(OUTPUT_PARQUET_FILE)
    print(f"\nData berhasil diproses dan disimpan ke: '{OUTPUT_PARQUET_FILE}'")


if __name__ == '__main__':
    preprocess_real_data()
