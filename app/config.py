from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Qwen via DashScope (OpenAI-compatible endpoint)
    qwen_base_url: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    qwen_api_key: str = ""
    qwen_model: str = "qwen-plus"

    # PostgreSQL + pgvector
    database_url: str = "postgresql://tutor:tutor@localhost:15432/algo_tutor"

    # Embeddings
    embedding_model: str = "BAAI/bge-m3"
    embedding_dim: int = 1024

    # Sandbox limits
    sandbox_timeout_seconds: float = 3.0
    sandbox_memory_limit: str = "128m"
    sandbox_cpu_limit: float = 1.0


settings = Settings()
