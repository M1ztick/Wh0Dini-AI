import json
import os
import uuid
from datetime import datetime
from typing import List

import structlog  # type: ignore
import tiktoken
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


# Configuration Management
class Settings(BaseSettings):
    openai_api_key: str = ""  # Make it optional initially
    model_name: str = "gpt-4o-mini"
    max_tokens: int = 500
    rate_limit: str = "10/minute"
    max_message_length: int = 4000
    max_conversation_tokens: int = 3000
    temperature: float = 0.2

    # Additional fields from .env file
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    environment: str = "development"
    log_level: str = "INFO"
    require_auth: bool = False
    api_key: str = "your_secure_api_key_here"
    allowed_origins: List[str] = ["http://localhost:3000",
                                  "http://localhost:8080", "http://localhost:8000"]
    rate_limit_per_minute: int = 10
    debug: bool = True
    reload: bool = True

    class Config:
        env_file = ".env"

    def validate_settings(self) -> None:
        """Validate critical settings after initialization"""
        if not self.openai_api_key or self.openai_api_key.strip() == "":
            raise ValueError(
                "OpenAI API key is required. Please set OPENAI_API_KEY environment variable or add it to .env file"
            )

        if self.openai_api_key == "your-openai-api-key-here":
            raise ValueError(
                "Please set a valid OpenAI API key. The default placeholder value is not valid."
            )


try:
    settings = Settings()
    settings.validate_settings()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("\nTo fix this:")
    print("1. Create a .env file in the project root")
    print("2. Add: OPENAI_API_KEY=your_actual_api_key_here")
    print("3. Get your API key from: https://platform.openai.com/api-keys")
    exit(1)
except Exception as e:
    print(f"Settings initialization failed: {e}")
    exit(1)

# Initialize OpenAI client (modern async client) with error handling
try:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
except Exception as e:
    print(f"Failed to initialize OpenAI client: {e}")
    exit(1)

# System prompt (moved from config.py)
SYSTEM_PROMPT = """
You are Wh0Dini-AI, a privacy-first, user-centric AI assistant.

Core Principles:
- Always prioritize user privacy: never store or log personal data
- Communicate clearly, respectfully, and empathetically
- Provide helpful, relevant, and safe information
- Avoid harmful, offensive, or biased content
- Encourage positive and ethical use
- Be concise but thorough in responses
- Acknowledge limitations honestly

Remember: You're designed to be helpful while maintaining the highest ethical standards.
"""

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)

