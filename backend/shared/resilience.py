"""
AnalytiX – Shared Circuit Breaker + Retry Policies
=============================================================
Provides resilience patterns for inter-service HTTP calls:
  • CircuitBreaker – prevents cascade failures
  • RetryPolicy – exponential backoff with jitter
  • HealthAwareClient – wraps httpx with both patterns

Usage:
    from shared.resilience import CircuitBreaker, with_retry, HealthAwareClient
    
    cb = CircuitBreaker(service_name="query-service", failure_threshold=5)
    client = HealthAwareClient(base_url="http://localhost:8003", circuit_breaker=cb)
    response = await client.get("/api/v1/query/...")
"""

import asyncio
import time
import random
import logging
from enum import Enum
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Circuit Breaker States
# --------------------------------------------------------------------------- #
class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Blocking calls (too many failures)
    HALF_OPEN = "half_open" # Testing recovery


class CircuitBreakerOpenError(Exception):
    """Raised when a circuit breaker is OPEN."""
    pass


class CircuitBreaker:
    """
    Standard circuit breaker with CLOSED → OPEN → HALF_OPEN state machine.
    
    Args:
        service_name: Human-readable name for logging.
        failure_threshold: Consecutive failures before opening.
        success_threshold: Successes needed in HALF_OPEN to close.
        timeout_seconds: How long to wait in OPEN state before testing.
    """

    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: float = 30.0,
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self.timeout_seconds:
                logger.info(f"Circuit [{self.service_name}] → HALF_OPEN (testing)")
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
        return self._state

    def record_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                logger.info(f"Circuit [{self.service_name}] → CLOSED ✓")
                self._state = CircuitState.CLOSED
                self._failure_count = 0
        elif self.state == CircuitState.CLOSED:
            self._failure_count = 0  # Reset on success

    def record_failure(self):
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            logger.warning(f"Circuit [{self.service_name}] → OPEN (failed in HALF_OPEN)")
            self._state = CircuitState.OPEN
        elif self._failure_count >= self.failure_threshold:
            logger.error(
                f"Circuit [{self.service_name}] → OPEN "
                f"({self._failure_count} consecutive failures)"
            )
            self._state = CircuitState.OPEN

    def can_execute(self) -> bool:
        return self.state != CircuitState.OPEN

    def status(self) -> dict:
        return {
            "service": self.service_name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "last_failure": self._last_failure_time,
        }

    def __call__(self, func: Callable) -> Callable:
        """Use as a decorator: @circuit_breaker"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not self.can_execute():
                raise CircuitBreakerOpenError(
                    f"Circuit breaker OPEN for {self.service_name}"
                )
            try:
                result = await func(*args, **kwargs)
                self.record_success()
                return result
            except CircuitBreakerOpenError:
                raise
            except Exception as e:
                self.record_failure()
                raise
        return wrapper


# --------------------------------------------------------------------------- #
# Retry with Exponential Backoff + Jitter
# --------------------------------------------------------------------------- #
async def with_retry(
    func: Callable,
    *args,
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,),
    **kwargs
) -> Any:
    """
    Execute an async function with exponential backoff retries.

    Args:
        func: Async callable to retry.
        max_attempts: Maximum total attempts.
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay cap.
        jitter: Add random jitter to avoid thundering herd.
        retryable_exceptions: Only retry on these exception types.
    """
    last_exception = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except CircuitBreakerOpenError:
            raise  # Never retry when circuit is open
        except retryable_exceptions as e:
            last_exception = e
            if attempt == max_attempts:
                logger.error(f"All {max_attempts} attempts failed: {e}")
                raise

            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            if jitter:
                delay += random.uniform(0, delay * 0.1)

            logger.warning(f"Attempt {attempt}/{max_attempts} failed: {e} – retrying in {delay:.2f}s")
            await asyncio.sleep(delay)

    raise last_exception


# --------------------------------------------------------------------------- #
# Health-Aware HTTP Client
# --------------------------------------------------------------------------- #
try:
    import httpx

    class HealthAwareClient:
        """
        Async HTTP client with circuit breaker + retry baked in.
        Drop-in replacement for httpx.AsyncClient for inter-service calls.
        """

        def __init__(
            self,
            base_url: str,
            circuit_breaker: Optional[CircuitBreaker] = None,
            max_retries: int = 3,
            timeout: float = 10.0,
        ):
            self.base_url = base_url.rstrip("/")
            self.circuit_breaker = circuit_breaker
            self.max_retries = max_retries
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(timeout)
            )

        async def _call(self, method: str, path: str, **kwargs) -> httpx.Response:
            if self.circuit_breaker and not self.circuit_breaker.can_execute():
                raise CircuitBreakerOpenError(
                    f"Circuit open for {self.circuit_breaker.service_name}"
                )
            try:
                response = await getattr(self._client, method)(path, **kwargs)
                response.raise_for_status()
                if self.circuit_breaker:
                    self.circuit_breaker.record_success()
                return response
            except Exception as e:
                if self.circuit_breaker:
                    self.circuit_breaker.record_failure()
                raise

        async def get(self, path: str, **kwargs) -> httpx.Response:
            return await with_retry(self._call, "get", path, max_attempts=self.max_retries, **kwargs)

        async def post(self, path: str, **kwargs) -> httpx.Response:
            return await with_retry(self._call, "post", path, max_attempts=self.max_retries, **kwargs)

        async def put(self, path: str, **kwargs) -> httpx.Response:
            return await with_retry(self._call, "put", path, max_attempts=self.max_retries, **kwargs)

        async def delete(self, path: str, **kwargs) -> httpx.Response:
            return await with_retry(self._call, "delete", path, max_attempts=self.max_retries, **kwargs)

        async def close(self):
            await self._client.aclose()

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            await self.close()

except ImportError:
    logger.warning("httpx not installed – HealthAwareClient not available.")


# --------------------------------------------------------------------------- #
# Pre-configured Circuit Breakers for each service
# --------------------------------------------------------------------------- #
CIRCUIT_BREAKERS = {
    "auth-service": CircuitBreaker("auth-service", failure_threshold=5, timeout_seconds=30),
    "metadata-service": CircuitBreaker("metadata-service", failure_threshold=5, timeout_seconds=30),
    "query-service": CircuitBreaker("query-service", failure_threshold=5, timeout_seconds=30),
    "cheminformatics-service": CircuitBreaker("cheminformatics-service", failure_threshold=3, timeout_seconds=60),
    "connector-service": CircuitBreaker("connector-service", failure_threshold=5, timeout_seconds=30),
    "audit-service": CircuitBreaker("audit-service", failure_threshold=10, timeout_seconds=15),
    "lineage-service": CircuitBreaker("lineage-service", failure_threshold=5, timeout_seconds=30),
    "bioinformatics-service": CircuitBreaker("bioinformatics-service", failure_threshold=3, timeout_seconds=60),
    "workflow-service": CircuitBreaker("workflow-service", failure_threshold=5, timeout_seconds=30),
    "ai-service": CircuitBreaker("ai-service", failure_threshold=3, timeout_seconds=45),
}


def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """Get the pre-configured circuit breaker for a service."""
    return CIRCUIT_BREAKERS.get(service_name, CircuitBreaker(service_name))


def get_all_circuit_status() -> list[dict]:
    """Get status of all circuit breakers (for health dashboard)."""
    return [cb.status() for cb in CIRCUIT_BREAKERS.values()]
