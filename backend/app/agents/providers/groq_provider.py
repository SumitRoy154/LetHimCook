import logging
import time
from typing import Optional

import groq

from app.agents.providers.base_provider import LLMProvider
from app.exceptions.agent import ProviderException

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    """Real Groq LLM Provider strategy using the official Groq Python SDK."""

    def __init__(
        self,
        api_key: str = "",
        model: str = "llama-3.3-70b-versatile",
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
            logger.warning("Groq API key missing. GroqProvider cannot execute live call.")
            raise ProviderException("Groq API key is missing. Set GROQ_API_KEY in environment.")

        logger.info("Executing Groq API call")
        logger.info("Provider: Groq")
        logger.info("Model: %s", self.model)

        start_time = time.time()

        try:
            client = groq.Groq(api_key=self.api_key, timeout=self.timeout)

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

            tokens_used = getattr(response.usage, "total_tokens", None) if hasattr(response, "usage") else None
            logger.info(
                "Groq call successful | exec_time=%.2fs | total_tokens=%s",
                exec_time,
                tokens_used,
            )

            return content

        except groq.AuthenticationError as exc:
            logger.error("Groq Authentication Error: %s", exc)
            raise ProviderException(f"Groq Authentication Error: Invalid API key. {exc}") from exc
        except groq.RateLimitError as exc:
            logger.error("Groq Rate Limit Error: %s", exc)
            raise ProviderException(f"Groq Rate Limit Exceeded: {exc}") from exc
        except groq.APITimeoutError as exc:
            logger.error("Groq Timeout Error: %s", exc)
            raise ProviderException(f"Groq API call timed out after {self.timeout}s: {exc}") from exc
        except groq.APIConnectionError as exc:
            logger.error("Groq Network/Connection Error: %s", exc)
            raise ProviderException(f"Groq Network Error: Unable to connect to Groq API. {exc}") from exc
        except groq.APIError as exc:
            logger.error("Groq API Error: %s", exc)
            raise ProviderException(f"Groq API Error: {exc}") from exc
        except Exception as exc:
            logger.error("Unexpected Groq Provider error: %s", exc)
            raise ProviderException(f"Groq Provider execution error: {exc}") from exc