# FastAPI app initialization
app = FastAPI(
    title="Wh0Dini-AI - User-first, Privacy-focused AI Assistant",
    description="A privacy-first FastAPI chatbot assistant powered by GPT-4o-mini that delivers intelligent conversations without compromising user data or identity.",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Mount static files with error handling
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Pydantic Models


class Message(BaseModel):
    role: str = Field(..., description="Role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., description="Conversation history")
    stream: bool = Field(default=False, description="Enable streaming response")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Wh0Dini-AI's reply")
    request_id: str = Field(..., description="Unique request identifier")

# Utility Functions (Fixed)


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Count tokens in text using tiktoken."""
    if not text:
        return 0

    try:
        # Handle different model names that might not be in tiktoken
        model_name = model
        if model.startswith("gpt-4o"):
            model_name = "gpt-4"  # Use gpt-4 encoding for gpt-4o variants
        elif model.startswith("gpt-3.5"):
            model_name = "gpt-3.5-turbo"

        encoding = tiktoken.encoding_for_model(model_name)
        return len(encoding.encode(text))
    except Exception as e:
        logger.warning("Token counting failed, using estimation", error=str(e))
        # Fallback estimation: ~4 chars per token
        return max(1, len(text) // 4)


def trim_conversation(messages: List[Message], max_tokens: int = 3000) -> List[Message]:
    """Trim conversation to stay within token limits while preserving context."""
    total_tokens = 0
    trimmed_messages = []

    # Process messages in reverse to keep most recent
    for message in reversed(messages):
        message_tokens = count_tokens(message.content)
        if total_tokens + message_tokens > max_tokens and len(trimmed_messages) > 0:
            break
        trimmed_messages.insert(0, message)
        total_tokens += message_tokens

    return trimmed_messages


def validate_message(message: Message) -> None:
    """Validate individual message."""
    if message.role not in ("user", "assistant", "system"):
        raise HTTPException(status_code=400, detail="Invalid message role")

    if not message.content:
        raise HTTPException(status_code=400, detail="Message content cannot be empty")

    if len(message.content) > settings.max_message_length:
        raise HTTPException(status_code=400, detail="Message too long")

    if not message.content.strip():
        raise HTTPException(status_code=400, detail="Empty message content")

# Main Chat Endpoint (Fixed)


@app.post("/chat", response_model=ChatResponse)
@limiter.limit(settings.rate_limit)
async def chat_endpoint(request: Request, chat_request: ChatRequest):
    """Enhanced chat endpoint with improved error handling, validation, and logging."""
    request_id = str(uuid.uuid4())

    try:
        logger.info(
            "chat_request_received",
            request_id=request_id,
            message_count=len(chat_request.messages),
            client_ip=get_remote_address(request)
        )

        if not chat_request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        for message in chat_request.messages:
            validate_message(message)

        trimmed_messages = trim_conversation(
            chat_request.messages,
            settings.max_conversation_tokens
        )

        openai_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in trimmed_messages:
            openai_messages.append({"role": msg.role, "content": msg.content})

        # Use modern async client
        completion = await client.chat.completions.create(
            model=settings.model_name,
            messages=openai_messages,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            user=request_id
        )

        # Add null safety checks
        if not completion or not completion.choices or len(completion.choices) == 0:
            raise HTTPException(
                status_code=500, detail="Invalid response from AI service")

        message_content = completion.choices[0].message.content
        if message_content is None:
            reply = "I apologize, but I couldn't generate a response. Please try again."
        else:
            reply = message_content.strip()

        logger.info(
            "chat_response_generated",
            request_id=request_id,
            response_length=len(reply),
            tokens_used=completion.usage.total_tokens if completion.usage else 0
        )

        return ChatResponse(response=reply, request_id=request_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "chat_error",
            request_id=request_id,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail="Internal server error")

# Streaming Chat Endpoint (Fixed)


@app.post("/chat/stream")
@limiter.limit(settings.rate_limit)
async def chat_stream(request: Request, chat_request: ChatRequest):
    """Streaming chat endpoint for real-time responses."""
    request_id = str(uuid.uuid4())

    async def generate_stream():
        try:
            if not chat_request.messages:
                yield "data: {\"error\": \"No messages provided\"}\n\n"
                return

            for message in chat_request.messages:
                validate_message(message)

            trimmed_messages = trim_conversation(
                chat_request.messages,
                settings.max_conversation_tokens
            )

            openai_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in trimmed_messages:
                openai_messages.append({"role": msg.role, "content": msg.content})

            stream = await client.chat.completions.create(
                model=settings.model_name,
                messages=openai_messages,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                stream=True,
                user=request_id
            )

            async for chunk in stream:
                # Enhanced null safety checks
                if (chunk and
                    hasattr(chunk, 'choices') and
                    chunk.choices and
                    len(chunk.choices) > 0 and
                    chunk.choices[0].delta and
                    hasattr(chunk.choices[0].delta, 'content') and
                        chunk.choices[0].delta.content is not None):

                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content, 'request_id': request_id})}\n\n"

            yield "data: [DONE]\n\n"

        except HTTPException as e:
            yield f"data: {json.dumps({'error': e.detail})}\n\n"
        except Exception as e:
            logger.error("stream_error", request_id=request_id, error=str(e))
            yield f"data: {json.dumps({'error': 'Internal server error'})}\n\n"

    try:
        logger.info("stream_request_started", request_id=request_id)

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "X-Request-ID": request_id,
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )

    except Exception as e:
        logger.error("stream_setup_error", request_id=request_id, error=str(e))
        raise HTTPException(status_code=500, detail="Stream setup failed")

# Health Check (Fixed)


@app.get("/health")
async def health_check():
    """Comprehensive health check including OpenAI connectivity."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {}
    }

    try:
        # Test OpenAI connectivity with timeout
        import asyncio
        models = await asyncio.wait_for(client.models.list(), timeout=5.0)
        health_status["services"]["openai"] = {
            "status": "connected",
            "model": settings.model_name
        }
    except asyncio.TimeoutError:
        health_status["status"] = "degraded"
        health_status["services"]["openai"] = {
            "status": "timeout",
            "error": "OpenAI API request timed out"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["openai"] = {
            "status": "disconnected",
            "error": str(e)
        }

    return health_status


@app.get("/")
async def root():
    return {
        "name": "Wh0Dini-AI",
        "version": "2.0.0",
        "description": "Privacy-first AI assistant that makes your data disappear like magic",
        "endpoints": {
            "chat": "/chat",
            "stream": "/chat/stream",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/chat-ui", response_class=HTMLResponse)
async def chat_ui():
    """Serve the web chat interface"""
    try:
        static_path = "static/index.html"
        if not os.path.exists(static_path):
            return HTMLResponse(
                content="""
                <!DOCTYPE html>
                <html>
                <head><title>Wh0Dini-AI</title></head>
                <body>
                    <h1>Wh0Dini-AI Chat Interface</h1>
                    <p>Chat UI not found. Please create static/index.html</p>
                    <p>Use the API at <a href="/docs">/docs</a> for testing.</p>
                </body>
                </html>
                """,
                status_code=200
            )

        with open(static_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except Exception as e:
        logger.error("chat_ui_error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to load chat interface")

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(
            "Wh0Dini_AI_main:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.reload,
            log_level=settings.log_level.lower()
        )
    except ImportError:
        print(
            "Error: uvicorn is not installed. Please install it with: pip install uvicorn[standard]")
        exit(1)
    except Exception as e:
        logger.error("startup_error", error=str(e))
        print(f"Failed to start server: {e}")
        exit(1)
