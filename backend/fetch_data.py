import requests
import pandas as pd
import time
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env untuk ambil API key

RAWG_API_KEY = os.getenv('RAWG_API_KEY')

def fetch_rawg_games(api_key, total_games=10000, page_size=40):
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
        print(f"Fetching page {page}...")
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}: {response.status_code}")
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

        # Jika tidak ada next page, hentikan loop
        if not data.get('next'):
            print("No more pages.")
            break

        # Sleep sebentar supaya tidak kena rate limit
        time.sleep(1)

    df = pd.DataFrame(games_list)
    df.to_csv("data/games.csv", index=False)
    print(f"Saved {len(games_list)} games to backend/data/games.csv")

if __name__ == "__main__":
    fetch_rawg_games(RAWG_API_KEY)