"""
LLM Factory - Creates LLM instances based on configuration.
Supports: DeepSeek, OpenAI, Anthropic (Claude)
"""
import os
from typing import Optional
from langchain_core.language_models import BaseLLM
from langchain_core.language_models.chat_models import BaseChatModel
from backend.config import settings


class LLMFactory:
    """
    Factory for creating LLM instances based on the LLM_PROVIDER setting.
    Supports multiple providers through a unified interface.
    """

    # Cache the LLM instance
    _instance: Optional[BaseChatModel] = None

    @classmethod
    def get_llm(cls, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> BaseChatModel:
        """
        Get or create an LLM instance based on configuration.

        Args:
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            A LangChain-compatible chat model instance
        """
        temp = temperature if temperature is not None else settings.AI_TEMPERATURE
        tokens = max_tokens if max_tokens is not None else settings.AI_MAX_TOKENS

        provider = settings.LLM_PROVIDER.lower()

        if provider == "deepseek":
            return cls._create_deepseek(temp, tokens)
        elif provider == "openai":
            return cls._create_openai(temp, tokens)
        elif provider == "anthropic":
            return cls._create_anthropic(temp, tokens)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    @classmethod
    def _create_deepseek(cls, temperature: float, max_tokens: int) -> BaseChatModel:
        """Create a DeepSeek chat model."""
        from langchain_openai import ChatOpenAI

        if not settings.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY is not configured")

        return ChatOpenAI(
            model=settings.DEEPSEEK_MODEL,
            openai_api_key=settings.DEEPSEEK_API_KEY,
            openai_api_base=settings.DEEPSEEK_BASE_URL,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=settings.AI_TOP_P,
        )

    @classmethod
    def _create_openai(cls, temperature: float, max_tokens: int) -> BaseChatModel:
        """Create an OpenAI chat model."""
        from langchain_openai import ChatOpenAI

        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")

        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=settings.AI_TOP_P,
        )

    @classmethod
    def _create_anthropic(cls, temperature: float, max_tokens: int) -> BaseChatModel:
        """Create an Anthropic (Claude) chat model."""
        from langchain_anthropic import ChatAnthropic

        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not configured")

        return ChatAnthropic(
            model=settings.ANTHROPIC_MODEL,
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=settings.AI_TOP_P,
        )

    @classmethod
    def is_configured(cls) -> bool:
        """Check if the configured LLM provider has an API key set."""
        provider = settings.LLM_PROVIDER.lower()
        if provider == "deepseek":
            return bool(settings.DEEPSEEK_API_KEY)
        elif provider == "openai":
            return bool(settings.OPENAI_API_KEY)
        elif provider == "anthropic":
            return bool(settings.ANTHROPIC_API_KEY)
        return False