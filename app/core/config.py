from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_name: str = "Smart Document Q&A"
    env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "postgresql+psycopg2://postgres:postgres@postgres:5432/docqa"
    redis_url: str = "redis://redis:6379/0"
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    faiss_index_path: str = "/data/faiss_index"
    bm25_index_path: str = "/data/bm25"
    upload_dir: str = "/data/uploads"
    max_upload_mb: int = 25
    top_k: int = 6
    chunk_size: int = 1000
    chunk_overlap: int = 150

@lru_cache
def get_settings() -> Settings:
    return Settings()
