import pandas as pd
import os

def filter_game_prices():
    # Tentukan path file secara dinamis
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(current_dir, 'data', 'games.csv')
    output_path = os.path.join(current_dir, 'data', 'games_with_prices.csv')

    print("==================================================")
    print("   PROSES PREPROCESSING & DATA CLEANING GAME      ")
    print("==================================================")

    # 1. Validasi keberadaan file games.csv
    if not os.path.exists(input_path):
        print(f"Error: File sumber tidak ditemukan di {input_path}")
        print("Pastikan file games.csv sudah diletakkan di dalam folder backend/data/")
        return

    print(f"Membaca file data mentah: {input_path}...")
    
    # 2. Load dataset menggunakan pandas
    df = pd.read_csv(input_path)
    total_raw_rows = len(df)
    print(f"Total baris data mentah terdeteksi: {total_raw_rows} baris")

    # 3. Proses filtering
    print("\nMelakukan pembersihan data (filtering)...")
    print("Kriteria: Menghapus game yang kolom 'price_idr'-nya kosong (null/NaN) atau tidak terisi.")
    
    # Filter baris yang memiliki nilai pada kolom 'price_idr' (tidak NaN dan tidak kosong)
    # Kami juga memastikan tipe data price_idr terkonversi menjadi numerik dengan baik
    df['price_idr_numeric'] = pd.to_numeric(df['price_idr'], errors='coerce')
    
    # Lakukan penyaringan
    filtered_df = df[df['price_idr_numeric'].notna()].copy()
    
    # Hapus kolom pembantu numerik agar struktur CSV asli tetap terjaga
    filtered_df = filtered_df.drop(columns=['price_idr_numeric'])
    
    total_filtered_rows = len(filtered_df)
    deleted_rows = total_raw_rows - total_filtered_rows

    print("\n---------------- Hasi Pembersihan ----------------")
    print(f"Baris sebelum difilter: {total_raw_rows} baris")
    print(f"Baris dihapus (tanpa harga): {deleted_rows} baris")
    print(f"Baris setelah difilter (bersih): {total_filtered_rows} baris")
    print("--------------------------------------------------")

    # 4. Menyimpan file bersih
    print(f"\nMenyimpan data bersih ke: {output_path}...")
    filtered_df.to_csv(output_path, index=False)
    print("Proses data cleaning selesai dengan sukses!")
    print("==================================================")

if __name__ == '__main__':
    filter_game_prices()
