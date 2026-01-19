# 📚 GUIA COMPLETO - Setup e Deploy (Passo a Passo)

## ⚡ Resumo Rápido

| Etapa | Tempo | O que fazer |
|-------|-------|-----------|
| 1. Setup local | 5 min | Clone + venv + pip install |
| 2. Download modelo | 5-10 min | Executar script de download |
| 3. Testar local | 5 min | Rodar FastAPI e chamar endpoints |
| 4. Build Docker | 10 min | Buildar imagem Docker |
| 5. Testar Docker | 5 min | Rodar container e testar |
| 6. Setup GCP | 5 min | Criar projeto e ativar APIs |
| 7. Deploy GCP | 10 min | Executar script ou comandos gcloud |
| 8. Validar produção | 5 min | Testar URL pública |
| **TOTAL** | **50-60 min** | **De zero a produção** |

---

## 📦 Passo 1: Preparar os Arquivos

### 1.1 - Criar estrutura de pastas

```bash
mkdir sentiment-api
cd sentiment-api

# Criar pastas
mkdir app
mkdir training
mkdir tests
mkdir models
```

### 1.2 - Copiar arquivos

Copie os arquivos de código fornecidos para seus respectivos locais:

**app/**
- `app/__init__.py` (vazio, apenas marca como pacote)
- `app/main.py` (código FastAPI)
- `app/config.py` (configurações)
- `app/models.py` (schemas Pydantic)
- `app/utils.py` (lógica de inferência)
- `app/logger.py` (logging)

**training/**
- `training/download_model.py` (script para baixar modelo)

**tests/**
- `tests/__init__.py` (vazio)
- `tests/test_api.py` (testes)

**Raiz do projeto**
- `requirements.txt`
- `Dockerfile`
- `.dockerignore`
- `.gitignore`
- `.env.example`
- `README.md`
- `test_requests.py`
- `deploy_gcp.sh`

**Resultado:**
```
sentiment-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── utils.py
│   └── logger.py
├── training/
│   └── download_model.py
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── models/
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .env.example
├── README.md
├── test_requests.py
└── deploy_gcp.sh
```

---

## 🔧 Passo 2: Setup Local

### 2.1 - Criar e ativar ambiente virtual

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# Windows (CMD)
python -m venv venv
venv\Scripts\activate.bat
```

### 2.2 - Instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Deve instalar:
- fastapi
- uvicorn
- pydantic
- transformers
- torch
- python-dotenv
- pytest
- httpx

**Tempo esperado:** 5-10 minutos (depende da internet)

### 2.3 - Verificar instalação

```bash
python -c "from transformers import pipeline; print('✅ Transformers OK')"
python -c "from fastapi import FastAPI; print('✅ FastAPI OK')"
```

---

## 🤖 Passo 3: Download do Modelo

### 3.1 - Executar script de download

```bash
python training/download_model.py
```

**O que vai acontecer:**
1. Script carrega o modelo `distilbert-base-multilingual-uncased-sentiment`
2. Hugging Face baixa ~500MB de arquivo
3. Modelo é cacheado pelo Hugging Face (geralmente em `~/.cache/huggingface/`)
4. Você vai ver logs de progresso

**Esperado:**
```
[INFO] Iniciando download do modelo...
[INFO] Modelo: distilbert-base-multilingual-uncased-sentiment
[INFO] Device: cpu
[INFO] Carregando modelo: distilbert-base-multilingual-uncased-sentiment
[INFO] Modelo carregado com sucesso
[INFO] ✅ Modelo baixado e pronto para usar!
```

**Tempo:** 5-15 minutos (depende de internet)

---

## ✅ Passo 4: Testar Local (sem Docker)

### 4.1 - Iniciar servidor

```bash
uvicorn app.main:app --reload --port 8000
```

**Esperado:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

### 4.2 - Testar em outro terminal

```bash
# Health check
curl http://localhost:8000/health

# Resposta esperada:
# {"status":"healthy","version":"1.0.0","model_ready":true}

# Predição
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Este produto é excelente!", "lang": "pt"}'

# Resposta esperada:
# {"label":"positive","score":0.9876,"model_version":"1.0.0","inference_time_ms":45.2}
```

### 4.3 - Acessar documentação Swagger

Abra no navegador: **http://localhost:8000/docs**

Você pode testar os endpoints direto do Swagger!

### 4.4 - Rodar testes automatizados

```bash
pytest tests/ -v

# Esperado: 10+ testes passando
```

**Parar o servidor:**
```
CTRL+C
```

---

## 🐳 Passo 5: Docker (Local)

### 5.1 - Instalar Docker

Se não tiver, baixe em: https://www.docker.com/products/docker-desktop

Verificar instalação:
```bash
docker --version
```

### 5.2 - Build da imagem

```bash
docker build -t sentiment-api:v1.0 .
```

**Esperado:**
```
[1/5] FROM python:3.11-slim
[2/5] WORKDIR /app
[3/5] COPY requirements.txt .
[4/5] RUN pip install -r requirements.txt
[5/5] COPY app/ ./app/
```

**Tempo:** 10-15 minutos (primeira vez)

### 5.3 - Rodar container

```bash
docker run -p 8000:8000 sentiment-api:v1.0
```

**Esperado:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5.4 - Testar container

Em outro terminal:
```bash
curl http://localhost:8000/health
```

### 5.5 - Ver containers rodando

```bash
docker ps

# Esperado:
# CONTAINER ID   IMAGE                    PORTS
# xxxxx          sentiment-api:v1.0       0.0.0.0:8000->8000/tcp
```

### 5.6 - Parar container

```bash
# Encontrar ID
docker ps

# Parar
docker stop <CONTAINER_ID>
```

---

## ☁️ Passo 6: Setup Google Cloud Platform

### 6.1 - Criar conta GCP

1. Ir para https://cloud.google.com/
2. Clique em "Try for Free"
3. Fazer login com Google
4. Adicionar cartão de crédito (required, mas tem free tier)

### 6.2 - Criar projeto

1. Acesse https://console.cloud.google.com/
2. Clique no dropdown do projeto (canto superior esquerdo)
3. Clique em "NEW PROJECT"
4. Nome: `sentiment-api` (ou o que preferir)
5. Clique "CREATE"

**Anote o PROJECT_ID** (ex: `sentiment-api-123456`)

### 6.3 - Instalar Google Cloud SDK

Mac/Linux:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

Windows:
- Baixe em: https://cloud.google.com/sdk/docs/install-sdk#windows
- Execute o instalador

Verificar:
```bash
gcloud --version
```

### 6.4 - Login no gcloud

```bash
gcloud auth login
```

1. Navegador abre automaticamente
2. Selecione sua conta Google
3. Clique "Allow"
4. Terminal mostra: "You are now authenticated"

### 6.5 - Configurar projeto

```bash
gcloud config set project <YOUR_PROJECT_ID>

# Exemplo:
# gcloud config set project sentiment-api-123456
```

Verificar:
```bash
gcloud config get-value project
```

### 6.6 - Ativar APIs necessárias

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

---

## 🚀 Passo 7: Deploy para Cloud Run

### Opção A: Script automático (mais fácil)

```bash
bash deploy_gcp.sh <PROJECT_ID> sentiment-api us-central1

# Exemplo:
# bash deploy_gcp.sh sentiment-api-123456 sentiment-api us-central1
```

O script faz tudo automaticamente!

### Opção B: Manual (passo a passo)

#### 7.1 - Build com gcloud

```bash
PROJECT_ID=sentiment-api-123456  # Substitua
SERVICE_NAME=sentiment-api
REGION=us-central1

gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:v1.0
```

**Tempo:** 5-10 minutos

**Esperado:**
```
Starting Step #0
...
DONE
```

#### 7.2 - Deploy para Cloud Run

```bash
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:v1.0 \
  --platform managed \
  --region $REGION \
  --memory 512Mi \
  --timeout 60 \
  --allow-unauthenticated
```

**Esperado:**
```
Deploying...
✓ Deploying new service... Done.
✓ Creating Revision...
✓ Service [sentiment-api] revision [sentiment-api-00001-xyz] has been deployed
Service URL: https://sentiment-api-xxxxx.run.app
```

**Copie a URL!**

---

## ✅ Passo 8: Testar Produção

### 8.1 - Usar script de testes

```bash
python test_requests.py https://sentiment-api-xxxxx.run.app
```

**Esperado:**
```
✅ Health Check PASSOU
✅ Positivo PT PASSOU
✅ Negativo PT PASSOU
✅ Neutro PT PASSOU
✅ Positivo EN PASSOU
✅ Negativo EN PASSOU

Total: 6/6 testes passaram
🎉 Todos os testes passaram!
```

### 8.2 - Testar manualmente

```bash
SERVICE_URL=https://sentiment-api-xxxxx.run.app

# Health
curl $SERVICE_URL/health

# Predição
curl -X POST $SERVICE_URL/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Adorei!", "lang": "pt"}'
```

### 8.3 - Acessar Swagger online

```
https://sentiment-api-xxxxx.run.app/docs
```

Abra no navegador e teste direto da UI!

---

## 📊 Passo 9: Monitoramento

### Ver logs

```bash
gcloud run logs read sentiment-api --limit 50
```

### Ver métricas

No Console GCP:
1. Acesse https://console.cloud.google.com/run
2. Clique em `sentiment-api`
3. Veja: requisições, erros, latência, etc.

### Desativar/Deletar serviço

```bash
gcloud run services delete sentiment-api --region us-central1
```

---

## 🎯 Checklist Final

- [ ] Arquivos copiados corretamente
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Modelo baixado (`python training/download_model.py`)
- [ ] Testes locais passando (`pytest tests/ -v`)
- [ ] Docker build funcionando (`docker build -t sentiment-api:v1.0 .`)
- [ ] Docker container testado (`docker run -p 8000:8000 sentiment-api:v1.0`)
- [ ] Projeto GCP criado
- [ ] gcloud CLI configurado (`gcloud config set project <PROJECT_ID>`)
- [ ] APIs ativadas
- [ ] Deploy completado
- [ ] Testes de produção passando

---

## 🆘 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'app'"

**Solução:** Certifique-se de estar no diretório raiz:
```bash
cd sentiment-api
python -c "from app.main import app"
```

### Erro: "No space left on device"

**Solução:** Limpar cache do Docker:
```bash
docker system prune -a
```

### Erro: "timeout" no primeiro teste

**Solução:** O modelo leva tempo para carregar na primeira vez. Aguarde 30 segundos e teste novamente.

### Erro: "CUDA out of memory"

**Solução:** Use CPU:
```bash
export MODEL_DEVICE=cpu
```

### Cloud Run falha com erro 500

**Solução:** Ver logs:
```bash
gcloud run logs read sentiment-api --limit 100
```

### Modelo não baixa

**Solução:** Verificar internet e espaço:
```bash
du -sh ~/.cache/huggingface/  # Verificar espaço usado
```

---

## 📚 Recursos Úteis

- FastAPI: https://fastapi.tiangolo.com/
- Hugging Face: https://huggingface.co/
- GCP Cloud Run: https://cloud.google.com/run/docs
- Docker: https://docs.docker.com/

---

## 🎉 Próximos Passos

1. Customizar o modelo (treinar o seu próprio)
2. Adicionar autenticação
3. Implementar rate limiting
4. Criar CI/CD com GitHub Actions
5. Suportar múltiplas versões do modelo

---

**Última atualização:** Janeiro 2026
