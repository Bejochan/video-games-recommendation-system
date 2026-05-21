from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import pickle
import httpx
import asyncio

# Inisialisasi Aplikasi FastAPI
app = FastAPI(title="Marketplace Game RecSys API")

# --- KONFIGURASI API RAWG ---
# Ganti dengan API Key yang baru saja kamu dapatkan dari rawg.io
RAWG_API_KEY = "7c6c538900bd48ccaff25b2006ae8aab"

# --- MENGATUR CORS ---
# Ini WAJIB agar Frontend (HTML biasa) diizinkan mengambil data dari Backend ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Mengizinkan akses dari mana saja (localhost)
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- LOAD MODEL & DATA ---
print("Memuat model XGBoost dan Katalog Game...")
with open("models/xgboost_recsys.pkl", "rb") as f:
    xgb_model = pickle.load(f)

df_katalog = pd.read_pickle("models/game_features.pkl")
# Ekstrak daftar genre untuk dikirim ke frontend
genre_cols = [col for col in df_katalog.columns if col.startswith('genre_') and col != 'genre_Unknown']
available_genres = [col.replace('genre_', '') for col in genre_cols]

# --- SCHEMA INPUT FRONTEND ---
class UserProfile(BaseModel):
    genres: list[str] = []
    
# --- HELPER FUNCTION: AMBIL GAMBAR DARI RAWG ---
async def get_game_cover(title: str):
    async with httpx.AsyncClient() as client:
        try:
            # Mencari game berdasarkan judul
            url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={title}&page_size=1"
            response = await client.get(url)
            data = response.json()
            
            # Jika ketemu, ambil 'background_image'
            if "results" in data and len(data["results"]) > 0:
                return data["results"][0].get("background_image")
            return None
        except Exception as e:
            return None

# --- ENDPOINT 1: AMBIL DAFTAR GENRE ---
@app.get("/api/genres")
def get_genres():
    return {"genres": available_genres}

# --- ENDPOINT 2: PROSES REKOMENDASI ---
@app.post("/api/recommend")
async def get_recommendations(profile: UserProfile):
    df_filtered = df_katalog.copy()
    
    # 1. Logika Filtering Cold Start
    if profile.genres:
        kondisi_genre = np.zeros(len(df_filtered), dtype=bool)
        for genre in profile.genres:
            col_name = f'genre_{genre}'
            if col_name in df_filtered.columns:
                kondisi_genre = kondisi_genre | (df_filtered[col_name] == 1)
        
        # Terapkan filter, jika kosong kembali ke semua data
        if kondisi_genre.any():
            df_filtered = df_filtered[kondisi_genre]
            
    # 2. Persiapan Data Inference
    X_infer = df_filtered.drop(columns=['clean_title', 'title'])
    
    # 3. Prediksi dengan XGBoost
    probs = xgb_model.predict_proba(X_infer)[:, 1]
    df_filtered['match_score'] = probs * 100
    
    # Ambil Top 10 tertinggi
    top_10 = df_filtered.sort_values(by='match_score', ascending=False).head(10)
    
    # 4. Ambil Poster dari RAWG secara pararel (Asynchronous) agar super cepat
    results = []
    tasks = [get_game_cover(row['title']) for _, row in top_10.iterrows()]
    covers = await asyncio.gather(*tasks)
    
    # Placeholder gambar kalau RAWG tidak menemukan gamenya
    fallback_image = "https://images.unsplash.com/photo-1552820728-8b83bb6b773f?w=400&q=80"
    
    for idx, (index, row) in enumerate(top_10.iterrows()):
        results.append({
            "title": row['title'],
            "match_score": int(row['match_score']),
            "image_url": covers[idx] if covers[idx] else fallback_image
        })
        
    return {"recommendations": results}