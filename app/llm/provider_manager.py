"""
Multi-LLM Provider Manager with failover support.
"""

import logging
from typing import Optional, Literal, Any
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, AIMessage

from app.config import settings

logger = logging.getLogger(__name__)

ProviderType = Literal["anthropic", "openai", "gemini"]


class LLMProviderManager:
    def __init__(self):
        self.providers: dict[str, Any] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        if settings.anthropic_api_key:
            try:
                config = settings.get_llm_config("anthropic")
                self.providers["anthropic"] = ChatAnthropic(
                    api_key=config["api_key"],
                    model=config["model"],
                    temperature=0.1,
                    max_tokens=4096
                )
                logger.info(f"Initialized Anthropic provider: {config['model']}")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic: {e}")

        if settings.openai_api_key:
            try:
                config = settings.get_llm_config("openai")
                self.providers["openai"] = ChatOpenAI(
                    api_key=config["api_key"],
                    model=config["model"],
                    temperature=0.1,
                    max_tokens=4096
                )
                logger.info(f"Initialized OpenAI provider: {config['model']}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")

        if settings.gemini_api_key:
            try:
                config = settings.get_llm_config("gemini")
                self.providers["gemini"] = ChatGoogleGenerativeAI(
                    google_api_key=config["api_key"],
                    model=config["model"],
                    temperature=0.1,
                    max_output_tokens=4096
                )
                logger.info(f"Initialized Gemini provider: {config['model']}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")

    def invoke_with_fallback(
        self,
        messages: list[BaseMessage],
        preferred_provider: Optional[ProviderType] = None
    ) -> tuple[AIMessage, ProviderType, dict]:
        if preferred_provider:
            providers = [preferred_provider]
        else:
            providers = [settings.primary_llm_provider]

        if settings.fallback_1_provider not in providers:
            providers.append(settings.fallback_1_provider)
        if settings.fallback_2_provider not in providers:
            providers.append(settings.fallback_2_provider)

        last_error = None
        for provider in providers:
            if provider not in self.providers:
                continue
            try:
                logger.info(f"Trying provider: {provider}")
                llm = self.providers[provider]
                response = llm.invoke(messages)

                metadata = {
                    "provider": provider,
                    "model": getattr(llm, "model", "unknown"),
                    "success": True
                }
                if hasattr(response, "response_metadata"):
                    metadata.update(response.response_metadata)

                logger.info(f"Success with provider: {provider}")
                return response, provider, metadata
            except Exception as e:
                logger.error(f"Provider '{provider}' failed: {str(e)}")
                last_error = e

        raise RuntimeError(f"All LLM providers failed. Last error: {str(last_error)}")


llm_manager = LLMProviderManager()
