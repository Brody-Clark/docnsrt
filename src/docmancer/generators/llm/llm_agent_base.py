from abc import ABC, abstractmethod


class LlmAgentBase(ABC):
    """Base class for LLM agents."""

    @abstractmethod
    def get_response(self, message: str) -> str:
        """Sends a message to the LLM and returns the response.

        Args:
            message (str): User prompt used to generate function summary

        Returns:
            str: JSON response containing function summary
        """
