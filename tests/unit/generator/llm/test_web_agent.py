from unittest.mock import patch, mock_open
import pytest
import requests
from docmancer.generators.llm import web_agent
from docmancer.config import LLMConfig, RemoteLLMSettings


def test_web_agent_init_raises_on_empty_endpoint():
    settings = LLMConfig(
        mode="REMOTE_API",
        remote_api=RemoteLLMSettings(
            provider="TestProvider",
            api_endpoint="",  # Empty endpoint should raise ValueError
        ),
    )
    with pytest.raises(ValueError, match="API endpoint cannot be empty."):
        web_agent.WebAgent(settings)


@patch("docmancer.generators.llm.web_agent.requests.post")
def test_web_agent_get_response_success(mock_post):
    # Mock successful API response
    mock_response = mock_post.return_value
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [{"message": {"content": '{"number": 42, "letter": "A"}'}}]
    }

    settings = LLMConfig(
        mode="REMOTE_API",
        temperature=0.5,
        remote_api=RemoteLLMSettings(
            provider="TestProvider",
            api_endpoint="https://api.test.com/v1/chat/completions",
            headers={"Authorization": "Bearer testkey"},
            payload_template={
                "model": "test-model",
                "messages": [{"role": "user", "content": "${prompt}"}],
                "max_tokens": 100,
                "temperature": 0.5,
            },
            response_path="choices.0.message.content",
        ),
    )

    agent = web_agent.WebAgent(settings)
    response = agent.get_response("Hello, world!")

    assert response == '{"number": 42, "letter": "A"}'
    mock_post.assert_called_once()
    called_args, called_kwargs = mock_post.call_args
    assert called_args[0] == "https://api.test.com/v1/chat/completions"
    assert called_kwargs["headers"]["Authorization"] == "Bearer testkey"
    assert called_kwargs["json"]["messages"][0]["content"] == "Hello, world!"


@patch("docmancer.generators.llm.web_agent.requests.post")
def test_web_agent_get_response_http_error(mock_post):
    # Mock HTTP error response
    mock_response = mock_post.return_value
    mock_response.raise_for_status.side_effect = requests.HTTPError(
        "401 Client Error: Unauthorized"
    )

    settings = LLMConfig(
        mode="REMOTE_API",
        remote_api=RemoteLLMSettings(
            provider="TestProvider",
            api_endpoint="https://api.test.com/v1/chat/completions",
            headers={"Authorization": "Bearer invalidkey"},
            payload_template={
                "model": "test-model",
                "messages": [{"role": "user", "content": "${prompt}"}],
                "max_tokens": 100,
                "temperature": 0.5,
            },
            response_path="choices.0.message.content",
        ),
    )

    # Web agent should return None on HTTP error
    agent = web_agent.WebAgent(settings)
    assert agent.get_response("Hello, world!") == None

    mock_post.assert_called_once()
