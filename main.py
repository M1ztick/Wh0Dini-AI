# FastAPI Application Entry Point
# This file serves as the main entry point and imports the app from Wh0Dini_AI_main.py

from Wh0Dini_AI_main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
