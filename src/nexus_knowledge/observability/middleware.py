"""FastAPI middleware providing request context and metrics."""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .context import pop_request_context, push_request_context
from .metrics import observe_api_error, observe_api_request

LOGGER = logging.getLogger("nexus_knowledge.api.middleware")


def _resolve_route(request: Request) -> str:
    route = request.scope.get("route")
    if route is None:
        return request.url.path
    return getattr(route, "path", request.url.path)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Populate logging/metrics context and propagate correlation identifiers."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("x-request-id") or f"req-{uuid.uuid4().hex}"
        correlation_header = request.headers.get("x-correlation-id")
        request_token, correlation_token = push_request_context(
            request_id,
            correlation_header,
        )
        span_id = f"span-{uuid.uuid4().hex[:12]}"
        start = time.perf_counter()

        LOGGER.info(
            "request.started",
            extra={
                "http_method": request.method,
                "http_path": request.url.path,
                "span_id": span_id,
                "source": "api",
            },
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            duration = time.perf_counter() - start
            route = _resolve_route(request)
            observe_api_error(request.method, route, exc.__class__.__name__)
            observe_api_request(request.method, route, 500, duration)
            LOGGER.exception(
                "request.failed",
                extra={
                    "http_method": request.method,
                    "http_path": route,
                    "span_id": span_id,
                    "duration_ms": duration * 1000,
                    "source": "api",
                },
            )
            raise
        else:
            duration = time.perf_counter() - start
            route = _resolve_route(request)
            status_code = response.status_code
            observe_api_request(request.method, route, status_code, duration)
            LOGGER.info(
                "request.completed",
                extra={
                    "http_method": request.method,
                    "http_path": route,
                    "status_code": status_code,
                    "span_id": span_id,
                    "duration_ms": duration * 1000,
                    "source": "api",
                },
            )
            response.headers["X-Request-ID"] = request_id
            response.headers.setdefault(
                "X-Correlation-ID",
                correlation_header or request_id,
            )
            return response
        finally:
            pop_request_context(request_token, correlation_token)


__all__ = ["RequestContextMiddleware"]
