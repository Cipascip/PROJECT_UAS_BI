import pandas as pd
import os
import csv # Impor modul csv

# --- PENGATURAN NAMA FILE ---
INPUT_CSV_FILE = "Data_cleaning_sipa.csv"
OUTPUT_DIR = "processed_data"
OUTPUT_PARQUET_FILE = f"{OUTPUT_DIR}/bansos_data_cleaned.parquet"

def preprocess_real_data():
    """
    Membaca data asli dengan metode yang lebih robust, membersihkan, dan menyimpannya.
    """
    print(f"Memulai proses pre-processing dari '{INPUT_CSV_FILE}'...")

    if not os.path.exists(INPUT_CSV_FILE):
        print(f"Error: File '{INPUT_CSV_FILE}' tidak ditemukan!")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Direktori '{OUTPUT_DIR}' berhasil dibuat.")

    # --- PERBAIKAN UTAMA: Menggunakan Modul `csv` untuk Parsing ---
    print("Membaca file CSV menggunakan modul 'csv'...")
    try:
        with open(INPUT_CSV_FILE, 'r', encoding='latin-1', newline='') as f:
            # Menggunakan csv.reader dengan delimiter titik-koma
            reader = csv.reader(f, delimiter=';')
            
            # Membaca semua baris
            all_rows = list(reader)
            
            # Ambil header dan bersihkan
            header = [h.strip().lower() for h in all_rows[0]]
            
            # Ambil data
            data = all_rows[1:]
            
            # Buat DataFrame
            df = pd.DataFrame(data, columns=header)
            print("File CSV berhasil dibaca dan DataFrame dibuat.")
            
    except Exception as e:
        print(f"Terjadi error saat membaca atau memproses file: {e}")
        return
        
    print("Nama kolom awal setelah parsing yang benar:", df.columns.tolist())

    # --- PENGUBAHAN NAMA KOLOM DAN PEMBERSIHAN (SAMA SEPERTI SEBELUMNYA) ---
    column_mapping = {
        'nama kk': 'nama_penerima',
        'provinsi': 'provinsi',
        'usia': 'usia',
        'pekerjaan': 'jenis_pekerjaan',
        'kse': 'skor_kse',
        'kategori': 'status_kse' 
    }
    df.rename(columns=column_mapping, inplace=True)
    
    if 'pendapatan' in df.columns:
        df['pendapatan'] = df['pendapatan'].astype(str).replace(r'[^\d]', '', regex=True)
        df['pendapatan'].replace('', '0', inplace=True)
        df['pendapatan'] = pd.to_numeric(df['pendapatan'], errors='coerce').fillna(0)

    # Pastikan kolom-kolom yang akan dikonversi ada sebelum diakses
    if 'usia' in df.columns and 'skor_kse' in df.columns:
        df['usia'] = pd.to_numeric(df['usia'], errors='coerce')
        df['skor_kse'] = pd.to_numeric(df['skor_kse'], errors='coerce')
        
        df.dropna(subset=['usia', 'skor_kse'], inplace=True) 
        df['usia'] = df['usia'].astype(int)
    else:
        print("Error: Kolom 'usia' atau 'skor_kse' tidak ditemukan setelah rename.")
        return

    print("Data setelah pembersihan:")
    df.info()

    df.to_parquet(OUTPUT_PARQUET_FILE)
    print(f"\nData berhasil diproses dan disimpan ke: '{OUTPUT_PARQUET_FILE}'")

if __name__ == '__main__':
    preprocess_real_data()
