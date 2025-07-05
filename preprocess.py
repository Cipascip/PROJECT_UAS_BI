import pandas as pd
import os

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
        df = pd.read_csv(INPUT_CSV_FILE, sep=';')
        print("File CSV berhasil dibaca.")
    except Exception as e:
        print(f"Terjadi error saat membaca file CSV: {e}")
        return

    # Membersihkan spasi di awal/akhir nama kolom
    df.columns = df.columns.str.strip()
    print("Nama kolom setelah dibersihkan dari spasi:", df.columns.tolist())

    # --- PENGUBAHAN NAMA KOLOM AGAR SESUAI DENGAN KEBUTUHAN APLIKASI ---
    # Ini adalah kunci untuk memperbaiki KeyError di app.py
    column_mapping = {
        'NAMA KK': 'Nama_Penerima',
        'PROVINSI': 'Provinsi',
        'USIA': 'Usia',
        'PEKERJAAN': 'Jenis_Pekerjaan',
        'KSE': 'Skor_KSE',
        'KATEGORI': 'Status_KSE' # Kita asumsikan KATEGORI adalah Status KSE (menerima/tidak)
    }
    df.rename(columns=column_mapping, inplace=True)
    
    # --- PEMBERSIHAN DATA LANJUTAN ---
    # Mengganti nilai 'menerima bansos' / 'Tidak menerima bansos' menjadi lebih standar jika diperlukan
    # Contoh ini tidak mengubahnya, tetapi ini adalah tempat untuk melakukannya
    print("Kolom setelah di-rename:", df.columns.tolist())
    
    # Menangani kolom 'PENDAPATAN' yang memiliki 'Rp' dan spasi
    if 'PENDAPATAN' in df.columns:
        df['PENDAPATAN'] = df['PENDAPATAN'].replace(r'[^\d]', '', regex=True).astype(float)
        
    # Pastikan tipe data Usia dan Skor KSE adalah numerik
    df['Usia'] = pd.to_numeric(df['Usia'], errors='coerce')
    df['Skor_KSE'] = pd.to_numeric(df['Skor_KSE'], errors='coerce')

    df.dropna(subset=['Usia', 'Skor_KSE'], inplace=True) # Hapus baris jika Usia atau Skor_KSE kosong
    df['Usia'] = df['Usia'].astype(int)
    
    print(f"Data setelah pembersihan memiliki {df.shape[0]} baris.")

    # Menyimpan DataFrame yang sudah bersih ke format Parquet
    df.to_parquet(OUTPUT_PARQUET_FILE)
    print(f"Data berhasil diproses dan disimpan ke: '{OUTPUT_PARQUET_FILE}'")

if __name__ == '__main__':
    preprocess_real_data()
