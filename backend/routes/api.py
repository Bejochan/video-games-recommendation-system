from flask import Blueprint, request, jsonify

api_bp = Blueprint('api', __name__)

# Dummy endpoint untuk test kuisioner POST
@api_bp.route('/quiz', methods=['POST'])
def quiz():
    data = request.json
    # Contoh: terima jawaban kuisioner user
    # TODO: proses data kuisioner dan simpan/olah
    return jsonify({"message": "Kuisioner diterima", "data": data})

# Dummy endpoint rekomendasi GET
@api_bp.route('/recommendations', methods=['GET'])
def recommendations():
    # TODO: implementasi logika rekomendasi berdasarkan kuisioner
    dummy_recommendations = [
        {"game_id": 1, "title": "Game A", "score": 0.85},
        {"game_id": 2, "title": "Game B", "score": 0.78},
    ]
    return jsonify(dummy_recommendations)

# Dummy endpoint pencarian GET dengan filter
@api_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    genre = request.args.get('genre', '')
    # TODO: implementasi pencarian game berdasarkan query dan filter genre
    dummy_results = [
        {"game_id": 3, "title": "Game C", "genre": "Action"},
        {"game_id": 4, "title": "Game D", "genre": "RPG"},
    ]
    return jsonify(dummy_results)