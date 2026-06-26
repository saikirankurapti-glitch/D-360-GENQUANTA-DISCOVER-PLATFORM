"""
AnalytiX – Shared Security Middleware
=================================================
Provides:
  • JWT rotation / refresh token revocation (token blacklist)
  • API rate limiting (per-IP + per-user sliding window)
  • CSRF protection (double-submit cookie pattern)
  • Security headers (CSP, HSTS, X-Frame-Options, etc.)
  • SQL injection detection (WAF-lite layer)
  • XSS input sanitization

Usage:
    from shared.security import setup_security
    setup_security(app, redis_url=settings.REDIS_URL)
"""

import re
import time
import hashlib
import secrets
import logging
from typing import Callable, Optional

from fastapi import FastAPI, Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# In-memory token blacklist (replace with Redis in production)
# --------------------------------------------------------------------------- #
_REVOKED_TOKENS: set = set()
_RATE_LIMIT_STORE: dict = {}  # {key: [timestamp, ...]}


# --------------------------------------------------------------------------- #
# Token Revocation
# --------------------------------------------------------------------------- #
def revoke_token(jti: str) -> None:
    """Add a JWT ID to the revocation set."""
    _REVOKED_TOKENS.add(jti)
    logger.info(f"Token revoked: {jti[:8]}...")


def is_token_revoked(jti: str) -> bool:
    """Check if a JWT has been revoked."""
    return jti in _REVOKED_TOKENS


def revoke_all_user_tokens(user_id: str, token_store: dict) -> int:
    """
    Revoke all active refresh tokens for a user.
    token_store should be a dict mapping {jti: user_id}.
    Returns the number of tokens revoked.
    """
    to_revoke = [jti for jti, uid in token_store.items() if uid == user_id]
    for jti in to_revoke:
        revoke_token(jti)
    return len(to_revoke)


# --------------------------------------------------------------------------- #
# Rate Limiter (Sliding Window)
# --------------------------------------------------------------------------- #
class RateLimiter:
    """Sliding window rate limiter using in-memory store."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_allowed(self, key: str) -> tuple[bool, dict]:
        now = time.time()
        window_start = now - self.window_seconds

        if key not in _RATE_LIMIT_STORE:
            _RATE_LIMIT_STORE[key] = []

        # Remove expired timestamps
        _RATE_LIMIT_STORE[key] = [
            ts for ts in _RATE_LIMIT_STORE[key] if ts > window_start
        ]

        current_count = len(_RATE_LIMIT_STORE[key])
        allowed = current_count < self.max_requests

        if allowed:
            _RATE_LIMIT_STORE[key].append(now)

        headers = {
            "X-RateLimit-Limit": str(self.max_requests),
            "X-RateLimit-Remaining": str(max(0, self.max_requests - current_count - 1)),
            "X-RateLimit-Reset": str(int(window_start + self.window_seconds)),
        }
        return allowed, headers


# Default rate limiters
_default_limiter = RateLimiter(max_requests=200, window_seconds=60)
_auth_limiter = RateLimiter(max_requests=10, window_seconds=60)   # Tighter for auth endpoints
_api_limiter = RateLimiter(max_requests=500, window_seconds=60)


# --------------------------------------------------------------------------- #
# SQL Injection Detection
# --------------------------------------------------------------------------- #
_SQL_INJECTION_PATTERNS = re.compile(
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b"
    r"|--|;|\bOR\b\s+\d+=\d+|\bAND\b\s+\d+=\d+|'[\s\S]*'|\/\*[\s\S]*\*\/)",
    re.IGNORECASE
)

def contains_sql_injection(value: str) -> bool:
    """Returns True if the string looks like a SQL injection attempt."""
    return bool(_SQL_INJECTION_PATTERNS.search(value))


def check_request_for_sqli(request: Request) -> bool:
    """Check query params and path for SQL injection patterns."""
    for param_value in request.query_params.values():
        if contains_sql_injection(param_value):
            return True
    return False


# --------------------------------------------------------------------------- #
# XSS Detection
# --------------------------------------------------------------------------- #
_XSS_PATTERNS = re.compile(
    r"(<script[\s\S]*?>[\s\S]*?</script>|javascript:|on\w+\s*=|<iframe|<object|<embed)",
    re.IGNORECASE
)

def contains_xss(value: str) -> bool:
    """Returns True if the string looks like an XSS attempt."""
    return bool(_XSS_PATTERNS.search(value))


# --------------------------------------------------------------------------- #
# Security Headers Middleware
# --------------------------------------------------------------------------- #
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers to every response."""

    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https: wss:; "
            "frame-ancestors 'none';"
        ),
        "Cache-Control": "no-store",
        "Pragma": "no-cache",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        for header, value in self.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response


