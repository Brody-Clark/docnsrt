"""Web-based LLM agent."""

import logging
import json
import requests
from copy import deepcopy
from docmancer.generators.llm.llm_agent_base import LlmAgentBase
from docmancer.config import LLMConfig

logger = logging.getLogger(__name__)

class WebAgent(LlmAgentBase):
    """
    Web-based LLM agent.
    """

    def __init__(self, settings: LLMConfig, timeout_seconds: int = 60):
        """
        Initializes the WebAgent with the LLM API endpoint and an optional API key.

        Args:
            api_endpoint (str): The URL of the LLM API endpoint.
                                 Examples:
                                 - OpenAI: "https://api.openai.com/v1/chat/completions"
                                 - Custom hosted model: "https://your-custom-llm.com/generate"
            api_key (Optional[str]): The API key for authentication, if required by the endpoint.
                                      Can be None if the endpoint doesn't require one.
        """
        if not settings.remote_api.api_endpoint:
            raise ValueError("API endpoint cannot be empty.")
        self.api_endpoint = settings.remote_api.api_endpoint
        self._timeout_seconds = timeout_seconds
        self.temperature = settings.temperature
        self._headers = settings.remote_api.headers or {}
        self._payload_template = settings.remote_api.payload_template or {}
        self._response_path = settings.remote_api.response_path or ""
        self._prompt_placeholder = "${prompt}"

    def _replace_prompt_in_obj(self, obj: any, prompt: str) -> any:
        """
        Recursively replace occurrences of the prompt placeholder in a JSON-like structure.

        Supports nested dicts, lists and strings (including strings that contain the placeholder).
        Leaves other types untouched.
        """
        if isinstance(obj, str):
            if self._prompt_placeholder in obj:
                return obj.replace(self._prompt_placeholder, prompt)
            return obj
        if isinstance(obj, dict):
            return {k: self._replace_prompt_in_obj(v, prompt) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._replace_prompt_in_obj(v, prompt) for v in obj]
        return obj

    def get_response(self, message: str) -> str:
        """
        Sends a message to the LLM API and returns the response.

        Args:
            message (str): The message to send to the LLM.

        Returns:
            str: The response from the LLM as a string.

        Raises:
            httpx.HTTPStatusError: If the API returns a non-2xx status code.
            httpx.RequestError: For network-related errors.
            json.JSONDecodeError: If the response is not valid JSON.
        """
        # Build payload by substituting prompt placeholder in a deepcopy of the template
        payload = deepcopy(self._payload_template)
        payload = self._replace_prompt_in_obj(payload, message)

        logger.info(
            f"Sending request to LLM API at {self.api_endpoint} with payload: {payload}"
        )
        try:
            response = requests.post(
                self.api_endpoint,
                headers=self._headers,
                json=payload,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            response_json = response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.exception(
                f"HTTP error occurred: {http_err} - Response content: {response.text}"
            )
            return None
        except requests.exceptions.RequestException as e:
            logger.exception(f"Error occurred while making API request: {e}")
            return None

        # Extract response based on response path if provided
        if self._response_path:
            parts = self._response_path.split(".")
            node = response_json
            for p in parts:
                if isinstance(node, dict):
                    node = node.get(p, {})
                elif p.isdigit() and isinstance(node, list):
                    idx = int(p)
                    if 0 <= idx < len(node):
                        node = node[idx]
                    else:
                        node = {}
            # if final node is not a string, return its json representation
            return node if isinstance(node, str) else json.dumps(node)

        # Default: return json.dumps of the full response
        return json.dumps(response_json)
