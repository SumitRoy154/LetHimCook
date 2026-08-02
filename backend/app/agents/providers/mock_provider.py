import logging
from typing import Callable, Optional

from app.agents.providers.base_provider import LLMProvider

logger = logging.getLogger(__name__)


class MockProvider(LLMProvider):
    """Mock LLM Provider for unit testing and offline development."""

    def __init__(self, response_generator: Optional[Callable[[str], str]] = None):
        self.response_generator = response_generator

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        logger.info("MockProvider invoked with prompt length: %s", len(prompt))
        if self.response_generator:
            return self.response_generator(prompt)
        return "{}"
