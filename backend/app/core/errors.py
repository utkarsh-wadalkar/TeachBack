"""Application-level exceptions, mapped to HTTP responses in ``main.py``.

Services raise these instead of importing FastAPI, keeping business logic free of
web-framework concerns.
"""

from __future__ import annotations


class AppError(Exception):
    status_code = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409
