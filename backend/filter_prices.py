import pandas as pd
import os

def is_nsfw(title, slug):
    title_lower = str(title).lower()
    slug_lower = str(slug).lower()
    
    # Standalone word checks for sensitive keywords to avoid partial matches (e.g. "Section" or "Essex")
    words = set(title_lower.split() + slug_lower.replace('-', ' ').split())
    strict_nsfw_words = {
        'sex', 'porn', 'hentai', 'futanari', 'erotic', 'xxx', 'boobs', 
        'nudity', 'nude', 'naked', 'milf', 'deepthroat', 'eroge', 'lewd',
        'ecchi', 'cum', 'orgasm', 'masturbate', 'masturbation', 'penis', 'vagina'
    }
    if any(w in strict_nsfw_words for w in words):
        return True
        
    # Substring checks for highly specific phrases
    nsfw_substrings = [
        'pornpack', 'porn-pack', 'sex-game', 'erotic-game', 
        'hentai-game', 'waifu-sex', 'mom got stuck', 'super deepthroat'
    ]
    if any(sub in title_lower or sub in slug_lower for sub in nsfw_substrings):
        return True
        
    return False

def filter_game_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(current_dir, 'data', 'games.csv')
    output_path = os.path.join(current_dir, 'data', 'games_with_prices.csv')

    print("==================================================")
    print("   PROSES PREPROCESSING & DATA CLEANING GAME      ")
    print("==================================================")

    if not os.path.exists(input_path):
        print(f"Error: File sumber tidak ditemukan di {input_path}")
        return

    print(f"Membaca file data mentah: {input_path}...")
    df = pd.read_csv(input_path)
    total_raw_rows = len(df)
    print(f"Total baris data mentah terdeteksi: {total_raw_rows} baris")

    # 1. Bersihkan nilai rilis NaN menjadi string kosong terlebih dahulu
    df['released'] = df['released'].fillna('')

    # 2. Proses filtering
    print("\nMelakukan pembersihan data (filtering)...")
    print("- Kriteria 1: Menghapus game tanpa harga (kolom 'price_idr' kosong).")
    print("- Kriteria 2: Menghapus game berkonten dewasa / NSFW (Porn, Hentai, dll).")
    
    # Konversi kolom harga ke numerik untuk validasi
    df['price_idr_numeric'] = pd.to_numeric(df['price_idr'], errors='coerce')
    
    # Lakukan filter ganda: harus memiliki harga DAN bukan NSFW
    filtered_rows = []
    nsfw_removed_count = 0
    price_removed_count = 0
    
    for idx, row in df.iterrows():
        # Cek Batasan Harga
        if pd.isna(row['price_idr_numeric']):
            price_removed_count += 1
            continue
            
        # Cek Batasan Konten Dewasa / NSFW
        if is_nsfw(row['name'], row['slug']):
            nsfw_removed_count += 1
            continue
            
        filtered_rows.append(row)
        
    filtered_df = pd.DataFrame(filtered_rows)
    
    # Hapus kolom pembantu
    if not filtered_df.empty:
        filtered_df = filtered_df.drop(columns=['price_idr_numeric'])
    
    total_filtered_rows = len(filtered_df)

    print("\n---------------- Hasil Pembersihan ----------------")
    print(f"Baris sebelum difilter: {total_raw_rows} baris")
    print(f"Baris dihapus karena TANPA HARGA: {price_removed_count} baris")
    print(f"Baris dihapus karena KONTEN NSFW: {nsfw_removed_count} baris")
    print(f"Baris setelah difilter (bersih): {total_filtered_rows} baris")
    print("--------------------------------------------------")

    # 3. Menyimpan file bersih
    print(f"\nMenyimpan data bersih ke: {output_path}...")
    filtered_df.to_csv(output_path, index=False)
    print("Proses data cleaning selesai dengan sukses!")
    print("==================================================")

if __name__ == '__main__':
    filter_game_data()
