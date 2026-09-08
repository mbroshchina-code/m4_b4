"""Модуль конфигурации приложения дипломного проекта."""

from __future__ import annotations
from functools import lru_cache
import os
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

os.environ["NO_PROXY"] = "localhost,127.0.0.1,redis"


class LLMSettings(BaseSettings):
    # Исторически проект использует переменные с одним подчёркиванием:
    # LLM_BASE_URL, LLM_OPENAI_PROXY_URL и т. п. LLMSettings читает .env
    # самостоятельно, поэтому этот контракт продолжает работать.
    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: SecretStr = SecretStr("sk-test-placeholder")
    default_model: str = "gpt-4o-mini"
    request_timeout: float = 30.0
    max_retries: int = 3
    openai_proxy_url: str | None = None
    base_url: str = "https://api.openai.com/v1"
    use_litellm_proxy: bool = False
    litellm_proxy_url: str = "http://localhost:4000/v1"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app_name: str = "BAG_ASSISTANT"
    debug: bool = False
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 3600
    chat_storage_dir: Path = Field(default_factory=lambda: Path("./var/chats"))
    chat_token_budget: int = 8000

    llm: LLMSettings = Field(default_factory=LLMSettings)

    admin_token: SecretStr = SecretStr("")
    moderation_openai_enabled: bool = False
    moderation_keywords_path: Path = Field(
        default_factory=lambda: Path("app/moderation/moderation_keywords.yaml")
    )
    broadcast_poll_interval_seconds: float = 10.0

    # --- новые поля для notify ---
    bot_url: str = "http://localhost:9000"
    internal_token: SecretStr
    bot_api_port: int = 9000


@lru_cache
def get_settings() -> Settings:
    return Settings()
