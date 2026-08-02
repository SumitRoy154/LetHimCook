import logging

from app.agents.providers.anthropic_provider import AnthropicProvider
from app.agents.providers.base_provider import LLMProvider
from app.agents.providers.google_provider import GoogleProvider
from app.agents.providers.groq_provider import GroqProvider
from app.agents.providers.mock_provider import MockProvider
from app.agents.providers.openai_provider import OpenAIProvider
from app.core.config import get_settings
from app.exceptions.agent import ProviderException

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Factory Pattern resolving real LLMProvider strategy instances for AI roles."""

    @staticmethod
    def get_provider_for_role(role_name: str, mock: bool = False) -> LLMProvider:
        if mock:
            logger.info("ProviderFactory resolving MockProvider for role '%s'", role_name)
            return MockProvider()

        settings = get_settings()
        role = role_name.lower().strip()

        if role == "planner":
            provider_name = settings.planner_provider.lower().strip()
            if provider_name == "groq":
                if not settings.groq_api_key:
                    logger.warning("GROQ_API_KEY is empty. Falling back to MockProvider for Planner role.")
                    return MockProvider()
                return GroqProvider(
                    api_key=settings.groq_api_key,
                    model=settings.planner_model,
                    temperature=settings.planner_temperature,
                    max_tokens=settings.planner_max_tokens,
                    timeout=settings.planner_timeout,
                )
            elif provider_name == "openai":
                if not settings.openai_api_key:
                    logger.warning("OPENAI_API_KEY is empty. Falling back to MockProvider for Planner role.")
                    return MockProvider()
                return OpenAIProvider(
                    api_key=settings.openai_api_key,
                    model=settings.planner_model,
                    temperature=settings.planner_temperature,
                    max_tokens=settings.planner_max_tokens,
                    timeout=settings.planner_timeout,
                )

        elif role == "cook":
            provider_name = settings.cook_provider.lower().strip()
            if provider_name == "groq":
                if not settings.groq_api_key:
                    logger.warning("GROQ_API_KEY is empty. Falling back to MockProvider for Cook role.")
                    return MockProvider()
                cook_model = settings.cook_model if "llama" in settings.cook_model.lower() or "mixtral" in settings.cook_model.lower() else "llama-3.3-70b-versatile"
                return GroqProvider(
                    api_key=settings.groq_api_key,
                    model=cook_model,
                    temperature=settings.cook_temperature,
                    max_tokens=settings.cook_max_tokens,
                    timeout=settings.cook_timeout,
                )
            elif provider_name == "google":
                if not settings.google_api_key:
                    logger.warning("GOOGLE_API_KEY is empty. Falling back to MockProvider for Cook role.")
                    return MockProvider()
                return GoogleProvider(
                    api_key=settings.google_api_key,
                    model=settings.cook_model if "gemini" in settings.cook_model.lower() else "gemini-1.5-pro",
                    temperature=settings.cook_temperature,
                    max_tokens=settings.cook_max_tokens,
                    timeout=settings.cook_timeout,
                )
            elif provider_name == "anthropic":
                if not settings.anthropic_api_key:
                    logger.warning("ANTHROPIC_API_KEY is empty. Falling back to MockProvider for Cook role.")
                    return MockProvider()
                return AnthropicProvider(
                    api_key=settings.anthropic_api_key,
                    model=settings.cook_model,
                    temperature=settings.cook_temperature,
                    max_tokens=settings.cook_max_tokens,
                    timeout=settings.cook_timeout,
                )

        elif role == "judge":
            provider_name = settings.judge_provider.lower().strip()
            if provider_name == "groq":
                if not settings.groq_api_key:
                    logger.warning("GROQ_API_KEY is empty. Falling back to MockProvider for Judge role.")
                    return MockProvider()
                judge_model = settings.judge_model if "llama" in settings.judge_model.lower() or "mixtral" in settings.judge_model.lower() else "llama-3.3-70b-versatile"
                return GroqProvider(
                    api_key=settings.groq_api_key,
                    model=judge_model,
                    temperature=settings.judge_temperature,
                    max_tokens=settings.judge_max_tokens,
                    timeout=settings.judge_timeout,
                )
            elif provider_name == "google":
                if not settings.google_api_key:
                    logger.warning("GOOGLE_API_KEY is empty. Falling back to MockProvider for Judge role.")
                    return MockProvider()
                return GoogleProvider(
                    api_key=settings.google_api_key,
                    model=settings.judge_model,
                    temperature=settings.judge_temperature,
                    max_tokens=settings.judge_max_tokens,
                    timeout=settings.judge_timeout,
                )

        if provider_name == "mock":
            return MockProvider()

        raise ProviderException(f"Unsupported or unconfigured provider '{provider_name}' for role '{role_name}'")
