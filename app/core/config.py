import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "CineMatch-V2"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey_for_cinematch")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TMDB_API_KEY: str = os.getenv("TMDB_API_KEY", "s296a050c356699a086aedbbd54308c2f")

settings = Settings()
