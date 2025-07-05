import pandas as pd
import os

# --- PENGATURAN NAMA FILE ---
INPUT_CSV_FILE = "Data_cleaning_sipa.csv"
OUTPUT_DIR = "processed_data"
OUTPUT_PARQUET_FILE = f"{OUTPUT_DIR}/bansos_data_cleaned.parquet"

def preprocess_real_data():
    """
    Membaca data asli, melakukan pembersihan dasar.
    """
    print("Memulai proses pre-processing data...")

    # Pastikan file input ada
    if not os.path.exists(INPUT_CSV_FILE):
        print(f"Error: File '{INPUT_CSV_FILE}' tidak ditemukan.")
        print("Pastikan file tersebut berada di folder yang sama dengan skrip ini.")
        return

    # Buat direktori output jika belum ada
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Direktori '{OUTPUT_DIR}' dibuat.")

    # Membaca data CSV asli
    print(f"Membaca file '{INPUT_CSV_FILE}'...")
    try:
        df = pd.read_csv(INPUT_CSV_FILE)
    except Exception as e:
        print(f"Terjadi error saat membaca file CSV: {e}")
        return
        
    print("File CSV berhasil dibaca. Informasi Data:")
    df.info()

    df.to_parquet(OUTPUT_PARQUET_FILE)
    print(f"\nData berhasil diproses dan disimpan ke: '{OUTPUT_PARQUET_FILE}'")


if __name__ == '__main__':
    preprocess_real_data()
