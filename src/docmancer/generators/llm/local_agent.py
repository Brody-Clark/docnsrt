"""Local LLM agent for inference using LlamaCpp."""

from llama_cpp import Llama
from docmancer.generators.llm.llm_agent_base import LlmAgentBase
from docmancer.config import LLMConfig


class LlamaCppAgent(LlmAgentBase):
    """
    LLM-based agent for local inference using LlamaCpp.
    """

    def __init__(self, settings: LLMConfig):
        self._settings = settings
        self._llm = Llama(
            model_path=self._settings.local.model_path,
            chat_format="chatml",
            n_ctx=self._settings.local.n_ctx,
            verbose=self._settings.local.log_verbose,
            n_gpu_layers=self._settings.local.n_gpu_layers,
            n_threads=self._settings.local.n_threads,
        )
        # Warm up the model
        self._llm(
            prompt="hello",
            max_tokens=1,
            stream=False,
        )

    def get_response(self, message: str) -> str:

        print("Generating response from local LLM...")
        response = self._llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "You are a source code documentation generator that responds only in JSON format.",
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            response_format={
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "number": {"type": "int"},
                        "letter": {"type": "string"},
                    },
                    "required": ["number", "letter"],
                },
            },
            temperature=self._settings.temperature,
        )

        return response["choices"][0]["message"]["content"]
