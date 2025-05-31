# Wh0Dini-AI 🎭

A privacy-first FastAPI chatbot assistant powered by GPT-4o-mini that delivers intelligent conversations without compromising user data or identity.

## Features ✨

- **Privacy-First**: No data logging or storage of personal information
- **Fast & Efficient**: Built with FastAPI for high performance
- **Rate Limited**: Built-in protection against abuse
- **Modern UI**: Clean, responsive web interface
- **Easy Deployment**: Docker-ready with dev container support
- **Comprehensive Testing**: Full test suite with coverage reporting

## Quick Start 🚀

### Prerequisites

- Python 3.11+
- OpenAI API key
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Wh0Dini-AI
   ```

2. **Set up the environment**

   ```bash
   # Option 1: Use the setup script
   chmod +x setup.sh
   ./setup.sh

   # Option 2: Use Makefile
   make setup

   # Option 3: Manual setup
   pip install -r requirements.txt
   cp .env.example .env
   ```

3. **Configure your API key**

   Edit `.env` file and add your OpenAI API key:

   ```env
   OPENAI_API_KEY=your_actual_api_key_here
   ```

4. **Run the application**

   ```bash
   # Option 1: Direct Python
   python main.py

   # Option 2: Using Makefile
   make run

   # Option 3: Using uvicorn directly
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Visit the application**
   Open your browser and go to: <http://localhost:8000>

## Development 🛠️

### Available Commands

Use the Makefile for common development tasks:

```bash
make help          # Show all available commands
make install       # Install dependencies
make dev           # Install development dependencies
make run           # Start the server
make test          # Run tests with coverage
make format        # Format code with black and isort
make lint          # Run linting checks
make type-check    # Run mypy type checking
make clean         # Clean up cache files
make check         # Run all checks (format, lint, type-check, test)
```

### Project Structure

```
Wh0Dini-AI/
├── main.py                 # Application entry point
├── Wh0Dini_AI_main.py     # Core FastAPI application
├── static/                 # Static web files
│   ├── index.html
│   ├── script.js
│   └── style.css
├── tests/                  # Test files
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── .env.example           # Environment variables template
├── pyproject.toml         # Python project configuration
├── Makefile              # Development commands
└── setup.sh              # Setup script
```

### Testing

Run tests with different options:

```bash
# Run all tests with coverage
make test

# Run quick tests without coverage
make test-quick

# Run specific test file
pytest test_api.py -v

# Run tests with live output
pytest -v -s
```

### Code Quality

The project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pre-commit**: Git hooks for quality checks

Set up pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

## Configuration ⚙️

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `MODEL_NAME` | OpenAI model to use | `gpt-4o-mini` |
| `MAX_TOKENS` | Maximum tokens per response | `500` |
| `RATE_LIMIT` | Rate limit per minute | `10/minute` |
| `API_HOST` | Server host | `0.0.0.0` |
| `API_PORT` | Server port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |

### API Endpoints

- `GET /` - Web interface
- `POST /chat` - Chat with the AI
- `POST /chat/stream` - Streaming chat response
- `GET /health` - Health check endpoint

## Deployment 🚢

### Using Docker

```bash
# Build the image
docker build -t wh0dini-ai .

# Run the container
docker run -p 8000:8000 --env-file .env wh0dini-ai
```

### Using Dev Container

The project includes a dev container configuration for VS Code:

1. Open in VS Code
2. Install the "Dev Containers" extension
3. Press `Ctrl+Shift+P` and select "Dev Containers: Reopen in Container"

## Contributing 🤝

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run quality checks (`make check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support 💬

If you encounter any issues or have questions, please open an issue on GitHub.
