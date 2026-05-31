import requests
import pandas as pd
import time
import os
import re
from dotenv import load_dotenv


# --- Konfigurasi ---
load_dotenv()
RAWG_API_KEY = os.getenv('RAWG_API_KEY')
RAWG_PAGE_SIZE = 40  # RAWG max 40 per page
RAWG_TOTAL_GAMES = 100000  # Target jumlah game
RAWG_SLEEP = 1  # Detik antar request RAWG

STEAM_SLEEP = 1  # Detik antar request Steam (rate limit ~200/5 menit)

# Path dinamis relatif terhadap lokasi file fetch_data.py agar aman dijalankan dari CWD mana saja
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

OUTPUT_PATH = os.path.join(DATA_DIR, "games_with_prices.csv")
PROGRESS_PATH = os.path.join(DATA_DIR, "progress_temp.csv")


# --- Fungsi Ambil Data RAWG ---
def fetch_rawg_games(api_key, total_games=100000, page_size=400):
    base_url = "https://api.rawg.io/api/games"
    games_list = []
    pages = total_games // page_size + 1

    for page in range(1, pages + 1):
        params = {
            "key": api_key,
            "page_size": page_size,
            "page": page,
            "ordering": "-rating"
        }
        print(f"[RAWG] Fetching page {page}/{pages}...")
        try:
            response = requests.get(base_url, params=params, timeout=30)
            if response.status_code != 200:
                print(f"[RAWG] Failed page {page}: {response.status_code}")
                break
            data = response.json()
            results = data.get('results', [])
            for game in results:
                # Ekstrak Steam AppID dari stores
                steam_appid = None
                if 'stores' in game and game['stores']:
                    for store in game['stores']:
                        if store.get('store', {}).get('slug') == 'steam':
                            url = store.get('url')
                            if url and '/app/' in url:
                                try:
                                    steam_appid = int(url.split('/app/')[1].split('/')[0])
                                except Exception:
                                    steam_appid = None
                games_list.append({
                    "id": game.get("id"),
                    "name": game.get("name"),
                    "released": game.get("released"),
                    "rating": game.get("rating"),
                    "ratings_count": game.get("ratings_count"),
                    "metacritic": game.get("metacritic"),
                    "genres": ", ".join([genre['name'] for genre in game.get("genres", [])]),
                    "platforms": ", ".join([platform['platform']['name'] for platform in game.get("platforms", [])]),
                    "background_image": game.get("background_image"),
                    "slug": game.get("slug"),
                    "steam_appid": steam_appid
                })
            if not data.get('next'):
                print("[RAWG] No more pages.")
                break
            time.sleep(RAWG_SLEEP)
        except Exception as e:
            print(f"[RAWG] Error on page {page}: {e}")
            time.sleep(5)
    df = pd.DataFrame(games_list)
    print(f"[RAWG] Total games fetched: {len(df)}")
    return df

