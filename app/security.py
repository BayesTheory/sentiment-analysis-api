import os
import secrets
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

from app.firestore_client import consume_ui_quota

# Header padrão para API Key [web:1]
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def _require_env_key(env_name: str) -> str:
    val = (os.getenv(env_name) or "").strip()
    if not val:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server misconfigured: missing {env_name}",
        )
    return val


def _require_header_key(api_key: str | None) -> str:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "APIKey"},
        )
    return api_key.strip()


def _timing_safe_equal(a: str, b: str) -> bool:
    return secrets.compare_digest(a, b)


# Protege /dash e /inferences com DASH_API_KEY
def require_api_key(api_key: str | None = Depends(api_key_header)) -> bool:
    expected = _require_env_key("DASH_API_KEY")
    provided = _require_header_key(api_key)

    if not _timing_safe_equal(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "APIKey"},
        )
    return True


# Alias (compat com código antigo que importava requireapikey)
requireapikey = require_api_key


# Protege /predict (API “puro”) com API_KEY
def require_predict_api_key(api_key: str | None = Depends(api_key_header)) -> bool:
    expected = _require_env_key("API_KEY")
    provided = _require_header_key(api_key)

    if not _timing_safe_equal(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "APIKey"},
        )
    return True


def _get_client_ip(request: Request) -> str:
    # Cloud Run costuma enviar X-Forwarded-For; pega o primeiro IP (cliente).
    xff = request.headers.get("x-forwarded-for") or request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


# Aplica quota/bloqueio do /ui/predict
def enforce_ui_quota(request: Request) -> bool:
    enabled = (os.getenv("UI_QUOTA_ENABLED", "true").strip().lower() == "true")
    if not enabled:
        return True

    ip = _get_client_ip(request)
    allowed, reason = consume_ui_quota(ip=ip, now=datetime.now(timezone.utc))

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=reason or "Rate limit",
        )
    return True
