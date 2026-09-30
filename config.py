import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    app_name = "PocketSmart AI"
    secret_key = os.getenv("SECRET_KEY", "dev-only-change-me")
    database_path = os.getenv("DATABASE_PATH", "pocketsmart.db")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
    use_mock_ai = os.getenv("USE_MOCK_AI", "true").lower() in {"1", "true", "yes"}

settings = Settings()
