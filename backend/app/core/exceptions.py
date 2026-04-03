from __future__ import annotations


class AppError(Exception):
    def __init__(self, message: str, *, status_code: int, error_code: str) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


class IngestionError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=400, error_code="INGESTION_ERROR")


class NotFoundError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class ExternalServiceError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=502, error_code="EXTERNAL_SERVICE_ERROR")
