"""
Configuration for Railway IA Testadora e Editora.
Simplified version without Supabase/Redis dependencies.
"""

import os
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # LLM Configuration
    anthropic_api_key: str = Field(default="")
    openai_api_key: str = Field(default="")
    gemini_api_key: str = Field(default="")

    # Test LLM Keys (for chatbot simulation)
    deepseek_api_key: str = Field(default="")
    openai_test_api_key: str = Field(default="")  # GPT-4.1 key (may differ from editor key)

    primary_llm_provider: Literal["anthropic", "openai", "gemini"] = "anthropic"
    primary_llm_model: str = "claude-sonnet-4-5-20250929"

    fallback_1_provider: Literal["anthropic", "openai", "gemini"] = "openai"
    fallback_1_model: str = "gpt-4-turbo-preview"
    fallback_2_provider: Literal["anthropic", "openai", "gemini"] = "gemini"
    fallback_2_model: str = "gemini-1.5-pro"

    # App Configuration
    app_password: str = "Vidabela@t3a"
    secret_key: str = Field(default="t3a-railway-secret-key-change-me")
    port: int = 8000

    # Database
    database_url: str = Field(default="sqlite:///data/app.db")

    # Logging
    log_level: str = "INFO"

    def get_llm_config(self, provider: str) -> dict:
        configs = {
            "anthropic": {
                "api_key": self.anthropic_api_key,
                "model": self.primary_llm_model if provider == self.primary_llm_provider else "claude-sonnet-4-5-20250929"
            },
            "openai": {
                "api_key": self.openai_api_key,
                "model": self.fallback_1_model if provider == self.fallback_1_provider else "gpt-4-turbo-preview"
            },
            "gemini": {
                "api_key": self.gemini_api_key,
                "model": self.fallback_2_model if provider == self.fallback_2_provider else "gemini-1.5-pro"
            }
        }
        return configs.get(provider, {})


settings = Settings()
