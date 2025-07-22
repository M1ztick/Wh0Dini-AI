import os
import sys
import types
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Add the project root to sys.path so imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Single app import at module level
try:
    from wh0dini_ai import app
    import wh0dini_ai.app as app_module
except ImportError:
    try:
        import app as app_module
        from app import app
    except ImportError:
        import Wh0Dini_AI_main as app_module
        from Wh0Dini_AI_main import app


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def patch_openai_client():
    # Patch the OpenAI client
    mock_client = AsyncMock()

    # Mock regular completion
    mock_completion = AsyncMock()
    mock_completion.choices = [
        types.SimpleNamespace(message=types.SimpleNamespace(content="Hello!"))
    ]
    mock_completion.usage = types.SimpleNamespace(total_tokens=10)

    # Mock streaming
    async def mock_stream(*_args: Any, **_kwargs: Any):
        class MockChunk:
            def __init__(self, content: str):
                self.choices = [
                    types.SimpleNamespace(delta=types.SimpleNamespace(content=content))
                ]

        yield MockChunk("Hello, ")
        yield MockChunk("world!")

    # Set up the side effect
    def create_completion(*args: Any, **kwargs: Any):
        if kwargs.get("stream"):
            return mock_stream(*args, **kwargs)
        return mock_completion

    mock_client.chat.completions.create.side_effect = create_completion

    # Mock models for health check
    mock_models = AsyncMock()
    mock_models.list.return_value = ["gpt-4o-mini"]
    mock_client.models = mock_models

    with patch.object(app_module, "client", mock_client):
        yield


@pytest.mark.anyio
async def test_health_check():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "openai" in data["services"]
        assert data["services"]["openai"]["status"] == "connected"


@pytest.mark.anyio
async def test_chat_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        payload = {"messages": [{"role": "user", "content": "Hello!"}]}
        resp = await ac.post("/chat", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "response" in data
        assert data["response"] == "Hello!"
        assert "request_id" in data


@pytest.mark.anyio
async def test_chat_stream_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        payload = {"messages": [{"role": "user", "content": "Stream this!"}]}
        resp = await ac.post("/chat/stream", json=payload)
        assert resp.status_code == 200

        # Properly read streaming response
        content = await resp.aread()
        text = content.decode("utf-8")

        # More specific assertions for streaming format
        assert resp.headers.get("content-type") == "text/plain; charset=utf-8"
        assert "Hello, " in text
        assert "world!" in text
