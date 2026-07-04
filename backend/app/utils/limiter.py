"""Rate limiter configuration (ROADMAP §3.4).

Uses X-Device-Id header as the key function instead of IP address.
Behind a reverse proxy (e.g. HF Space), all users share the same IP,
so IP-based limiting would act as a global cap. X-Device-Id is already
sent by the frontend on every request, making it a reliable per-user key.

Fallback: if X-Device-Id is missing, falls back to remote address so that
unauthenticated/headerless requests are still rate-limited (just globally).
"""

from starlette.requests import Request
from slowapi import Limiter


def _get_device_id_or_ip(request: Request) -> str:
    """Extract X-Device-Id from headers; fall back to client IP."""
    device_id = request.headers.get("x-device-id", "").strip()
    if device_id:
        return device_id
    # Respect X-Forwarded-For if present (common behind proxies)
    forwarded = request.headers.get("x-forwarded-for", "").strip()
    if forwarded:
        # Take the first (client) IP from the chain
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


limiter = Limiter(key_func=_get_device_id_or_ip)
