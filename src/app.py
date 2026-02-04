import logging
from contextlib import asynccontextmanager
from logging.config import dictConfig

from fastapi import (
    FastAPI,
    Request,
    status,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse

from .api import router
from .clickhouse import (
    close_clickhouse_client,
    init_clickhouse_client,
)
from .config import get_config
from .exceptions import HTTPException
from .logging import get_logging_config

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_clickhouse_client()
    yield
    await close_clickhouse_client()


def patch_openapi_schema(app: FastAPI) -> None:
    openapi_schema = app.openapi()
    for path in openapi_schema["paths"].values():
        for method in path.values():
            if (
                isinstance(method, dict)
                and "responses" in method
                and "422" in method["responses"]
            ):
                method["responses"].pop("422")
    app.openapi_schema = openapi_schema


def validation_exception_handler(_: Request, exc: RequestValidationError) -> ORJSONResponse:
    errors: dict[str, str] = {str(error["loc"][-1]): error["msg"] for error in exc.errors()}
    return ORJSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Invalid input data",
            "errors": errors,
        },
    )


def http_exception_handler(_: Request, exc: HTTPException) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


def init_app():
    config = get_config()
    dictConfig(get_logging_config(config.debug))
    app = FastAPI(
        debug=config.debug,
        lifespan=lifespan,
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )
    app.include_router(router)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    patch_openapi_schema(app)
    return app
