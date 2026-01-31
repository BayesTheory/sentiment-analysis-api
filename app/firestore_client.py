import os
import hashlib
from datetime import datetime, timedelta, timezone

from google.cloud import firestore

from app.logger import get_logger

logger = get_logger(__name__)

_db = None


def get_db():
    global _db
    if _db is None:
        project_id = os.getenv("FIRESTORE_PROJECT_ID", "").strip() or None
        _db = firestore.Client(project=project_id)
    return _db


def save_inference(doc_id: str, data: dict) -> bool:
    enabled = os.getenv("FIRESTORE_ENABLED", "true").strip().lower() == "true"
    if not enabled:
        return False

    if not doc_id or not str(doc_id).strip():
        logger.error("doc_id vazio em save_inference")
        return False

    collection = os.getenv("FIRESTORE_COLLECTION", "inferences").strip() or "inferences"

    try:
        db = get_db()
        db.collection(collection).document(str(doc_id)).set(data)
        return True
    except Exception as e:
        logger.error(f"Falha ao salvar no Firestore: {e}", exc_info=True)
        return False


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        return int(raw)
    except Exception:
        return default


def _ip_hash(ip: str) -> str:
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()


def consume_ui_quota(ip: str, now: datetime | None = None) -> tuple[bool, str]:
    """
    Aplica quota/bloqueio por IP para o endpoint /ui/predict.

    Regras (via env vars):
    - UI_DAILY_LIMIT (default 10)
    - UI_COOLDOWN_DAYS (default 30)
    - UI_COOLDOWN_DAILY_LIMIT (default 1)
    - UI_BURST_MIN_INTERVAL_MS (default 800)  -> se reqs muito rápidas, bloqueia
    - UI_BURST_BLOCK_SECONDS (default 3600)   -> 1h de block por burst
    """
    enabled = os.getenv("FIRESTORE_ENABLED", "true").strip().lower() == "true"
    if not enabled:
        # Se Firestore desligado, não dá pra contar quota; PoC: deixa passar.
        logger.warning("FIRESTORE_ENABLED=false: UI quota não está sendo aplicada.")
        return True, ""

    if now is None:
        now = datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    collection = os.getenv("UI_QUOTA_COLLECTION", "ui_quota").strip() or "ui_quota"

    daily_limit = _int_env("UI_DAILY_LIMIT", 10)
    cooldown_days = _int_env("UI_COOLDOWN_DAYS", 30)
    cooldown_daily_limit = _int_env("UI_COOLDOWN_DAILY_LIMIT", 1)

    burst_min_interval_ms = _int_env("UI_BURST_MIN_INTERVAL_MS", 800)
    burst_block_seconds = _int_env("UI_BURST_BLOCK_SECONDS", 3600)

    ip = (ip or "").strip() or "unknown"
    doc_id = _ip_hash(ip)

    db = get_db()
    doc_ref = db.collection(collection).document(doc_id)
    txn = db.transaction()

    @firestore.transactional
    def _txn_consume(transaction):
        snap = doc_ref.get(transaction=transaction)
        data = snap.to_dict() if snap.exists else {}

        today = now.date().isoformat()

        # Fields
        stored_day = data.get("day")
        count_today = int(data.get("count_today") or 0)

        cooldown_until = data.get("cooldown_until")  # datetime | None
        cooldown_day = data.get("cooldown_day")
        cooldown_count_today = int(data.get("cooldown_count_today") or 0)

        last_request_at = data.get("last_request_at")  # datetime | None
        burst_block_until = data.get("burst_block_until")  # datetime | None

        # Se mudou o dia, zera contadores diários
        if stored_day != today:
            stored_day = today
            count_today = 0

        # Se tá bloqueado por burst
        if isinstance(burst_block_until, datetime):
            if burst_block_until.tzinfo is None:
                burst_block_until = burst_block_until.replace(tzinfo=timezone.utc)
            if now < burst_block_until:
                remaining = int((burst_block_until - now).total_seconds())
                return False, f"IP temporariamente bloqueado (burst). Tente em {remaining}s."

        # Detecta burst (muito rápido) e bloqueia na hora
        if isinstance(last_request_at, datetime):
            if last_request_at.tzinfo is None:
                last_request_at = last_request_at.replace(tzinfo=timezone.utc)
            delta_ms = (now - last_request_at).total_seconds() * 1000.0
            if delta_ms >= 0 and delta_ms < burst_min_interval_ms:
                new_block_until = now + timedelta(seconds=burst_block_seconds)
                transaction.set(
                    doc_ref,
                    {
                        "ip_hash": doc_id,
                        "day": stored_day,
                        "count_today": count_today,
                        "burst_block_until": new_block_until,
                        "last_request_at": now,
                        "updated_at": firestore.SERVER_TIMESTAMP,
                        **({} if snap.exists else {"created_at": firestore.SERVER_TIMESTAMP}),
                    },
                    merge=True,
                )
                return False, "Muitas requisições muito rápidas. IP bloqueado temporariamente."

        # Em cooldown?
        in_cooldown = False
        if isinstance(cooldown_until, datetime):
            if cooldown_until.tzinfo is None:
                cooldown_until = cooldown_until.replace(tzinfo=timezone.utc)
            in_cooldown = now < cooldown_until

        # Se cooldown expirou, limpa estado
        if not in_cooldown and cooldown_until is not None:
            cooldown_until = None
            cooldown_day = None
            cooldown_count_today = 0

        # Se está em cooldown, aplica limite diário menor
        if in_cooldown:
            if cooldown_day != today:
                cooldown_day = today
                cooldown_count_today = 0

            if cooldown_count_today >= cooldown_daily_limit:
                return False, "Em cooldown: limite diário atingido. Tente amanhã."

            cooldown_count_today += 1

            transaction.set(
                doc_ref,
                {
                    "ip_hash": doc_id,
                    "day": stored_day,
                    "count_today": count_today,
                    "cooldown_until": cooldown_until,
                    "cooldown_day": cooldown_day,
                    "cooldown_count_today": cooldown_count_today,
                    "last_request_at": now,
                    "updated_at": firestore.SERVER_TIMESTAMP,
                    **({} if snap.exists else {"created_at": firestore.SERVER_TIMESTAMP}),
                },
                merge=True,
            )
            return True, ""

        # Fora de cooldown: aplica limite normal
        if count_today >= daily_limit:
            new_cooldown_until = now + timedelta(days=cooldown_days)
            transaction.set(
                doc_ref,
                {
                    "ip_hash": doc_id,
                    "day": stored_day,
                    "count_today": count_today,
                    "cooldown_until": new_cooldown_until,
                    "cooldown_day": today,
                    "cooldown_count_today": 0,
                    "updated_at": firestore.SERVER_TIMESTAMP,
                    **({} if snap.exists else {"created_at": firestore.SERVER_TIMESTAMP}),
                },
                merge=True,
            )
            return False, "Limite diário atingido. Cooldown ativado."

        # Consome 1 do dia
        count_today += 1
        transaction.set(
            doc_ref,
            {
                "ip_hash": doc_id,
                "day": stored_day,
                "count_today": count_today,
                "cooldown_until": None,
                "cooldown_day": None,
                "cooldown_count_today": 0,
                "burst_block_until": None,
                "last_request_at": now,
                "updated_at": firestore.SERVER_TIMESTAMP,
                **({} if snap.exists else {"created_at": firestore.SERVER_TIMESTAMP}),
            },
            merge=True,
        )
        return True, ""

    try:
        return _txn_consume(txn)
    except Exception as e:
        logger.error(f"Falha ao aplicar UI quota no Firestore: {e}", exc_info=True)
        # Se deu erro no Firestore, pra PoC eu deixaria passar; se quiser fail-closed, mude pra False.
        return True, ""
