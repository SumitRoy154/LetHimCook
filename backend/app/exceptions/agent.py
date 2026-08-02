from app.exceptions.base import BusinessException


class AgentException(BusinessException):
    """Base exception for all AI agent framework errors."""
    pass


class ProviderException(AgentException):
    """Raised when an LLM provider API call or initialization fails."""
    def __init__(self, message: str = "LLM provider error occurred"):
        super().__init__(message)


class InvalidResponseException(AgentException):
    """Raised when LLM output fails JSON parsing or Pydantic schema validation."""
    def __init__(self, message: str = "Invalid structured JSON response from LLM"):
        super().__init__(message)


class PromptException(AgentException):
    """Raised when prompt template loading or formatting fails."""
    def __init__(self, message: str = "Prompt template resolution failed"):
        super().__init__(message)
