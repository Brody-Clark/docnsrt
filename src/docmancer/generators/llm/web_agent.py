"""Web-based LLM agent."""

from typing import Dict, Any, Optional
import json
import httpx
from docmancer.generators.llm.llm_agent_base import LlmAgentBase


class WebAgent(LlmAgentBase):
    """
    Web-based LLM agent.
    """

    def __init__(self, api_endpoint: str, api_key: Optional[str] = None):
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
        if not api_endpoint:
            raise ValueError("API endpoint cannot be empty.")
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        # Use httpx.AsyncClient for persistent connections and better performance
        # across multiple requests.
        self._client = httpx.AsyncClient()

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
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            # Common header for Bearer token authentication (e.g., OpenAI, many others)
            headers["Authorization"] = f"Bearer {self.api_key}"
            # Some APIs might use different headers, e.g., "X-API-Key"

        try:
            response = await self._client.post(
                self.api_endpoint,
                headers=headers,
                json=payload,
                timeout=60.0,  # Set a reasonable timeout for LLM responses
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
