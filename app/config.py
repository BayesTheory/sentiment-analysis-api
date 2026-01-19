import os
from dotenv import load_dotenv

load_dotenv()

# Aplicação
APP_NAME = os.getenv("APP_NAME", "Sentiment Analysis API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Servidor
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8080))
WORKERS = int(os.getenv("WORKERS", 1))

# Modelo
MODEL_NAME = os.getenv("MODEL_NAME", "cardiffnlp/twitter-roberta-base-sentiment-latest")
MODEL_LOCAL_PATH = os.getenv("MODEL_LOCAL_PATH", "/tmp/sentiment-model")  # ✅ /tmp
MODEL_DEVICE = os.getenv("MODEL_DEVICE", "cpu")
USE_LOCAL_MODEL = os.getenv("USE_LOCAL_MODEL", "True").lower() == "true"

# Classe para acesso fácil
class Settings:
    app_name = APP_NAME
    app_version = APP_VERSION
    debug = DEBUG
    log_level = LOG_LEVEL
    host = HOST
    port = PORT
    workers = WORKERS
    model_name = MODEL_NAME
    model_local_path = MODEL_LOCAL_PATH
    model_device = MODEL_DEVICE
    use_local_model = USE_LOCAL_MODEL

settings = Settings()
