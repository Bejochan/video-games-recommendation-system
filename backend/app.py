from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Load konfigurasi dari .env
RAWG_API_KEY = os.getenv('RAWG_API_KEY')
STEAM_API_KEY = os.getenv('STEAM_API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')

GENRE_WEIGHT = float(os.getenv('GENRE_WEIGHT', 0.4))
PLAYSTYLE_WEIGHT = float(os.getenv('PLAYSTYLE_WEIGHT', 0.4))
RATING_WEIGHT = float(os.getenv('RATING_WEIGHT', 0.2))

# Load data game dari CSV
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'games.csv')
games_df = pd.read_csv(DATA_PATH)

# Simpan jawaban kuisioner user sementara di memori (bisa diganti DB)
user_quiz_data = {}

# Fungsi hitung Playstyle DNA (dummy contoh)
def calculate_playstyle_dna(quiz_answers):
    # quiz_answers: dict pertanyaan dan jawaban (skala 1-5)
    # Contoh sederhana: hitung rata-rata skor untuk dimensi tertentu
    dna = {
        "casual": quiz_answers.get("casual", 3) / 5,
        "hardcore": quiz_answers.get("hardcore", 3) / 5,
        "calming": quiz_answers.get("calming", 3) / 5,
        "adrenaline": quiz_answers.get("adrenaline", 3) / 5,
    }
    return dna

# Fungsi hitung skor kecocokan hybrid
def calculate_match_score(game, user_preferences, playstyle_dna):
    # Genre matching (sederhana: cek genre ada di preferensi)
    genre_score = 1.0 if any(g.strip().lower() in user_preferences.get('genres', '').lower() for g in game['genres'].split(',')) else 0.0

    # Playstyle DNA matching (dummy: rata-rata bobot playstyle)
    playstyle_score = sum(playstyle_dna.values()) / len(playstyle_dna)

    # Rating normalisasi (asumsi rating max 5)
    rating_score = game['rating'] / 5 if not pd.isna(game['rating']) else 0.5

    # Hitung weighted score
    total_score = (GENRE_WEIGHT * genre_score) + (PLAYSTYLE_WEIGHT * playstyle_score) + (RATING_WEIGHT * rating_score)
    return total_score

@app.route('/')
def home():
    return "Backend Flask is running!"

@app.route('/api/quiz', methods=['POST'])
def quiz():
    data = request.json
    user_id = data.get('user_id', 'default_user')
    answers = data.get('answers', {})
    user_quiz_data[user_id] = answers
    return jsonify({"message": "Kuisioner diterima", "user_id": user_id})

@app.route('/api/recommendations', methods=['GET'])
def recommendations():
    user_id = request.args.get('user_id', 'default_user')
    user_answers = user_quiz_data.get(user_id)
    if not user_answers:
        return jsonify({"error": "User quiz data not found"}), 400

    playstyle_dna = calculate_playstyle_dna(user_answers)
    user_genres = user_answers.get('genres', '')

    # Hitung skor kecocokan untuk tiap game
    games_df['match_score'] = games_df.apply(lambda row: calculate_match_score(row, {'genres': user_genres}, playstyle_dna), axis=1)

    # Ambil 10 game dengan skor tertinggi
    top_games = games_df.sort_values(by='match_score', ascending=False).head(10)

    # Format hasil
    results = []
    for _, row in top_games.iterrows():
        results.append({
            "id": row['id'],
            "title": row['name'],
            "genres": row['genres'],
            "rating": row['rating'],
            "cover_url": row['background_image'],
            "match_score": round(row['match_score'], 3)
        })

    return jsonify(results)

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    genre_filter = request.args.get('genre', '').lower()

    filtered = games_df

    if query:
        filtered = filtered[filtered['name'].str.lower().str.contains(query)]

    if genre_filter:
        filtered = filtered[filtered['genres'].str.lower().str.contains(genre_filter)]

    # Batasi hasil pencarian maksimal 20 game
    filtered = filtered.head(20)

    results = []
    for _, row in filtered.iterrows():
        results.append({
            "id": row['id'],
            "title": row['name'],
            "genres": row['genres'],
            "rating": row['rating'],
            "cover_url": row['background_image']
        })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)