import requests
import pandas as pd
import time
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env untuk ambil API key

RAWG_API_KEY = os.getenv('RAWG_API_KEY')
STEAM_API_KEY = os.getenv('STEAM_API_KEY')  # Jika diperlukan, tapi Steam API harga biasanya tanpa key

RAWG_DATA_PATH = "data/games.csv"
OUTPUT_PATH = "data/games_with_prices.csv"

def fetch_rawg_games(api_key, total_games=100000, page_size=100):
    base_url = "https://api.rawg.io/api/games"
    games_list = []
    pages = total_games // page_size + 1

    for page in range(1, pages + 1):
        params = {
            "key": api_key,
            "page_size": page_size,
            "page": page,
            "ordering": "-rating"  # Urutkan berdasarkan rating tertinggi
        }
        print(f"Fetching RAWG page {page}...")
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch RAWG page {page}: {response.status_code}")
            break

        data = response.json()
        results = data.get('results', [])
        for game in results:
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
                "slug": game.get("slug")
            })

        if not data.get('next'):
            print("No more RAWG pages.")
            break

        time.sleep(1)  # Hindari rate limit

    df = pd.DataFrame(games_list)
    df.to_csv(RAWG_DATA_PATH, index=False)
    print(f"Saved {len(games_list)} games to {RAWG_DATA_PATH}")
    return df

def fetch_steam_app_list():
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MyApp/1.0; +https://yourdomain.com)"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        apps = data.get('applist', {}).get('apps', [])
        if apps:
            return pd.DataFrame(apps)
        else:
            print("Steam app list is empty.")
            return pd.DataFrame()
    else:
        print(f"Failed to fetch Steam app list: {response.status_code}")
        return pd.DataFrame()

def fetch_steam_game_price(app_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc=ID"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if str(app_id) in data and data[str(app_id)]['success']:
                price_info = data[str(app_id)]['data'].get('price_overview', {})
                if price_info:
                    # Harga dalam cent, konversi ke rupiah
                    return price_info.get('final', None)
    except Exception as e:
        print(f"Error fetching price for appid {app_id}: {e}")
    return None

def merge_rawg_and_steam(rawg_df, steam_apps_df):
    if steam_apps_df.empty or 'name' not in steam_apps_df.columns:
        print("Steam app list is empty or missing 'name' column. Skipping merge.")
        rawg_df['price'] = None
        return rawg_df

    steam_apps_df['name_lower'] = steam_apps_df['name'].str.lower()
    rawg_df['name_lower'] = rawg_df['name'].str.lower()

    merged = pd.merge(rawg_df, steam_apps_df, left_on='name_lower', right_on='name_lower', how='left')

    # Ambil harga dari Steam API untuk setiap appid yang ada
    prices = []
    total = len(merged)
    for idx, row in merged.iterrows():
        appid = row.get('appid')
        if pd.notna(appid):
            price = fetch_steam_game_price(int(appid))
            prices.append(price)
        else:
            prices.append(None)
        if idx % 50 == 0:
            print(f"Processed {idx}/{total} games for price")
        time.sleep(0.5)  # Hindari rate limit

    merged['price'] = prices
    merged.drop(columns=['name_lower'], inplace=True)
    return merged

if __name__ == "__main__":
    # 1. Tarik data RAWG
    rawg_df = fetch_rawg_games(RAWG_API_KEY, total_games=10000, page_size=40)

    # 2. Tarik daftar game Steam
    steam_apps_df = fetch_steam_app_list()

    # 3. Gabungkan dan ambil harga
    merged_df = merge_rawg_and_steam(rawg_df, steam_apps_df)

    # 4. Simpan hasil gabungan
    merged_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved merged data with prices to {OUTPUT_PATH}")