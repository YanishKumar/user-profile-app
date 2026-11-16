"""FastAPI application bootstrap."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from src.models.base import init_db
from src.api.routes import router as profile_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: initialize DB on startup."""
    init_db()
    # Ensure static and upload directories exist
    os.makedirs("static/avatars", exist_ok=True)
    os.makedirs("uploads/avatars", exist_ok=True)
    yield


app = FastAPI(
    title="User Profile & Avatar API",
    description="Endpoints for user profile management, avatar uploads, and public profile views.",
    version="1.0.0",
    lifespan=lifespan,
)

# Mount static default avatars and uploaded media
os.makedirs("static/avatars", exist_ok=True)
os.makedirs("uploads/avatars", exist_ok=True)
app.mount("/static/avatars", StaticFiles(directory="static/avatars"), name="static_avatars")
app.mount("/media/avatars", StaticFiles(directory="uploads/avatars"), name="media_avatars")

# Include profile routes
app.include_router(profile_router)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Ensure HTTPExceptions formatted with dict details match OpenAPI ErrorResponse."""
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "http_error", "message": str(exc.detail)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Format Pydantic validation errors according to OpenAPI ErrorResponse specification."""
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    msg = first_error.get("msg", "Invalid request payload")
    loc = ".".join(str(x) for x in first_error.get("loc", []))
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "validation_error",
            "message": f"Validation failed at '{loc}': {msg}",
            "details": {"errors": errors},
        },
    )


@app.get("/health", tags=["system"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "user-profile-app"}
