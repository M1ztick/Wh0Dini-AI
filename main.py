from Wh0Dini_AI_main import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",  # Allow external connections
        port=8000,  # Explicit port specification
        reload=True,  # Auto-reload during development
    )
