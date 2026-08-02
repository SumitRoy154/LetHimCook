import logging
import time
from typing import Optional

import anthropic

from app.agents.providers.base_provider import LLMProvider
from app.exceptions.agent import ProviderException

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """Real Anthropic Claude LLM Provider strategy using the official Anthropic Python SDK."""

    def __init__(
        self,
        api_key: str = "",
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 3000,
        timeout: float = 60.0,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            logger.warning("Anthropic API key missing. AnthropicProvider cannot execute live call.")
            raise ProviderException("Anthropic API key is missing. Set ANTHROPIC_API_KEY in environment.")

        start_time = time.time()
        logger.info(
            "Executing Anthropic API call | model=%s, temp=%.2f, max_tokens=%s, timeout=%.1fs",
            self.model,
            self.temperature,
            self.max_tokens,
            self.timeout,
        )

        try:
            client = anthropic.Anthropic(api_key=self.api_key, timeout=self.timeout)

            kwargs = {
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            response = client.messages.create(**kwargs)
            exec_time = time.time() - start_time

            # Extract content text blocks
            content_blocks = [b.text for b in response.content if hasattr(b, "text")]
            content_str = "\n".join(content_blocks) if content_blocks else ""

            # Log token metrics
            total_tokens = None
            if hasattr(response, "usage") and response.usage:
                total_tokens = getattr(response.usage, "input_tokens", 0) + getattr(response.usage, "output_tokens", 0)

            logger.info(
                "Anthropic call successful | exec_time=%.2fs | total_tokens=%s",
                exec_time,
                total_tokens,
            )

            return content_str

        except anthropic.AuthenticationError as exc:
            logger.error("Anthropic Authentication Error: %s", exc)
            raise ProviderException(f"Anthropic Authentication Error: Invalid API key. {exc}") from exc
        except anthropic.RateLimitError as exc:
            logger.error("Anthropic Rate Limit Error: %s", exc)
            raise ProviderException(f"Anthropic Rate Limit Exceeded: {exc}") from exc
        except anthropic.APITimeoutError as exc:
            logger.error("Anthropic Timeout Error: %s", exc)
            raise ProviderException(f"Anthropic API call timed out after {self.timeout}s: {exc}") from exc
        except anthropic.APIError as exc:
            logger.error("Anthropic API Error: %s", exc)
            raise ProviderException(f"Anthropic API Error: {exc}") from exc
        except Exception as exc:
            logger.error("Unexpected Anthropic Provider error: %s", exc)
            raise ProviderException(f"Anthropic Provider execution error: {exc}") from exc
