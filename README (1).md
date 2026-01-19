# 🎯 Sentiment Analysis API

API de análise de sentimentos com **FastAPI**, modelo **RoBERTa (Twitter)**, containerizada com **Docker** e deployável em **Google Cloud Run**.

## 🎬 Quick Start

### Local

\`\`\`bash
# 1. Clone/Setup
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate (Windows)
pip install -r requirements.txt

# 2. Configurar .env
cp .env .env.local

# 3. Rodar
uvicorn app.main:app --reload --port 8000
\`\`\`

Abra: http://127.0.0.1:8000/main

### Cloud Run

\`\`\`bash
bash deploy_gcp.sh
\`\`\`

Sua URL: https://sentiment-api-XXXXX.southamerica-east1.run.app

## 📊 Rotas

| Rota | Método | Descrição |
|------|--------|-----------|
| \`/\` | GET | Info da API |
| \`/main\` | GET | Interface web |
| \`/health\` | GET | Health check |
| \`/predict\` | POST | Análise de sentimento |
| \`/docs\` | GET | Swagger UI |

## 🏗️ Arquitetura

\`\`\`
Usuário → Frontend (HTML/CSS) → FastAPI → RoBERTa Model → Resultado
\`\`\`

## 📦 Model

- **cardiffnlp/twitter-roberta-base-sentiment-latest**
- **Classes:** Positive, Neutral, Negative
- **Idioma:** English only
- **Local:** \`./models/Sentiment-Model\`

## 🛠️ Tech Stack

- **Backend:** FastAPI + Uvicorn
- **ML:** Transformers (HuggingFace)
- **Frontend:** HTML + CSS + JavaScript
- **Container:** Docker
- **Cloud:** Google Cloud Run

## 📝 Exemplo de Uso

\`\`\`bash
curl -X POST http://localhost:8000/predict \\
  -H "Content-Type: application/json" \\
  -d '{"text":"I love this!","lang":"en"}'
\`\`\`

**Resposta:**
\`\`\`json
{
  "label": "positive",
  "score": 0.999,
  "model_version": "1.0.0",
  "inference_time_ms": 45.2
}
\`\`\`

## 🚀 Deploy

\`\`\`bash
# Cloud Run
bash deploy_gcp.sh

# Docker local
docker build -t sentiment-api .
docker run -p 8080:8080 sentiment-api
\`\`\`

## 📄 Estrutura

\`\`\`
sentiment-api/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── logger.py
│   ├── models.py
│   ├── utils.py
│   └── main.py
├── static/
│   ├── index.html
│   └── style.css
├── training/
│   └── download_model.py
├── models/
│   └── Sentiment-Model/  (seu modelo)
├── tests/
│   └── test_api.py
├── Dockerfile
├── requirements.txt
├── .env
├── .gitignore
├── deploy_gcp.sh
└── README.md
\`\`\`

## 📄 Licença

MIT
