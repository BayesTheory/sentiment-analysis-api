import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from google.cloud import firestore

from app.firestore_client import get_db
from app.security import require_api_key

router = APIRouter(tags=["Dashboard"])


def _format_ts(ts) -> str:
    if ts is None:
        return "-"
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return str(ts)


@router.get("/dash")
async def dash_page():
    # HTML estático do dashboard
    return FileResponse("static/dash.html", media_type="text/html")


@router.get("/inferences", dependencies=[Depends(require_api_key)])
async def list_inferences(limit: int = 50):
    # limita o range aceitável
    limit = max(1, min(limit, 200))

    collection = os.getenv("FIRESTORE_COLLECTION", "inferences").strip() or "inferences"

    db = get_db()
    query = (
        db.collection(collection)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
    )

    items = []
    for doc in query.stream():
        d = doc.to_dict() or {}

        score = d.get("score")
        time_ms = d.get("inference_time_ms")

        # dado antigo pode não estar arredondado
        try:
            if isinstance(score, (int, float)):
                score = round(float(score), 5)
            if isinstance(time_ms, (int, float)):
                time_ms = round(float(time_ms), 2)
        except Exception:
            pass

        items.append(
            {
                "id": d.get("id", doc.id),
                "created_at": _format_ts(d.get("created_at")),
                "lang": d.get("lang"),
                "label": d.get("label"),
                "score": score,
                "inference_time_ms": time_ms,
                "model_version": d.get("model_version"),
                "text": d.get("text"),
            }
        )

    return {"count": len(items), "items": items}
