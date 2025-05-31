#!/bin/bash
# Wh0Dini-AI Environment Setup Script

echo "🚀 Setting up Wh0Dini-AI development environment..."

# Check if .env exists, if not copy from example
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual OpenAI API key!"
else
    echo "✅ .env file already exists"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🔧 Installing development tools..."
pip install black isort flake8 mypy pre-commit

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p static logs tests

# Set up pre-commit hooks (optional)
if command -v pre-commit &> /dev/null; then
    echo "🪝 Setting up pre-commit hooks..."
    pre-commit install
fi

# Run basic tests to verify setup
echo "🧪 Running basic tests..."
if python -c "import fastapi, uvicorn, openai; print('✅ All core dependencies imported successfully')"; then
    echo "✅ Environment setup completed successfully!"
    echo ""
    echo "🎯 Next steps:"
    echo "1. Edit .env file with your OpenAI API key"
    echo "2. Run 'python main.py' to start the server"
    echo "3. Visit http://localhost:8000 to test the application"
else
    echo "❌ Some dependencies failed to import. Please check the installation."
    exit 1
fi
