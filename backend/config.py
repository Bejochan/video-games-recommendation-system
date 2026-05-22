import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

class Config:
    RAWG_API_KEY = os.getenv('RAWG_API_KEY')
    STEAM_API_KEY = os.getenv('STEAM_API_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')

    # Bobot default untuk weighted scoring
    GENRE_WEIGHT = float(os.getenv('GENRE_WEIGHT', 0.4))
    PLAYSTYLE_WEIGHT = float(os.getenv('PLAYSTYLE_WEIGHT', 0.4))
    RATING_WEIGHT = float(os.getenv('RATING_WEIGHT', 0.2))