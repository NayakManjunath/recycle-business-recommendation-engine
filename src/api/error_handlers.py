"""
Centralized FastAPI error handling.

Module 8.2
----------
Provides consistent, safe API error responses without exposing
internal implementation details, file paths, or tracebacks.
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status


def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: Any | None = None,
) -> JSONResponse:
    """Build a consistent API error response."""

    payload: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
        }
    }

    if details is not None:
        payload["error"]["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=payload,
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Handle explicit FastAPI HTTP exceptions."""

    return _error_response(
        status_code=exc.status_code,
        code="HTTP_ERROR",
        message=str(exc.detail),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Handle request validation errors.

    FastAPI's 422 status semantics are preserved while the response
    is normalized into the project's API error structure.
    """

    return _error_response(
    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    code="VALIDATION_ERROR",
    message="Request validation failed.",
    details=exc.errors(),
)

async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handle unexpected application failures safely.

    Internal exception details are intentionally not returned to clients.
    """

    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected internal server error occurred.",
    )
    