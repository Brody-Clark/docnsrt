"""Web-based LLM agent."""

from typing import Dict, Any, Optional
import json
import httpx
from docmancer.generators.llm.llm_agent_base import LlmAgentBase
from docmancer.config import RemoteLLMSettings


class WebAgent(LlmAgentBase):
    """
    Web-based LLM agent.
    """

    def __init__(self, settings: RemoteLLMSettings, timeout_seconds: int = 60):
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
        if not settings.base_url:
            raise ValueError("API endpoint cannot be empty.")
        self.api_endpoint = settings.base_url
        self._client = httpx.AsyncClient()
        self._timeout_seconds = timeout_seconds
        self.temperature = settings.temperature
        self._headers = settings.headers or {}
        self._payload_template = settings.payload_template or {}
        self._response_path = settings.response_path or ""
        
    
    def send_message(self, message: str) -> str:
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
        # Construct payload based on template and message
        payload = self._payload_template.copy()
        payload["messages"] = [
            {
                "role": "system",
                "content": "You are a source code documentation generator that responds only in JSON format.",
            },
            {
                "role": "user",
                "content": message,
            },
        ]

        # Make the API request
        try:
            response_json = httpx.run(self._make_api_request(payload))
        except httpx.HTTPError as e:
            print(f"Error occurred while making API request: {e}")
            return json.dumps({"error": str(e)})

        # Extract response based on response path if provided
        if self._response_path:
            keys = self._response_path.split(".")
            for key in keys:
                response_json = response_json.get(key, {})
        
        return json.dumps(response_json)
    async def _make_api_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to make the actual HTTP POST request to the LLM API.

        Args:
            payload (Dict[str, Any]): The JSON payload to send to the API.
                                       This structure depends heavily on the LLM API.

        Returns:
            Dict[str, Any]: The JSON response from the API.

        Raises:
            httpx.HTTPStatusError: If the API returns a non-2xx status code.
            httpx.RequestError: For network-related errors.
            json.JSONDecodeError: If the response is not valid JSON.
        """
        try:
            response = await self._client.post(
                self.api_endpoint,
                headers=self._headers,
                json=payload,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses
            return response.json()
        except httpx.HTTPStatusError as e:
            print(
                f"API request failed with status {e.response.status_code}: {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}: {e}")
            raise
        except json.JSONDecodeError as e:
            print(
                f"Failed to decode JSON response: {e}. Response text: {response.text}"
            )
            raise
