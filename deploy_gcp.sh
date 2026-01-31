# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================
$PROJECT_ID = "rian-sentiment-api"
$SERVICE_NAME = "sentiment-api"
$REGION = "us-central1"

# Hardware
$MEMORY = "2Gi"
$CPU = "1"
$TIMEOUT = "180"

# ==============================================================================
# ENV VARS (runtime)
# ==============================================================================
# modelo já dentro da imagem em /app/models (via Dockerfile: COPY models/ ./models/)
$MODEL_LOCAL_PATH = "/app/models"

# dashboard
$DASH_API_KEY = "9d51j3fyw0s3"

# firestore (opcional, mas recomendado explicitar)
$FIRESTORE_ENABLED = "true"
$FIRESTORE_COLLECTION = "inferences"

# ==============================================================================
# SCRIPT DE DEPLOY (Windows PowerShell)
# ==============================================================================
Write-Host "🚀 Deploy: $SERVICE_NAME"
Write-Host "📍 Projeto: $PROJECT_ID | Região: $REGION | 🧠 Memória: $MEMORY | ⏱️ Timeout: ${TIMEOUT}s"

# 1) Projeto certo
gcloud config set project $PROJECT_ID

# 2) APIs necessárias (Run + Build + Firestore + Storage)
gcloud services enable run.googleapis.com cloudbuild.googleapis.com firestore.googleapis.com storage.googleapis.com

# 3) Deploy
gcloud run deploy $SERVICE_NAME `
  --source . `
  --region $REGION `
  --platform managed `
  --memory $MEMORY `
  --cpu $CPU `
  --timeout $TIMEOUT `
  --min-instances 0 `
  --max-instances 1 `
  --concurrency 80 `
  --allow-unauthenticated `
  --set-env-vars "MODEL_LOCAL_PATH=$MODEL_LOCAL_PATH,DASH_API_KEY=$DASH_API_KEY,FIRESTORE_ENABLED=$FIRESTORE_ENABLED,FIRESTORE_COLLECTION=$FIRESTORE_COLLECTION"

Write-Host "✅ Deploy concluído!"
Write-Host "🌍 URL:"
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"
