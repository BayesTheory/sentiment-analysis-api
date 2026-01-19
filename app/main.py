from contextlib import asynccontextmanager
import os
import uuid

from fastapi import FastAPI, HTTPException, status, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from google.cloud import firestore

from app.config import settings
from app.logger import get_logger
from app.models import PredictRequest, PredictResponse, HealthResponse
from app.utils import predict, is_model_loaded
from app.firestore_client import save_inference
from app.dash import router as dash_router

logger = get_logger(__name__)


def _cfg(*names: str, default=None):
    """Pega o primeiro atributo existente em settings."""
    for n in names:
        if hasattr(settings, n):
            return getattr(settings, n)
    return default


@asynccontextmanager
async def lifespan(app_: FastAPI):
    app_name = _cfg("app_name", "appname", default="App")
    app_version = _cfg("app_version", "appversion", default="0.0.0")
    logger.info(f"Iniciando {app_name} v{app_version}")
    yield
    logger.info("Encerrando aplicação")


app = FastAPI(
    title=_cfg("app_name", "appname", default="Sentiment API"),
    version=_cfg("app_version", "appversion", default="0.0.0"),
    description="API de análise de sentimentos - RoBERTa Twitter Model",
    lifespan=lifespan,
)

# Middleware (global)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(dash_router)


@app.get("/", tags=["Info"])
async def root():
    return {
        "name": _cfg("app_name", "appname"),
        "version": _cfg("app_version", "appversion"),
        "ui_url": "/main",
        "dash_url": "/dash",
        "docs_url": "/docs",
        "model": _cfg("model_name", "modelname"),
    }


@app.get("/main", tags=["UI"])
async def main():
    try:
        return FileResponse("static/index.html", media_type="text/html")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="UI não encontrada")


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    try:
        return HealthResponse(
            status="healthy",
            version=_cfg("app_version", "appversion"),
            model_ready=is_model_loaded(),
        )
    except Exception as e:
        logger.error(f"Erro no health check: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço indisponível",
        )


@app.post("/predict", response_model=PredictResponse, tags=["Prediction"])
async def predict_sentiment(
    payload: PredictRequest,
    background_tasks: BackgroundTasks,
):
    try:
        logger.info(f"Predição: text_len={len(payload.text)}, lang={payload.lang}")

        label, score, inference_time_ms = predict(payload.text)

        score = round(float(score), 5)
        inference_time_ms = round(float(inference_time_ms), 2)

        inference_id = str(uuid.uuid4())

        doc = {
            "id": inference_id,
            "text": payload.text,
            "lang": payload.lang,
            "label": label,
            "score": score,
            "inference_time_ms": inference_time_ms,
            "model_version": _cfg("app_version", "appversion"),
            "created_at": firestore.SERVER_TIMESTAMP,
        }

        background_tasks.add_task(save_inference, inference_id, doc)

        return PredictResponse(
            inference_id=inference_id,
            label=label,
            score=score,
            model_version=_cfg("app_version", "appversion"),
            inference_time_ms=inference_time_ms,
        )

    except ValueError as e:
        logger.warning(f"Validação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno",
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Exceção: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal Server Error"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=_cfg("host", default="0.0.0.0"),
        port=_cfg("port", default=8000),
        workers=_cfg("workers", default=1),
    )
