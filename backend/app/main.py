
import logging
import time
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Application lifecycle
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s", settings.APP_NAME)

    # Database connectivity is checked by /health/ready.
    # Do not expose credentials or secrets in logs.
    yield

    engine.dispose()
    logger.info("Application shutdown complete")


# --------------------------------------------------
# Create FastAPI application
# --------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    description="AI Medical Assistant and Clinical Intelligence API",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)


# --------------------------------------------------
# CORS middleware
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)


# --------------------------------------------------
# Request middleware
# --------------------------------------------------

@app.middleware("http")
async def request_context_middleware(
    request: Request,
    call_next,
):
    request_id = str(uuid4())
    request.state.request_id = request_id

    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled request error | request_id=%s | path=%s",
            request_id,
            request.url.path,
        )
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000

    response.headers["X-Request-ID"] = request_id

    # Do not log request bodies, query values, or patient information.
    logger.info(
        "HTTP request | method=%s | path=%s | status=%s | "
        "duration_ms=%.2f | request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id,
    )

    return response


# --------------------------------------------------
# Centralized error handling
# --------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    request_id = getattr(request.state, "request_id", "unknown")

    # Preserve HTTP status codes, headers, and expected API errors.
    detail = exc.detail

    if not isinstance(detail, (str, dict, list, int, float, bool)):
        detail = "Request could not be completed."

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": detail,
            "request_id": request_id,
        },
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    request_id = getattr(request.state, "request_id", "unknown")

    # Return locations and error types, not submitted input values.
    errors = [
        {
            "location": list(error.get("loc", ())),
            "type": error.get("type", "validation_error"),
            "message": error.get("msg", "Invalid value"),
        }
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={
            "error": "Request validation failed.",
            "details": errors,
            "request_id": request_id,
        },
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
):
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        "Unexpected application error | request_id=%s",
        request_id,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected server error occurred.",
            "request_id": request_id,
        },
    )


# --------------------------------------------------
# Register API routers
# --------------------------------------------------

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


# --------------------------------------------------
# Root and health endpoints
# --------------------------------------------------

@app.get("/", tags=["System"])
def home():
    return {
        "message": "AI Medical Assistant API is running",
        "version": app.version,
        "docs": "/docs",
    }


@app.get("/health/live", tags=["Health"])
def liveness_check():
    """Confirms that the API process is responding."""
    return {
        "status": "alive",
    }


@app.get("/health/ready", tags=["Health"])
def readiness_check():
    """Checks whether the application can reach PostgreSQL."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "database": "connected",
        }

    except Exception:
        logger.exception("Database readiness check failed")

        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "database": "unavailable",
            },
        )
