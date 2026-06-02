from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Load konfigurasi dari .env
RAWG_API_KEY = os.getenv('RAWG_API_KEY')
STEAM_API_KEY = os.getenv('STEAM_API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')

# Path ke data games_with_prices.csv
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'games_with_prices.csv')

# Load dataset utama
if os.path.exists(DATA_PATH):
    games_df = pd.read_csv(DATA_PATH)
    # Bersihkan data null
    games_df['price_idr'] = pd.to_numeric(games_df['price_idr'], errors='coerce').fillna(0.0)
    games_df['original_price_idr'] = pd.to_numeric(games_df['original_price_idr'], errors='coerce').fillna(0.0)
    games_df['discount_percent'] = pd.to_numeric(games_df['discount_percent'], errors='coerce').fillna(0.0)
    games_df['rating'] = pd.to_numeric(games_df['rating'], errors='coerce').fillna(0.0)
    games_df['ratings_count'] = pd.to_numeric(games_df['ratings_count'], errors='coerce').fillna(0)
    games_df['metacritic'] = pd.to_numeric(games_df['metacritic'], errors='coerce').fillna(0.0)
    games_df['genres'] = games_df['genres'].fillna('')
    games_df['platforms'] = games_df['platforms'].fillna('Unknown')
    games_df['background_image'] = games_df['background_image'].fillna('')
    games_df['released'] = games_df['released'].fillna('')
else:
    # Fallback kosong jika file tidak ditemukan
    games_df = pd.DataFrame(columns=[
        'id', 'name', 'released', 'rating', 'ratings_count', 'metacritic',
        'genres', 'platforms', 'background_image', 'slug', 'steam_appid',
        'price_idr', 'original_price_idr', 'discount_percent', 'price_fetched'
    ])

# Pre-calculate Playstyle DNA untuk setiap game berdasarkan Genre, Metacritic, dan Ratings Count
# Dimensi DNA: [casual_vs_hardcore, simple_vs_complex, calming_vs_adrenaline]
def precompute_game_dna(row):
    genres = [g.strip().lower() for g in row['genres'].split(',') if g.strip()]
    
    # 1. Casual vs Hardcore (0.0 = Casual, 1.0 = Hardcore)
    ch_base = 0.5
    hardcore_genres = {'rpg', 'strategy', 'shooter', 'simulation'}
    casual_genres = {'casual', 'puzzle', 'arcade', 'educational', 'card', 'board games'}
    
    for g in genres:
        if g in hardcore_genres:
            ch_base += 0.15
        elif g in casual_genres:
            ch_base -= 0.15
            
    # Tambah skor hardcore berdasarkan popularitas & metacritic
    if row['ratings_count'] > 1000:
        ch_base += 0.05
    if row['metacritic'] > 80:
        ch_base += 0.05
        
    ch = np.clip(ch_base, 0.0, 1.0)
    
    # 2. Simple vs Complex (0.0 = Simple, 1.0 = Complex)
    sc_base = 0.5
    complex_genres = {'strategy', 'rpg', 'simulation', 'massively multiplayer'}
    simple_genres = {'arcade', 'action', 'platformer', 'casual', 'puzzle', 'racing'}
    
    for g in genres:
        if g in complex_genres:
            sc_base += 0.2
        elif g in simple_genres:
            sc_base -= 0.1
            
    sc = np.clip(sc_base, 0.0, 1.0)
    
    # 3. Calming vs Adrenaline (0.0 = Calming, 1.0 = Adrenaline)
    ca_base = 0.5
    adrenaline_genres = {'shooter', 'action', 'fighting', 'racing', 'sports'}
    calming_genres = {'casual', 'puzzle', 'simulation', 'adventure', 'family'}
    
    for g in genres:
        if g in adrenaline_genres:
            ca_base += 0.2
        elif g in calming_genres:
            ca_base -= 0.15
            
    ca = np.clip(ca_base, 0.0, 1.0)
    
    return pd.Series([ch, sc, ca])

# Tambahkan kolom DNA ke games_df
if not games_df.empty:
    games_df[['dna_hardcore', 'dna_complex', 'dna_adrenaline']] = games_df.apply(precompute_game_dna, axis=1)

# In-memory session store untuk data kuesioner user
user_sessions = {}

