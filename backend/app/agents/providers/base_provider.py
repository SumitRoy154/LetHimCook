from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """Abstract Strategy Interface for LLM Providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Send prompt to LLM provider and return raw text response."""
        pass
