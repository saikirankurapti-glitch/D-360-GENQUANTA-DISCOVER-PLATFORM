"""
AnalytiX – Shared Observability Middleware
======================================================
Drop-in FastAPI middleware that adds:
  • OpenTelemetry distributed tracing (OTLP export)
  • Prometheus metrics (request count, latency histograms)
  • Health / Readiness / Liveness probes
  • Structured JSON logging with trace correlation

Usage (in each service's main.py):
    from shared.observability import setup_observability, add_health_probes
    setup_observability(app, service_name="auth-service", service_port=8001)
    add_health_probes(app)
"""

import time
import logging
import os
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# --------------------------------------------------------------------------- #
# OpenTelemetry
# --------------------------------------------------------------------------- #
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    logging.warning("OpenTelemetry packages not installed – tracing disabled.")

# --------------------------------------------------------------------------- #
# Prometheus
# --------------------------------------------------------------------------- #
try:
    from prometheus_client import (
        Counter, Histogram, Gauge,
        generate_latest, CONTENT_TYPE_LATEST,
        CollectorRegistry, REGISTRY
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("prometheus_client not installed – metrics disabled.")

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Global Metrics (created once per process)
# --------------------------------------------------------------------------- #
_metrics_initialized = False
REQUEST_COUNT: Counter = None
REQUEST_LATENCY: Histogram = None
ACTIVE_REQUESTS: Gauge = None


def _init_metrics(service_name: str):
    global _metrics_initialized, REQUEST_COUNT, REQUEST_LATENCY, ACTIVE_REQUESTS
    if _metrics_initialized or not PROMETHEUS_AVAILABLE:
        return
    try:
        REQUEST_COUNT = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["service", "method", "endpoint", "status"]
        )
        REQUEST_LATENCY = Histogram(
            "http_request_duration_seconds",
            "HTTP request latency in seconds",
            ["service", "method", "endpoint"],
            buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        ACTIVE_REQUESTS = Gauge(
            "http_active_requests",
            "Currently active HTTP requests",
            ["service"]
        )
        _metrics_initialized = True
    except ValueError:
        # Metrics already registered (e.g., during testing)
        _metrics_initialized = True


# --------------------------------------------------------------------------- #
# Prometheus Middleware
# --------------------------------------------------------------------------- #
class PrometheusMiddleware(BaseHTTPMiddleware):
    """Records per-request metrics into Prometheus."""

    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.service_name = service_name
        _init_metrics(service_name)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not PROMETHEUS_AVAILABLE or not _metrics_initialized:
            return await call_next(request)

        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        endpoint = request.url.path
        method = request.method

        if ACTIVE_REQUESTS:
            ACTIVE_REQUESTS.labels(service=self.service_name).inc()

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            status = str(response.status_code)
        except Exception as exc:
            status = "500"
            raise exc
        finally:
            duration = time.perf_counter() - start_time
            if REQUEST_COUNT:
                REQUEST_COUNT.labels(
                    service=self.service_name,
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).inc()
            if REQUEST_LATENCY:
                REQUEST_LATENCY.labels(
                    service=self.service_name,
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
            if ACTIVE_REQUESTS:
                ACTIVE_REQUESTS.labels(service=self.service_name).dec()

        return response


# --------------------------------------------------------------------------- #
# OpenTelemetry Setup
# --------------------------------------------------------------------------- #
def _setup_tracing(service_name: str, service_version: str = "1.0.0"):
    """Configure OpenTelemetry tracing with OTLP gRPC export."""
    if not OTEL_AVAILABLE:
        return

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

    resource = Resource.create({
        "service.name": service_name,
        "service.version": service_version,
        "deployment.environment": os.getenv("ENVIRONMENT", "development"),
        "platform": "genquantaa-helix",
    })

    provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(provider)
    logger.info(f"OpenTelemetry tracing configured – exporting to {otlp_endpoint}")


# --------------------------------------------------------------------------- #
# Main Setup Function
# --------------------------------------------------------------------------- #
def setup_observability(
    app: FastAPI,
    service_name: str,
    service_port: int,
    service_version: str = "1.0.0",
    enable_tracing: bool = True,
    enable_metrics: bool = True,
):
    """
    Call this in each service's main.py BEFORE including routers.

    Args:
        app: The FastAPI application instance.
        service_name: Human-readable service name (e.g. "auth-service").
        service_port: The port this service runs on.
        service_version: Semantic version string.
        enable_tracing: Whether to configure OTLP tracing.
        enable_metrics: Whether to add Prometheus metrics middleware.
    """
    # 1. Setup tracing
    if enable_tracing and OTEL_AVAILABLE:
        _setup_tracing(service_name, service_version)
        FastAPIInstrumentor.instrument_app(app)
        HTTPXClientInstrumentor().instrument()
        logger.info(f"[{service_name}] OpenTelemetry FastAPI instrumentation active")

    # 2. Add Prometheus middleware
    if enable_metrics:
        app.add_middleware(PrometheusMiddleware, service_name=service_name)
        logger.info(f"[{service_name}] Prometheus metrics middleware active")

    # 3. Expose /metrics endpoint
    if enable_metrics and PROMETHEUS_AVAILABLE:
        @app.get("/metrics", include_in_schema=False)
        async def metrics_endpoint():
            return Response(
                content=generate_latest(REGISTRY),
                media_type=CONTENT_TYPE_LATEST
            )

    logger.info(f"[{service_name}] Observability setup complete (port={service_port})")


# --------------------------------------------------------------------------- #
# Health Probes
# --------------------------------------------------------------------------- #
def add_health_probes(
    app: FastAPI,
    db_check_fn: Callable = None,
    readiness_checks: dict = None,
):
    """
    Add Kubernetes-compatible health probe endpoints to the FastAPI app.

    Endpoints added:
      GET /healthz     – Liveness probe (service is alive)
      GET /readyz      – Readiness probe (service is ready to serve traffic)
      GET /health      – Combined health status (for legacy compatibility)

    Args:
        app: FastAPI app instance.
        db_check_fn: Optional callable that returns True if DB is reachable.
        readiness_checks: Dict of {name: callable} additional readiness checks.
    """
    _service_start = time.time()

    @app.get("/healthz", include_in_schema=False, tags=["Health"])
    async def liveness():
        """Kubernetes liveness probe – returns 200 if process is alive."""
        return {"status": "alive", "uptime_seconds": round(time.time() - _service_start, 2)}

    @app.get("/readyz", include_in_schema=False, tags=["Health"])
    async def readiness():
        """Kubernetes readiness probe – returns 200 if service can handle requests."""
        checks = {}
        all_ok = True

        # Database check
        if db_check_fn:
            try:
                db_ok = db_check_fn()
                checks["database"] = "ok" if db_ok else "degraded"
                if not db_ok:
                    all_ok = False
            except Exception as e:
                checks["database"] = f"error: {str(e)}"
                all_ok = False

        # Custom checks
        if readiness_checks:
            for name, check_fn in readiness_checks.items():
                try:
                    ok = check_fn()
                    checks[name] = "ok" if ok else "degraded"
                    if not ok:
                        all_ok = False
                except Exception as e:
                    checks[name] = f"error: {str(e)}"
                    all_ok = False

        status_code = 200 if all_ok else 503
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "ready" if all_ok else "not_ready",
                "checks": checks,
                "uptime_seconds": round(time.time() - _service_start, 2)
            }
        )

    @app.get("/health", include_in_schema=False, tags=["Health"])
    async def health():
        """Combined health endpoint for load balancers."""
        return {
            "status": "healthy",
            "uptime_seconds": round(time.time() - _service_start, 2)
        }
