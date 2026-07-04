"""Asahi chatbot endpoint — POST /chat (see docs/CHATBOT.md).

Thin route (per ARCHITECTURE.md §5.2): validate, rate-limit, delegate to the
service. The GitHub Models call + system prompt live in services/asahi_chat.py.

Rate limiting is a minimal in-memory fixed window — enough to protect the free
GitHub Models quota for a single-instance prototype. For multi-instance prod,
swap in slowapi/Redis (noted in docs/CHATBOT.md).
"""

import time

from fastapi import APIRouter, Header, Request

from app.schemas.chat import (
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    FreeChatRequest,
    FreeChatResponse,
)
from app.services import asahi_chat, chat_memory
from app.utils.errors import ApiException, CHAT_RATE_LIMITED

router = APIRouter(prefix="/chat", tags=["chat"])

_RATE_LIMIT = 12          # requests per window per client
_RATE_WINDOW_S = 60.0
_hits: dict[str, list[float]] = {}


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _enforce_rate_limit(client_ip: str) -> None:
    now = time.monotonic()
    window_start = now - _RATE_WINDOW_S
    recent = [t for t in _hits.get(client_ip, []) if t > window_start]
    if len(recent) >= _RATE_LIMIT:
        raise ApiException(
            429, CHAT_RATE_LIMITED, "Sabar ya, kebanyakan ngobrol. Coba lagi sebentar."
        )
    recent.append(now)
    _hits[client_ip] = recent


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, http_request: Request) -> ChatResponse:
    _enforce_rate_limit(_client_ip(http_request))
    reply = asahi_chat.generate_reply(request)
    return ChatResponse(reply=reply)


@router.post("/ask", response_model=FreeChatResponse)
def chat_ask(
    request: FreeChatRequest,
    http_request: Request,
    x_device_id: str | None = Header(default=None),
) -> FreeChatResponse:
    """Free-text chat with Asahi (home page). Guardrails live in the system prompt.
    Persists the turn (best-effort) so Asahi remembers it next session."""
    _enforce_rate_limit(_client_ip(http_request))
    reply = asahi_chat.generate_free_reply(request, x_device_id)
    chat_memory.save_turn(x_device_id, request.message, reply)
    return FreeChatResponse(reply=reply)


@router.get("/history", response_model=ChatHistoryResponse)
def chat_history(x_device_id: str | None = Header(default=None)) -> ChatHistoryResponse:
    """Recent free-chat turns for this device, so the widget can restore them."""
    return ChatHistoryResponse(messages=chat_memory.load_recent(x_device_id))