# --- Fungsi Ambil Harga Steam ---
def fetch_steam_game_price(app_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc=ID&filters=price_overview"
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            data = response.json()
            app_data = data.get(str(app_id), {})
            if app_data.get('success') and 'data' in app_data:
                data_details = app_data['data']
                if isinstance(data_details, dict):
                    price_info = data_details.get('price_overview')
                    if price_info:
                        # Harga dari Steam API dalam sub-unit (sen/cents), dibagi 100 untuk Rupiah asli
                        initial_price = price_info.get("initial", 0) / 100
                        final_price = price_info.get("final", 0) / 100
                        return {
                            "status": "success",
                            "currency": price_info.get("currency", "IDR"),
                            "initial": int(initial_price),
                            "final": int(final_price),
                            "discount_percent": price_info.get("discount_percent", 0)
                        }
                    if data_details.get('is_free'):
                        return {
                            "status": "free",
                            "currency": "IDR",
                            "initial": 0,
                            "final": 0,
                            "discount_percent": 0
                        }
                elif isinstance(data_details, list):
                    # Game gratis seringkali mengembalikan data berupa list kosong [] ketika difilter price_overview
                    return {
                        "status": "free",
                        "currency": "IDR",
                        "initial": 0,
                        "final": 0,
                        "discount_percent": 0
                    }
                return {"status": "no_price"}
            else:
                return {"status": "not_found"}
        elif response.status_code in [403, 429]:
            print(f"[STEAM] Rate limited/Blocked (Status {response.status_code})! Sleeping 60s...")
            time.sleep(60)
            return fetch_steam_game_price(app_id)
    except Exception as e:
        print(f"[STEAM] Error fetching price for appid {app_id}: {e}")
    return {"status": "error"}


# --- Fungsi Pendukung Pencocokan Steam AppID ---
def get_steam_appid_from_rawg(game_id, api_key):
    url = f"https://api.rawg.io/api/games/{game_id}/stores?key={api_key}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            results = response.json().get('results', [])
            for store in results:
                if store.get('store_id') == 1: # Store ID 1 adalah Steam
                    store_url = store.get('url')
                    if store_url and '/app/' in store_url:
                        try:
                            appid = int(store_url.split('/app/')[1].split('/')[0])
                            return appid
                        except Exception:
                            pass
        elif response.status_code == 429:
            print("[RAWG] Rate limited! Sleeping 10s...")
            time.sleep(10)
            return get_steam_appid_from_rawg(game_id, api_key)
    except Exception as e:
        print(f"[RAWG] Error fetching stores for game {game_id}: {e}")
    return None

def clean_suffix(name):
    # Membersihkan sufiks umum game
    name = re.sub(r' - complete edition| complete edition| - goty| goty| - game of the year edition| game of the year edition', '', name)
    name = re.sub(r' - definitive edition| definitive edition| - gold edition| gold edition| - enhanced edition| enhanced edition', '', name)
    return name.strip()

def match_steam_appid(game_name, steam_apps_exact, steam_apps_cleaned):
    if not game_name or not steam_apps_exact:
        return None
    name_lower = str(game_name).lower()
    
    # 1. Pencocokan persis (exact match)
    if name_lower in steam_apps_exact:
        return steam_apps_exact[name_lower]
        
    # 2. Pencocokan tanpa spasi & tanda baca (alphanumeric only)
    cleaned = ''.join(c for c in name_lower if c.isalnum())
    if cleaned in steam_apps_cleaned:
        return steam_apps_cleaned[cleaned]
        
    # 3. Pencocokan dengan pembersihan sufiks
    suff_cleaned = ''.join(c for c in clean_suffix(name_lower) if c.isalnum())
    if suff_cleaned in steam_apps_cleaned:
        return steam_apps_cleaned[suff_cleaned]
        
    return None


# --- Main Proses Gabungan ---

def main():
    # 1. Fetch data RAWG
    if os.path.exists(PROGRESS_PATH):
        print("[INFO] Melanjutkan dari progress terakhir...")
        df = pd.read_csv(PROGRESS_PATH)
    else:
        df = fetch_rawg_games(RAWG_API_KEY, total_games=RAWG_TOTAL_GAMES, page_size=RAWG_PAGE_SIZE)
        df.to_csv(PROGRESS_PATH, index=False)

    # Inisialisasi kolom jika belum ada
    if 'steam_appid' not in df.columns:
        df['steam_appid'] = None
    if 'price_idr' not in df.columns:
        df['price_idr'] = None
    if 'original_price_idr' not in df.columns:
        df['original_price_idr'] = None
    if 'discount_percent' not in df.columns:
        df['discount_percent'] = None
    if 'price_fetched' not in df.columns:
        df['price_fetched'] = False

    # Secara otomatis tandai game non-PC sebagai terproses (fetched = True) agar tidak membuang request API
    non_pc_mask = ~df['platforms'].astype(str).str.lower().str.contains('pc', na=False)
    df.loc[non_pc_mask, 'price_fetched'] = True
    print(f"[INFO] Otomatis melewati {non_pc_mask.sum()} game non-PC dari pencarian harga Steam.")

    # Unduh list game Steam untuk pencocokan nama berkecepatan tinggi
    print("[STEAM] Mengunduh database game Steam untuk pencocokan nama...")
    steam_apps_exact = {}
    steam_apps_cleaned = {}
    last_appid = 0
    steam_api_key = os.getenv('STEAM_API_KEY')
    if steam_api_key:
        while True:
            url = f"https://api.steampowered.com/IStoreService/GetAppList/v1/?key={steam_api_key}&max_results=50000&last_appid={last_appid}"
            try:
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    data = r.json().get('response', {})
                    batch = data.get('apps', [])
                    if not batch:
                        break
                    for app in batch:
                        name_lower = app['name'].lower()
                        steam_apps_exact[name_lower] = app['appid']
                        
                        cleaned = ''.join(c for c in name_lower if c.isalnum())
                        steam_apps_cleaned[cleaned] = app['appid']
                    if not data.get('have_more_results'):
                        break
                    last_appid = data.get('last_appid')
                else:
                    break
            except Exception as e:
                print(f"[STEAM] Error fetching Steam app list: {e}")
                break
        print(f"[STEAM] Berhasil memuat {len(steam_apps_exact)} game dari Steam")
    else:
        print("[STEAM] WARNING: STEAM_API_KEY tidak ditemukan di .env! Pencocokan nama dilewati.")

    # Lakukan pencocokan nama offline awal untuk mengisi steam_appid yang kosong
    # Ini sangat cepat (hanya butuh waktu < 2 detik untuk mencocokkan ribuan game)
    missing_appid_mask = df['steam_appid'].isna() & (df['price_fetched'] == False)
    if missing_appid_mask.sum() > 0 and steam_apps_exact:
        print(f"[INFO] Mencocokkan nama game PC dengan database Steam (total {missing_appid_mask.sum()} game belum memiliki steam_appid)...")
        matched_count = 0
        for idx, row in df[missing_appid_mask].iterrows():
            appid = match_steam_appid(row['name'], steam_apps_exact, steam_apps_cleaned)
            if appid:
                df.at[idx, 'steam_appid'] = appid
                matched_count += 1
        print(f"[INFO] Berhasil mencocokkan {matched_count} game secara offline menggunakan nama game!")
        df.to_csv(PROGRESS_PATH, index=False)

    # 2. Ambil harga Steam berdasarkan steam_appid
    prices_final = df['price_idr'].tolist()
    prices_initial = df['original_price_idr'].tolist()
    discount_percents = df['discount_percent'].tolist()
    steam_appids = df['steam_appid'].tolist()
    price_fetched = df['price_fetched'].tolist()

    unfetched_count = len(df) - sum(price_fetched)
    print(f"[STEAM] Mulai mengambil harga untuk {unfetched_count} game PC yang tersisa...")

    try:
        for idx, row in df.iterrows():
            if price_fetched[idx]:
                continue

            appid = steam_appids[idx]
            
            # Jika appid masih kosong, tetapi platformnya adalah PC, coba panggil RAWG stores API secara on-the-fly
            if pd.isna(appid):
                platforms = str(row.get('platforms', '')).lower()
                if 'pc' in platforms:
                    game_id = row.get('id')
                    print(f"[RAWG] Fetching stores for unmatched PC game: {row['name']} (ID: {game_id})...")
                    appid = get_steam_appid_from_rawg(game_id, RAWG_API_KEY)
                    if appid:
                        steam_appids[idx] = appid
                        df.at[idx, 'steam_appid'] = appid
                    time.sleep(RAWG_SLEEP)

            if pd.notna(appid):
                price_res = fetch_steam_game_price(int(appid))
                status = price_res.get("status", "error")
                
                if status in ["success", "free"]:
                    prices_final[idx] = price_res['final']
                    prices_initial[idx] = price_res['initial']
                    discount_percents[idx] = price_res['discount_percent']
                    price_fetched[idx] = True
                    print(f"[STEAM] Berhasil: {row['name']} -> Rp {price_res['final']}")
                elif status in ["no_price", "not_found"]:
                    prices_final[idx] = None
                    prices_initial[idx] = None
                    discount_percents[idx] = None
                    price_fetched[idx] = True
                    print(f"[STEAM] Tidak dijual/tidak ada harga: {row['name']}")
                else:
                    # Status "error" (rate limit / network error), jangan tandai fetched=True agar bisa diulang nanti
                    print(f"[STEAM] Error/Limit pada: {row['name']}. Dilewati untuk dicoba lagi nanti.")
                    time.sleep(5)
            else:
                # Memang tidak punya steam_appid setelah pencocokan offline & online
                prices_final[idx] = None
                prices_initial[idx] = None
                discount_percents[idx] = None
                price_fetched[idx] = True
                print(f"[STEAM] Dilewati (Tidak ada AppID): {row['name']}")
                
            # Progress info & simpan berkala
            if idx % 50 == 0:
                print(f"[STEAM] Processed {idx}/{len(df)} games")
                df['price_idr'] = prices_final
                df['original_price_idr'] = prices_initial
                df['discount_percent'] = discount_percents
                df['steam_appid'] = steam_appids
                df['price_fetched'] = price_fetched
                df.to_csv(PROGRESS_PATH, index=False)
            time.sleep(STEAM_SLEEP)
            
    except KeyboardInterrupt:
        print("[INFO] Proses dihentikan oleh user. Menyimpan progress terakhir...")
    finally:
        df['price_idr'] = prices_final
        df['original_price_idr'] = prices_initial
        df['discount_percent'] = discount_percents
        df['steam_appid'] = steam_appids
        df['price_fetched'] = price_fetched
        
        # Simpan progress sementara
        df.to_csv(PROGRESS_PATH, index=False)
        
        # Simpan hasil akhir
        df.to_csv(OUTPUT_PATH, index=False)
        print(f"[DONE] Data disimpan di {OUTPUT_PATH}")


if __name__ == "__main__":
    main()



if __name__ == "__main__":
    main()