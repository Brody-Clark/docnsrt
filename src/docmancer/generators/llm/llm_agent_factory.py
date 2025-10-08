"""Factory class for creating LLM agents."""

from docmancer.config import LLMConfig, LLMType
from docmancer.generators.llm.llm_agent_base import LlmAgentBase
from docmancer.generators.llm.local_agent import LlamaCppAgent
from docmancer.generators.llm.web_agent import WebAgent

class LlmFactory:
    """Factory class for creating LLM agents."""

    def get_agent(self, llm_config: LLMConfig) -> LlmAgentBase:
        """Get an LLM agent based on the provided configuration.

        Args:
            llm_config (LLMConfig): The configuration for the LLM agent.

        Raises:
            NotImplementedError: If the LLM type is not supported.

        Returns:
            LlmAgentBase: An instance of the LLM agent.
        """
        if llm_config.get_mode_enum() == LLMType.LOCAL:
            return LlamaCppAgent(llm_config)
        if llm_config.get_mode_enum() == LLMType.REMOTE_API:
            return WebAgent(llm_config)

        raise NotImplementedError(f"Provided config is not supported")