# Fungsi memodifikasi DNA berdasarkan pilihan Mood
def apply_mood_modifier(dna, mood):
    # dna: dict dengan kunci 'hardcore', 'complex', 'adrenaline'
    # mood: string ('relaxed', 'competitive', 'immersive', 'focused', 'none')
    adjusted = dna.copy()
    
    if mood == 'relaxed':
        # Lebih casual (kurang hardcore), simpel, dan menenangkan (kurang adrenalin)
        adjusted['hardcore'] = max(0.0, adjusted['hardcore'] - 0.25)
        adjusted['complex'] = max(0.0, adjusted['complex'] - 0.2)
        adjusted['adrenaline'] = max(0.0, adjusted['adrenaline'] - 0.3)
    elif mood == 'competitive':
        # Lebih hardcore, adrenalin tinggi, dan kompleks
        adjusted['hardcore'] = min(1.0, adjusted['hardcore'] + 0.3)
        adjusted['complex'] = min(1.0, adjusted['complex'] + 0.15)
        adjusted['adrenaline'] = min(1.0, adjusted['adrenaline'] + 0.3)
    elif mood == 'immersive':
        # Sangat kompleks dan sedikit lebih tenang (fokus ke cerita/eksplorasi mendalam)
        adjusted['hardcore'] = min(1.0, adjusted['hardcore'] + 0.1)
        adjusted['complex'] = min(1.0, adjusted['complex'] + 0.3)
        adjusted['adrenaline'] = max(0.0, adjusted['adrenaline'] - 0.1)
    elif mood == 'focused':
        # Sangat hardcore dan kompleks (fokus memecahkan masalah/strategi)
        adjusted['hardcore'] = min(1.0, adjusted['hardcore'] + 0.2)
        adjusted['complex'] = min(1.0, adjusted['complex'] + 0.35)
        
    return adjusted

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "message": "Backend Sistem Rekomendasi Game VibePlay berjalan sempurna!",
        "total_games": len(games_df)
    })

@app.route('/health')
def health():
    return "OK", 200


# API Endpoint untuk menyimpan jawaban kuisioner dan menghitung DNA
@app.route('/api/quiz', methods=['POST'])
def save_quiz():
    data = request.json
    user_id = data.get('user_id', 'anonymous_user')
    answers = data.get('answers', {}) # Berisi jawaban untuk 10-15 pertanyaan
    
    # Hitung Playstyle DNA dasar dari kuesioner
    # Jawaban berskala 1-5 akan dipetakan ke koordinat [0.0 - 1.0]
    
    # 1. Hardcore vs Casual
    # Pertanyaan: Q1, Q4, Q7
    hc_scores = []
    if 'q1' in answers: hc_scores.append(answers['q1'] / 5.0)  # Would you rather: Casual (1) vs Hardcore (5)
    if 'q4' in answers: hc_scores.append(answers['q4'] / 5.0)  # MCQ
    if 'q7' in answers: hc_scores.append(answers['q7'] / 5.0)  # MCQ
    dna_hardcore = np.mean(hc_scores) if hc_scores else 0.5
    
    # 2. Complex vs Simple
    # Pertanyaan: Q2, Q5, Q8, Q11
    cp_scores = []
    if 'q2' in answers: cp_scores.append(answers['q2'] / 5.0)  # Would you rather: Simple (1) vs Complex (5)
    if 'q5' in answers: cp_scores.append(answers['q5'] / 5.0)  # MCQ
    if 'q8' in answers: cp_scores.append(answers['q8'] / 5.0)  # MCQ
    if 'q11' in answers: cp_scores.append(answers['q11'] / 5.0) # MCQ
    dna_complex = np.mean(cp_scores) if cp_scores else 0.5
    
    # 3. Calming vs Adrenaline
    # Pertanyaan: Q3, Q6, Q9, Q10, Q12
    ad_scores = []
    if 'q3' in answers: ad_scores.append(answers['q3'] / 5.0)  # Would you rather: Calming (1) vs Adrenaline (5)
    if 'q6' in answers: ad_scores.append(answers['q6'] / 5.0)  # MCQ
    if 'q9' in answers: ad_scores.append(answers['q9'] / 5.0)  # MCQ
    if 'q10' in answers: ad_scores.append(answers['q10'] / 5.0) # MCQ
    if 'q12' in answers: ad_scores.append(answers['q12'] / 5.0) # MCQ
    dna_adrenaline = np.mean(ad_scores) if ad_scores else 0.5
    
    # Simpan di session memory
    user_sessions[user_id] = {
        "answers": answers,
        "base_dna": {
            "hardcore": float(dna_hardcore),
            "complex": float(dna_complex),
            "adrenaline": float(dna_adrenaline)
        },
        "preferred_genres": data.get('preferred_genres', []) # List genre yang dipilih
    }
    
    return jsonify({
        "success": True,
        "message": "Kuisioner berhasil dianalisis!",
        "dna": user_sessions[user_id]["base_dna"]
    })

