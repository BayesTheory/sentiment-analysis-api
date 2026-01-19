import logging
import os
import time
from transformers import pipeline

logger = logging.getLogger(__name__)
_pipe = None

# Local: ./models (Windows)
# Cloud Run: /app/models (WORKDIR=/app + COPY models/ ./models/)
LOCAL_DIR = os.getenv("MODEL_LOCAL_PATH", "./models")


def load_model():
    global _pipe
    if _pipe is not None:
        return _pipe

    if (not os.path.exists(LOCAL_DIR)) or (len(os.listdir(LOCAL_DIR)) == 0):
        raise RuntimeError(
            f"Modelo não encontrado em {LOCAL_DIR}. "
            "Verifique se a pasta models/ contém (pytorch_model.bin, config.json, merges.txt, vocab.json...)."
        )

    logger.info(f"Carregando pipeline de {LOCAL_DIR}...")
    _pipe = pipeline(
        "sentiment-analysis",
        model=LOCAL_DIR,
        tokenizer=LOCAL_DIR,
        device=-1
    )
    logger.info("✅ Pipeline carregado!")
    return _pipe


def is_model_loaded():
    return _pipe is not None


def predict(text: str):
    pipe = load_model()
    start = time.time()
    output = pipe(text, truncation=True, max_length=512)[0]
    inference_time_ms = (time.time() - start) * 1000

    label_map = {"LABEL_0": "negative", "LABEL_1": "neutral", "LABEL_2": "positive"}
    label = label_map.get(output["label"], output["label"].lower())
    score = float(output["score"])

    return label, score, inference_time_ms
