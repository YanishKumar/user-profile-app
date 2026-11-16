# User Profile App

User Profile management system with avatar upload and bio, built with FastAPI, SQLAlchemy 2.0, Pydantic v2, and Pillow.

## Features
- **User Story 1 (P1 MVP)**: View and update biography & display name
- **User Story 2 (P2)**: Upload avatar with server-side validation and WebP normalization (256x256)
- **User Story 3 (P3)**: Public read-only profile view

## Setup & Running
```bash
# Create venv and install dependencies
uv venv
uv pip install -e ".[dev]"

# Run tests
pytest

# Start dev server
uvicorn src.main:app --reload
```