# API Endpoint untuk menghasilkan Rekomendasi
@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    user_id = data.get('user_id', 'anonymous_user')
    mood = data.get('mood', 'none').lower() # 'relaxed', 'competitive', 'immersive', 'focused', 'none'
    max_budget = float(data.get('max_budget', 1000000.0)) # Default budget Rp 1.000.000
    
    # Bobot aspek (dari user slider di frontend)
    # Default seimbang jika tidak diset
    w_genre = float(data.get('weight_genre', 0.3))
    w_dna = float(data.get('weight_dna', 0.3))
    w_rating = float(data.get('weight_rating', 0.2))
    w_price = float(data.get('weight_price', 0.2))
    
    # Normalisasi bobot agar total = 1.0
    total_w = w_genre + w_dna + w_rating + w_price
    if total_w > 0:
        w_genre /= total_w
        w_dna /= total_w
        w_rating /= total_w
        w_price /= total_w
    else:
        w_genre, w_dna, w_rating, w_price = 0.3, 0.3, 0.2, 0.2
        
    user_data = user_sessions.get(user_id)
    if not user_data:
        # Jika tidak ada sesi, gunakan DNA default tengah-tengah
        base_dna = {"hardcore": 0.5, "complex": 0.5, "adrenaline": 0.5}
        pref_genres = []
    else:
        base_dna = user_data["base_dna"]
        pref_genres = [g.lower() for g in user_data["preferred_genres"]]
        
    # Terapkan modifikasi mood pada DNA
    adjusted_dna = apply_mood_modifier(base_dna, mood)
    
    # Lakukan perhitungan skor untuk seluruh game
    recommendations_df = games_df.copy()
    
    # 1. Hitung Genre Match Score
    def get_genre_score(genres_str):
        if not pref_genres:
            return 1.0 # Netral jika user tidak memilih genre spesifik
        game_genres = [g.strip().lower() for g in genres_str.split(',') if g.strip()]
        if not game_genres:
            return 0.0
        # Berapa banyak genre game yang cocok dengan preferensi user
        matches = sum(1 for g in game_genres if g in pref_genres)
        return matches / len(pref_genres)
        
    recommendations_df['score_genre'] = recommendations_df['genres'].apply(get_genre_score)
    
    # 2. Hitung Playstyle DNA Match Score (1 - Jarak Euclidean normalized)
    g_dna = recommendations_df[['dna_hardcore', 'dna_complex', 'dna_adrenaline']].values
    u_dna = np.array([adjusted_dna['hardcore'], adjusted_dna['complex'], adjusted_dna['adrenaline']])
    distances = np.linalg.norm(g_dna - u_dna, axis=1)
    # Jarak maksimum dalam ruang 3D [0,1]^3 adalah sqrt(3) ~= 1.732
    recommendations_df['score_dna'] = 1.0 - (distances / np.sqrt(3))
    
    # 3. Hitung Rating Score (Rating Rawg & Metacritic)
    # Gabungan rating (skala 5) dan metacritic (skala 100)
    meta_norm = recommendations_df['metacritic'] / 100.0
    rawg_norm = recommendations_df['rating'] / 5.0
    # Beri bobot 60% Metacritic dan 40% Rawg Rating (jika metacritic tersedia)
    recommendations_df['score_rating'] = np.where(
        recommendations_df['metacritic'] > 0,
        (meta_norm * 0.6) + (rawg_norm * 0.4),
        rawg_norm
    )
    
    # 4. Hitung Price Score (Budget & Diskon)
    # Jika harga <= budget, nilai sempurna 1.0 + bonus jika ada diskon
    # Jika harga > budget, nilai turun drastis
    def get_price_score(row):
        price = row['price_idr']
        if price == 0:
            # Game gratis
            return 1.0
        if price <= max_budget:
            # Beri bonus kecil bagi game yang sedang diskon besar (value value deal)
            discount_bonus = (row['discount_percent'] / 100.0) * 0.1
            return min(1.0, 0.9 + discount_bonus)
        else:
            # Penalti linier jika melebihi budget, bernilai 0 jika melebihi 2x budget
            penalty = (price - max_budget) / max_budget
            return max(0.0, 1.0 - penalty)
            
    recommendations_df['score_price'] = recommendations_df.apply(get_price_score, axis=1)
    
    # Hitung Skor Akhir Linear (Sesi 1 - Balanced Match)
    recommendations_df['match_score'] = (
        (recommendations_df['score_genre'] * w_genre) +
        (recommendations_df['score_dna'] * w_dna) +
        (recommendations_df['score_rating'] * w_rating) +
        (recommendations_df['score_price'] * w_price)
    )
    
    # Hitung Skor Sesi 2 (High Rating Priority - Menggandakan pengaruh Rating & Metacritic)
    # Diperhitungkan pengaruh tinggi-rendah rating game secara signifikan
    recommendations_df['match_score_high_rating'] = (
        (recommendations_df['score_genre'] * (w_genre * 0.5)) +
        (recommendations_df['score_dna'] * (w_dna * 0.5)) +
        (recommendations_df['score_rating'] * (w_rating + (w_genre * 0.25) + (w_dna * 0.25))) +
        (recommendations_df['score_price'] * w_price)
    )
    
    # Ambil 10 game terbaik untuk Sesi 1
    top_balanced = recommendations_df.sort_values(by='match_score', ascending=False).head(10)
    
    # Ambil 10 game terbaik untuk Sesi 2
    top_high_rating = recommendations_df.sort_values(by='match_score_high_rating', ascending=False).head(10)
    
    # Format Response Helper
    def format_list(df, score_col):
        res = []
        for _, row in df.iterrows():
            # Tentukan kategori kecocokan
            score_val = row[score_col]
            if score_val >= 0.85:
                match_label = "Sangat Tinggi"
                match_class = "match-very-high"
            elif score_val >= 0.70:
                match_label = "Tinggi"
                match_class = "match-high"
            else:
                match_label = "Cukup Tinggi"
                match_class = "match-medium"
                
            res.append({
                "id": int(row['id']),
                "title": row['name'],
                "released": row['released'],
                "genres": row['genres'],
                "platforms": row['platforms'],
                "rating": float(row['rating']),
                "metacritic": int(row['metacritic']),
                "cover_url": row['background_image'],
                "steam_appid": int(row['steam_appid']) if not pd.isna(row['steam_appid']) else None,
                "price_idr": float(row['price_idr']),
                "original_price_idr": float(row['original_price_idr']),
                "discount_percent": float(row['discount_percent']),
                "match_score": round(float(score_val) * 100, 1),
                "match_label": match_label,
                "match_class": match_class,
                "dna": {
                    "hardcore": round(float(row['dna_hardcore']), 2),
                    "complex": round(float(row['dna_complex']), 2),
                    "adrenaline": round(float(row['dna_adrenaline']), 2)
                }
            })
        return res

    return jsonify({
        "user_dna": adjusted_dna,
        "mood_applied": mood,
        "balanced": format_list(top_balanced, 'match_score'),
        "high_rating": format_list(top_high_rating, 'match_score_high_rating')
    })

