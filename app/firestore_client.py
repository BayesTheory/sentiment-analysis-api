import os
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
