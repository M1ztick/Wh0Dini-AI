"""
Main entry point for Wh0Dini-AI application.
"""


def main():
    """Main entry point for the application."""
    import uvicorn

    uvicorn.run(
        "wh0dini_ai.app:app",  # Use import string for reload to work
        host="0.0.0.0",  # Allow external connections
        port=8000,  # Explicit port specification
        reload=True,  # Auto-reload during development
    )


if __name__ == "__main__":
    main()
