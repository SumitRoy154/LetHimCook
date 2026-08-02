import logging
import time
from typing import Optional

import openai

from app.agents.providers.base_provider import LLMProvider
from app.exceptions.agent import ProviderException

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """Real OpenAI LLM Provider strategy using the official OpenAI Python SDK."""

    def __init__(
        self,
        api_key: str = "",
        model: str = "gpt-4o",
        temperature: float = 0.3,
        max_tokens: int = 1500,
        timeout: float = 30.0,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            logger.warning("OpenAI API key missing. OpenAIProvider cannot execute live call.")
            raise ProviderException("OpenAI API key is missing. Set OPENAI_API_KEY in environment.")

        start_time = time.time()
        logger.info(
            "Executing OpenAI API call | model=%s, temp=%.2f, max_tokens=%s, timeout=%.1fs",
            self.model,
            self.temperature,
            self.max_tokens,
            self.timeout,
        )

        try:
            client = openai.OpenAI(api_key=self.api_key, timeout=self.timeout)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                messages=messages,
                response_format={"type": "json_object"},
            )

            exec_time = time.time() - start_time
            content = response.choices[0].message.content or ""

            # Log token usage metrics if available
            tokens_used = getattr(response.usage, "total_tokens", None) if hasattr(response, "usage") else None
            logger.info(
                "OpenAI call successful | exec_time=%.2fs | total_tokens=%s",
                exec_time,
                tokens_used,
            )

            return content

        except openai.AuthenticationError as exc:
            logger.error("OpenAI Authentication Error: %s", exc)
            raise ProviderException(f"OpenAI Authentication Error: Invalid API key. {exc}") from exc
        except openai.RateLimitError as exc:
            logger.error("OpenAI Rate Limit Error: %s", exc)
            raise ProviderException(f"OpenAI Rate Limit Exceeded: {exc}") from exc
        except openai.APITimeoutError as exc:
            logger.error("OpenAI Timeout Error: %s", exc)
            raise ProviderException(f"OpenAI API call timed out after {self.timeout}s: {exc}") from exc
        except openai.APIError as exc:
            logger.error("OpenAI API Error: %s", exc)
            raise ProviderException(f"OpenAI API Error: {exc}") from exc
        except Exception as exc:
            logger.error("Unexpected OpenAI Provider error: %s", exc)
            raise ProviderException(f"OpenAI Provider execution error: {exc}") from exc