# API Endpoint untuk Pencarian Manual dengan Filter Toko / Marketplace
@app.route('/api/search', methods=['GET'])
def search_games():
    query = request.args.get('q', '').lower()
    genre_filter = request.args.get('genre', '').lower()
    max_price = request.args.get('max_price')
    min_rating = request.args.get('min_rating')
    
    filtered_df = games_df.copy()
    
    # 1. Filter Nama
    if query:
        filtered_df = filtered_df[filtered_df['name'].str.lower().str.contains(query, na=False)]
        
    # 2. Filter Genre
    if genre_filter:
        filtered_df = filtered_df[filtered_df['genres'].str.lower().str.contains(genre_filter, na=False)]
        
    # 3. Filter Harga Maksimal (Marketplace Budget Slider)
    if max_price:
        try:
            max_p = float(max_price)
            # Jika budget diset 0, anggap mencari game gratis
            if max_p == 0:
                filtered_df = filtered_df[filtered_df['price_idr'] == 0]
            else:
                filtered_df = filtered_df[filtered_df['price_idr'] <= max_p]
        except ValueError:
            pass
            
    # 4. Filter Rating Minimal
    if min_rating:
        try:
            min_r = float(min_rating)
            filtered_df = filtered_df[filtered_df['rating'] >= min_r]
        except ValueError:
            pass
            
    # Batasi hasil pencarian maksimal 24 game untuk grid toko
    top_search = filtered_df.head(24)
    
    results = []
    for _, row in top_search.iterrows():
        results.append({
            "id": int(row['id']),
            "title": row['name'],
            "released": row['released'],
            "genres": row['genres'],
            "platforms": row['platforms'],
            "rating": float(row['rating']),
            "metacritic": int(row['metacritic']),
            "cover_url": row['background_image'],
            "steam_appid": int(row['steam_appid']) if not pd.isna(row['steam_appid']) else None,
            "price_idr": float(row['price_idr']),
            "original_price_idr": float(row['original_price_idr']),
            "discount_percent": float(row['discount_percent']),
            "dna": {
                "hardcore": round(float(row['dna_hardcore']), 2),
                "complex": round(float(row['dna_complex']), 2),
                "adrenaline": round(float(row['dna_adrenaline']), 2)
            }
        })
        
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)