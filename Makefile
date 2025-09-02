# TwistyVoice AI Assistant - Portfolio Demo Makefile
# 
# This Makefile provides a "runs in 5 minutes" experience for portfolio demos
# All targets work without external API dependencies using fake providers

.PHONY: help setup demo serve seed test lint type clean install-deps

# Default target
help:
	@echo "TwistyVoice AI Assistant - Portfolio Demo"
	@echo ""
	@echo "Available targets:"
	@echo "  setup     - Create virtual environment and install dependencies"
	@echo "  demo      - Run complete demo (seed + serve) - ONE COMMAND DEMO!"
	@echo "  serve     - Start FastAPI server on port 8000"
	@echo "  seed      - Populate database with sample data"
	@echo "  test      - Run pytest suite"
	@echo "  lint      - Run ruff linting"
	@echo "  type      - Run mypy type checking"
	@echo "  clean     - Clean up generated files"
	@echo ""
	@echo "Quick start: make demo"

# Setup virtual environment and install dependencies
setup:
	@echo "🚀 Setting up TwistyVoice development environment..."
	python -m venv venv
	@echo "📦 Installing dependencies..."
	./venv/Scripts/pip install --upgrade pip
	./venv/Scripts/pip install -r requirements.txt
	@echo "✅ Setup complete! Run 'make demo' to start the demo"

# Install dependencies (for CI or existing venv)
install-deps:
	@echo "📦 Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt

# One-command demo: seed database and start server
demo: seed
	@echo "🎬 Starting TwistyVoice demo server..."
	@echo "🌐 Server will be available at: http://localhost:8000"
	@echo "📚 API docs available at: http://localhost:8000/docs"
	@echo "🛑 Press Ctrl+C to stop the server"
	@echo ""
	python src/main.py

# Start FastAPI server
serve:
	@echo "🌐 Starting TwistyVoice server on port 8000..."
	@echo "📚 API docs: http://localhost:8000/docs"
	python src/main.py

# Populate database with sample data
seed:
	@echo "🌱 Seeding database with sample data..."
	python scripts/seed_db.py
	@echo "✅ Database seeded successfully!"

# Run test suite
test:
	@echo "🧪 Running test suite..."
	python -m pytest tests/ -v --tb=short

# Run linting
lint:
	@echo "🔍 Running ruff linting..."
	python -m ruff check src/ tests/ scripts/

# Run type checking
type:
	@echo "🔍 Running mypy type checking..."
	python -m mypy src/ --ignore-missing-imports

# Clean up generated files
clean:
	@echo "🧹 Cleaning up..."
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	rm -rf src/__pycache__ src/*/__pycache__ src/*/*/__pycache__
	rm -rf tests/__pycache__ tests/*/__pycache__
	rm -rf scripts/__pycache__
	rm -f twistyvoice.db
	rm -f logs/*.log
	@echo "✅ Cleanup complete!"

# Development workflow
dev: lint type test
	@echo "✅ All checks passed! Ready for development."
