# Changelog

All notable changes to Wh0Dini-AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-21

### Added
- Initial release of Wh0Dini-AI
- FastAPI-based chatbot with OpenAI GPT-4o-mini integration
- Privacy-first architecture with no user data logging
- Rate limiting and abuse protection
- Modern web UI with responsive design
- Docker containerization support
- Comprehensive test suite
- Development tooling (black, isort, flake8, mypy, pre-commit)
- Makefile for development automation
- Environment-based configuration
- Streaming and standard chat endpoints
- Health check endpoint
- Static file serving for web interface

### Package Structure
- Created proper Python package structure with `wh0dini_ai` package
- Added package metadata in `pyproject.toml` for Python packaging
- Configured entry points for command-line usage
- Added version management system

### Documentation
- Comprehensive README with setup and usage instructions
- MIT License
- Setup scripts and development guides
- VS Code Dev Container configuration

### Dependencies
- FastAPI for web framework
- OpenAI Python client for AI integration
- Uvicorn for ASGI server
- Pydantic for data validation
- Structlog for logging
- SlowAPI for rate limiting
- TikToken for token counting
- And other supporting libraries
