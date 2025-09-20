#!/bin/bash

# Pfadi AI Assistent - Development Setup Script
# This script helps with initial development setup

set -e

echo "🏕️ Pfadi AI Assistent - Development Setup"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check if .env exists, if not, copy from example
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your Azure credentials."
else
    echo "✅ .env file already exists"
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Docker
if command_exists docker; then
    echo "✅ Docker is installed"
else
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
    echo "✅ Docker Compose is available"
else
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Optional: Check Node.js for local development
if command_exists node; then
    echo "✅ Node.js is installed ($(node --version))"
else
    echo "⚠️  Node.js not found. Install it for local frontend development."
fi

# Optional: Check Python for local development  
if command_exists python3; then
    echo "✅ Python 3 is installed ($(python3 --version))"
else
    echo "⚠️  Python 3 not found. Install it for local backend development."
fi

echo ""
echo "🚀 Setup complete! Available commands:"
echo ""
echo "Development with Docker:"
echo "  docker-compose up --build    # Start all services"
echo "  docker-compose up backend    # Start only backend + Redis"
echo "  docker-compose up frontend   # Start only frontend"
echo "  docker-compose down          # Stop all services"
echo ""
echo "Local Development:"
echo "  Backend:"
echo "    cd backend"
echo "    python -m venv venv"
echo "    source venv/bin/activate"
echo "    pip install -r requirements.txt"
echo "    uvicorn app.main:app --reload"
echo ""
echo "  Frontend:"
echo "    cd frontend"
echo "    npm install"
echo "    npm run dev"
echo ""
echo "URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000/docs"
echo "  Health Check: http://localhost:8000/health"
echo ""
echo "🔧 Don't forget to configure your Azure credentials in .env!"
echo "Gut Pfad! 🔥"