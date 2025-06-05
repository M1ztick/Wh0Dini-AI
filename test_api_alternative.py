import os
import sys
import types
from typing import Any, Optional
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Add the project root to sys.path so imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the app module (remove unused app_module import)
try:
    from app import app
except ImportError:
    # Fallback to direct import if app.py doesn't exist
    from Wh0Dini_AI_main import app


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def patch_openai_client():
    # Import the actual module to patch
    try:
        import app as app_module_import
    except ImportError:
        import Wh0Dini_AI_main as app_module_import

    # Patch the OpenAI AsyncOpenAI client in the app module
    mock_client = AsyncMock()
    # Mock chat.completions.create for /chat and /chat/stream
    mock_completion = AsyncMock()
    mock_completion.choices = [
        types.SimpleNamespace(message=types.SimpleNamespace(content="Hello!"))
    ]
    mock_completion.usage = types.SimpleNamespace(total_tokens=10)
    mock_client.chat.completions.create.return_value = mock_completion

    # For streaming, yield a mock async generator
    async def mock_stream(*args: Any, **kwargs: Any):
        class MockChunk:
            def __init__(self, content: Optional[str]):
                self.choices = [
                    types.SimpleNamespace(delta=types.SimpleNamespace(content=content))
                ]

        yield MockChunk("Hello, ")
        yield MockChunk("world!")
        yield MockChunk(None)  # Simulate end

    mock_client.chat.completions.create.side_effect = lambda *args: Any, **kwargs: Any: (
        mock_stream() if kwargs.get("stream") else mock_completion
    )

    # Mock models.list for health check
    mock_models = AsyncMock()
    mock_models.list.return_value = ["gpt-4o-mini"]
    mock_client.models = mock_models

    with patch.object(app_module_import, "client", mock_client):
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
        # The response is streamed as text/plain, so we check the content
        text = resp.text
        assert "Hello, " in text or "world!" in text
        assert "[DONE]" in text or "data:" in text
