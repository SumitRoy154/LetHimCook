import logging
import time
from typing import Optional

from app.agents.providers.base_provider import LLMProvider
from app.exceptions.agent import ProviderException

logger = logging.getLogger(__name__)


class GoogleProvider(LLMProvider):
    """Real Google Gemini LLM Provider strategy using the official Google GenAI SDK."""

    def __init__(
        self,
        api_key: str = "",
        model: str = "gemini-1.5-pro",
        temperature: float = 0.2,
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
            logger.warning("Google API key missing. GoogleProvider cannot execute live call.")
            raise ProviderException("Google API key is missing. Set GOOGLE_API_KEY in environment.")

        start_time = time.time()
        logger.info(
            "Executing Google Gemini API call | model=%s, temp=%.2f, max_tokens=%s, timeout=%.1fs",
            self.model,
            self.temperature,
            self.max_tokens,
            self.timeout,
        )

        try:
            # Try new google.genai SDK first
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=self.api_key)
                config = types.GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                    response_mime_type="application/json",
                )
                if system_prompt:
                    config.system_instruction = system_prompt

                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config,
                )
                exec_time = time.time() - start_time
                logger.info("Google Gemini call successful (genai SDK) | exec_time=%.2fs", exec_time)
                return response.text or ""

            except ImportError:
                # Fall back to google.generativeai SDK
                import google.generativeai as legacy_genai

                legacy_genai.configure(api_key=self.api_key)
                system_instruction = system_prompt if system_prompt else None
                model_instance = legacy_genai.GenerativeModel(
                    model_name=self.model,
                    system_instruction=system_instruction,
                    generation_config=legacy_genai.GenerationConfig(
                        temperature=self.temperature,
                        max_output_tokens=self.max_tokens,
                        response_mime_type="application/json",
                    ),
                )
                response = model_instance.generate_content(prompt, request_options={"timeout": self.timeout})
                exec_time = time.time() - start_time
                logger.info("Google Gemini call successful (legacy SDK) | exec_time=%.2fs", exec_time)
                return response.text or ""

        except Exception as exc:
            logger.error("Google Gemini API Error: %s", exc)
            raise ProviderException(f"Google Gemini Provider execution error: {exc}") from exc
