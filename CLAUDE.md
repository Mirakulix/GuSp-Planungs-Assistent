# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**GuSp-Planungs-und-Leitungs-Assistent** - A Python-based planning and management assistant for GuSp (likely Gruppe Späher/Scout Group). This is an early-stage project currently in initial setup phase.

## Development Setup

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (when they exist)
pip install -r requirements-dev.txt  # if this file exists
```

### Common Commands

Since this is an early-stage project, standard Python development commands apply:

```bash
# Install package in development mode (when setup.py exists)
pip install -e .

# Run the application (when main module exists)
python -m gusp_assistant
# or
python main.py

# Run tests (when test framework is set up)
python -m pytest
# or
python -m unittest discover

# Code formatting and linting (when tools are configured)
black .
isort .
flake8 .
mypy .
```

## Project Structure

The project is currently minimal with:
- `README.md` - Basic project title
- `requirements.txt` - Empty dependencies file
- `venv/` - Python virtual environment
- `LICENSE` - GPL v3 license

Expected future structure:
- `src/` or project root - Main application code
- `tests/` - Test files
- `docs/` - Documentation
- Configuration files (setup.py, pyproject.toml, etc.)

## Development Notes

- Project uses GPL v3 license
- Python 3.12 virtual environment is set up
- No source code or dependencies defined yet
- No testing framework or linting tools configured yet

## Next Steps for Development

When working on this project, consider:
1. Defining core dependencies in requirements.txt
2. Setting up project structure (src/ directory or package layout)
3. Creating main application entry point
4. Adding development dependencies (pytest, black, flake8, etc.)
5. Setting up CI/CD configuration
6. Adding more detailed README with usage instructions