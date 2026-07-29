from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    ApiError,
    RefreshTokenError,
    UnauthorizedError,
)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(RefreshTokenError)
    async def refresh_token_handler(
        request: Request,
        exc: RefreshTokenError,
    ):
        return JSONResponse(
            status_code=401,
            content={
                "error": "oauth_expired",
                "message": (
                    "Authorization has expired. "
                    "Please authorize GarminSupla again."
                ),
            },
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(
        request: Request,
        exc: UnauthorizedError,
    ):
        return JSONResponse(
            status_code=401,
            content={
                "error": "unauthorized",
                "message": "Unauthorized.",
            },
        )

    @app.exception_handler(ApiError)
    async def api_error_handler(
        request: Request,
        exc: ApiError,
    ):
        return JSONResponse(
            status_code=502,
            content={
                "error": "supla_api_error",
                "message": str(exc),
            },
        )
