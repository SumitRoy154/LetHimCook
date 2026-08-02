import json
import logging
import os
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Type, TypeVar

from pydantic import BaseModel, ValidationError

from app.agents.providers.base_provider import LLMProvider
from app.exceptions.agent import (
    AgentException,
    InvalidResponseException,
    PromptException,
)

logger = logging.getLogger(__name__)

OutputSchemaType = TypeVar("OutputSchemaType", bound=BaseModel)


class BaseAgent(ABC, Generic[OutputSchemaType]):
    """Abstract Base Class for all AI Agents."""

    def __init__(
        self,
        role_name: str,
        prompt_filename: str,
        output_schema: Type[OutputSchemaType],
        provider: LLMProvider,
    ):
        self.role_name = role_name
        self.prompt_filename = prompt_filename
        self.output_schema = output_schema
        self.provider = provider

    def load_prompt_template(self) -> str:
        """Load external markdown prompt file from backend/app/prompts/."""
        # Find prompts directory relative to app root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        prompt_path = os.path.join(base_dir, "prompts", self.prompt_filename)

        if not os.path.exists(prompt_path):
            raise PromptException(f"Prompt template file '{self.prompt_filename}' not found at {prompt_path}")

        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as exc:
            raise PromptException(f"Failed to read prompt template '{self.prompt_filename}': {exc}") from exc

    def parse_json_response(self, raw_text: str) -> Dict[str, Any]:
        """Extract and parse structured JSON dictionary from LLM response text."""
        cleaned_text = raw_text.strip()

        # Remove markdown ```json ... ``` code blocks if present
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned_text, re.IGNORECASE)
        if json_match:
            cleaned_text = json_match.group(1).strip()

        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as exc:
            logger.error("JSON parsing error for agent '%s': %s | Raw output: %s", self.role_name, exc, raw_text)
            raise InvalidResponseException(
                f"Agent '{self.role_name}' output failed JSON parsing: {exc}"
            ) from exc

    def validate_output(self, raw_dict: Dict[str, Any]) -> OutputSchemaType:
        """Validate parsed dictionary against the agent's Pydantic output schema."""
        try:
            return self.output_schema.model_validate(raw_dict)
        except ValidationError as exc:
            logger.error("Pydantic schema validation failure for agent '%s': %s", self.role_name, exc)
            raise InvalidResponseException(
                f"Agent '{self.role_name}' output failed schema validation: {exc}"
            ) from exc

    @abstractmethod
    def prepare_input(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw payload dictionary into template format variables."""
        pass

    def run(self, payload: Dict[str, Any]) -> OutputSchemaType:
        """Full agent execution pipeline: Prompt Load -> Provider Call -> JSON Parse -> Schema Validation."""
        start_time = time.time()
        logger.info("Starting execution for agent role '%s'", self.role_name)

        try:
            # 1. Load prompt template
            template = self.load_prompt_template()

            # 2. Prepare variables and format prompt
            formatted_vars = self.prepare_input(payload)
            formatted_prompt = template.format(**formatted_vars)

            # 3. Call LLM provider strategy
            raw_response = self.provider.generate(prompt=formatted_prompt)

            # 4. Parse JSON
            parsed_dict = self.parse_json_response(raw_response)

            # 5. Validate schema
            validated_result = self.validate_output(parsed_dict)

            exec_time = time.time() - start_time
            logger.info(
                "Agent '%s' executed successfully | time=%.2fs | provider=%s",
                self.role_name,
                exec_time,
                type(self.provider).__name__,
            )

            return validated_result

        except AgentException:
            raise
        except Exception as exc:
            exec_time = time.time() - start_time
            logger.error("Unexpected error in agent '%s' after %.2fs: %s", self.role_name, exec_time, exc)
            raise AgentException(f"Agent '{self.role_name}' failed during execution: {exc}") from exc