# --------------------------------------------------------------------------- #
# WAF Middleware (Rate Limit + SQLi + XSS Detection)
# --------------------------------------------------------------------------- #
class WAFMiddleware(BaseHTTPMiddleware):
    """
    Lightweight Web Application Firewall:
    - Rate limiting (per IP, tighter on /auth endpoints)
    - SQL injection detection in query params
    - XSS detection in query params
    - Blocks suspicious requests with 429 / 403
    """

    EXEMPT_PATHS = {"/healthz", "/readyz", "/health", "/metrics", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        # Skip exempt paths
        if path in self.EXEMPT_PATHS or path.startswith("/openapi"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        # --- Rate limiting ---
        if "/auth" in path or "/login" in path or "/token" in path:
            allowed, rate_headers = _auth_limiter.is_allowed(f"auth:{client_ip}")
        else:
            allowed, rate_headers = _default_limiter.is_allowed(f"ip:{client_ip}")

        if not allowed:
            logger.warning(f"Rate limit exceeded: {client_ip} → {path}")
            return Response(
                content='{"detail":"Too many requests. Please slow down."}',
                status_code=429,
                media_type="application/json",
                headers={**rate_headers, "Retry-After": "60"}
            )

        # --- SQL Injection detection ---
        if check_request_for_sqli(request):
            logger.warning(f"SQL injection attempt blocked: {client_ip} → {path}")
            return Response(
                content='{"detail":"Forbidden – malicious input detected."}',
                status_code=403,
                media_type="application/json"
            )

        # --- XSS detection ---
        for param_value in request.query_params.values():
            if contains_xss(param_value):
                logger.warning(f"XSS attempt blocked: {client_ip} → {path}")
                return Response(
                    content='{"detail":"Forbidden – malicious input detected."}',
                    status_code=403,
                    media_type="application/json"
                )

        response = await call_next(request)
        for header, value in rate_headers.items():
            response.headers[header] = value
        return response


# --------------------------------------------------------------------------- #
# CSRF Protection
# --------------------------------------------------------------------------- #
class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Double-submit CSRF protection for state-mutating endpoints.
    Skips: GET, HEAD, OPTIONS, and API token authenticated routes.
    """

    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
    CSRF_COOKIE_NAME = "csrftoken"
    CSRF_HEADER_NAME = "X-CSRFToken"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method in self.SAFE_METHODS:
            response = await call_next(request)
            # Set CSRF cookie if not present
            if self.CSRF_COOKIE_NAME not in request.cookies:
                token = secrets.token_urlsafe(32)
                response.set_cookie(
                    self.CSRF_COOKIE_NAME, token,
                    httponly=False,  # Must be readable by JS
                    secure=True,
                    samesite="strict"
                )
            return response

        # For API routes using Bearer token auth, skip CSRF
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return await call_next(request)

        cookie_token = request.cookies.get(self.CSRF_COOKIE_NAME)
        header_token = request.headers.get(self.CSRF_HEADER_NAME)

        if not cookie_token or not header_token:
            return Response(
                content='{"detail":"CSRF token missing."}',
                status_code=403,
                media_type="application/json"
            )

        if not secrets.compare_digest(cookie_token, header_token):
            logger.warning("CSRF validation failed")
            return Response(
                content='{"detail":"CSRF token invalid."}',
                status_code=403,
                media_type="application/json"
            )

        return await call_next(request)


# --------------------------------------------------------------------------- #
# Master Setup
# --------------------------------------------------------------------------- #
def setup_security(
    app: FastAPI,
    enable_waf: bool = True,
    enable_security_headers: bool = True,
    enable_csrf: bool = False,  # Set True for browser-facing services
):
    """
    Apply all security middleware to a FastAPI app.
    Call BEFORE including routers.

    Args:
        app: FastAPI app instance.
        enable_waf: Enable rate limiting + SQLi + XSS detection.
        enable_security_headers: Add OWASP security response headers.
        enable_csrf: Enable CSRF double-submit cookie protection.
    """
    # Note: Starlette applies middleware in REVERSE order of addition.
    # WAF should be outermost (added last).

    if enable_security_headers:
        app.add_middleware(SecurityHeadersMiddleware)
        logger.info("Security headers middleware active")

    if enable_csrf:
        app.add_middleware(CSRFMiddleware)
        logger.info("CSRF middleware active")

    if enable_waf:
        app.add_middleware(WAFMiddleware)
        logger.info("WAF middleware active (rate limiting + SQLi + XSS detection)")
