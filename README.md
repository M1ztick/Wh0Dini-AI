# Wh0Dini-AI 🎭  
*A GPT-powered FastAPI chatbot with a privacy-first, white-box architecture.*

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/built%20with-FastAPI-009688.svg)

---

## Overview 🌐

**Wh0Dini-AI** is a fully transparent, privacy-first chatbot powered by OpenAI's GPT-4o-mini model and built using FastAPI. It’s designed to deliver intelligent conversations *without tracking, logging, or compromising user data*. The project is a direct expression of **Mistyk Media’s** core philosophy: *user-centric development that safeguards personal information rather than exploiting it*.

Both this project and Mistyk Media’s broader approach champion what we call a **"white-box" (or “clear-glass”) development strategy** — an open, honest methodology where *every line of code and configuration is public*, with nothing hidden behind proprietary walls.

---

## Features ✨

- 🔒 **Privacy-First** — No user data logging or behavioral tracking.
- ⚡ **FastAPI-Powered** — Lightning-fast backend with async support.
- 🧠 **GPT-4o-mini** — Uses OpenAI's blazing-fast lightweight model.
- 🔐 **Rate Limited** — Built-in abuse protection.
- 🖥️ **Modern UI** — Sleek, responsive front-end via static assets.
- 🐳 **Containerized** — Docker-ready with dev container config.
- 🧪 **Tested** — Comes with full test suite and coverage support.

---

## Quick Start 🚀

### Prerequisites

- Python 3.11+
- OpenAI API key
- Git

### Installation

```bash
git clone https://github.com/YOUR-USERNAME/Wh0Dini-AI.git
cd Wh0Dini-AI
```

#### Set Up the Environment

Choose one setup method:

```bash
# Setup script
chmod +x setup.sh && ./setup.sh

# OR with Makefile
make setup

# OR manually
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and insert your API key:

```env
OPENAI_API_KEY=your_actual_api_key_here
```

#### Run the App

```bash
# Option 1: Python
python main.py

# Option 2: Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Option 3: Makefile
make run
```

Open your browser: [http://localhost:8000](http://localhost:8000)

---

## Project Structure 🗂️

```
Wh0Dini-AI/
├── main.py                 # App entry point
├── Wh0Dini_AI_main.py     # Core FastAPI app logic
├── static/                 # HTML, CSS, JS assets
│   ├── index.html
│   ├── script.js
│   └── style.css
├── tests/                  # Test suite
├── requirements.txt        # Runtime deps
├── requirements-dev.txt    # Dev/test deps
├── .env.example            # Env var template
├── pyproject.toml          # Project config
├── Makefile                # Dev commands
└── setup.sh                # Setup script
```

---

## Environment Variables ⚙️

| Variable          | Description                  | Default         |
|------------------|------------------------------|-----------------|
| `OPENAI_API_KEY` | Your OpenAI key              | **Required**    |
| `MODEL_NAME`     | GPT model name               | `gpt-4o-mini`   |
| `MAX_TOKENS`     | Max tokens per reply         | `500`           |
| `RATE_LIMIT`     | Requests per minute          | `10/minute`     |
| `API_HOST`       | App host                     | `0.0.0.0`       |
| `API_PORT`       | App port                     | `8000`          |
| `LOG_LEVEL`      | Logging verbosity            | `INFO`          |

---

## API Endpoints 📡

| Endpoint         | Method | Description               |
|------------------|--------|---------------------------|
| `/`              | GET    | Web UI frontend           |
| `/chat`          | POST   | Standard chat response    |
| `/chat/stream`   | POST   | Streaming chat response   |
| `/health`        | GET    | Health check              |

---

## Docker Deployment 🐳

```bash
docker build -t wh0dini-ai .
docker run -p 8000:8000 --env-file .env wh0dini-ai
```

---

## Dev Containers (VS Code) 🧪

1. Open in VS Code  
2. Install the “Dev Containers” extension  
3. Press `Ctrl+Shift+P` → `Reopen in Container`  
4. Magic.

---

## Development & Testing 🛠️

Run commands via `make`:

```bash
make help        # List all tasks
make dev         # Dev dependencies
make run         # Start app
make test        # Run tests with coverage
make lint        # Lint with flake8
make format      # Format with black & isort
make type-check  # Check types with mypy
make check       # Run all checks
```

Run tests manually:

```bash
pytest -v
pytest tests/test_api.py
```

---

## Code Quality & Tooling ✅

- [`black`](https://github.com/psf/black) — Formatter  
- [`isort`](https://pycqa.github.io/isort/) — Import sorting  
- [`flake8`](https://flake8.pycqa.org) — Linter  
- [`mypy`](http://mypy-lang.org) — Type checker  
- [`pre-commit`](https://pre-commit.com) — Git hook runner

Set it up:

```bash
pip install pre-commit
pre-commit install
```

---

## Contributing 🤝

We welcome contributions!

1. Fork the repo  
2. `git checkout -b feature/amazing-idea`  
3. Make your changes  
4. `make check` to validate  
5. Push and open a PR

---

## License 📄

Licensed under the [MIT License](./LICENSE).

---

## Support 💬

Have a question, bug, or feature request?  
Open an issue on the [GitHub repo](https://github.com/YOUR-USERNAME/Wh0Dini-AI/issues).

---

## Screenshot 📸

> *(Insert an image or GIF of the app UI here to make devs go "Ooooh")*
