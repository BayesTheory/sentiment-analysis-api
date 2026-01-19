# 🎯 Sentiment Analysis API

API de análise de sentimentos com **FastAPI** + **RoBERTa (Twitter)**, interface web integrada, Firestore para logging, Docker e deploy em **Google Cloud Run**.

- **Status**: ✅ Em produção (Cloud Run)
- **Modelo**: `cardiffnlp/twitter-roberta-base-sentiment-latest` (English only)
- **Licença**: MIT

---

## 🔗 URLs de Produção

| Recurso | Link |
|---------|------|
| **API** | https://sentiment-analysis-api-XXXXX.southamerica-east1.run.app |
| **Docs (Swagger)** | https://sentiment-analysis-api-XXXXX.southamerica-east1.run.app/docs |
| **UI** | https://sentiment-analysis-api-XXXXX.southamerica-east1.run.app/main |
| **Health Check** | https://sentiment-analysis-api-XXXXX.southamerica-east1.run.app/health |

---

## ✨ O que entrega

- ✅ Classificação de sentimento em tempo real (positive/neutral/negative)
- ✅ Interface web simples e responsiva em `/main`
- ✅ Health check para monitoramento (`/health`)
- ✅ Logging automático no Firestore
- ✅ Tracking por inference ID (UUID)
- ✅ Documentação interativa via Swagger (`/docs`)

---

## 📌 Endpoints

| Rota | Método | Descrição | Autenticação |
|------|--------|-----------|--------------|
| `/` | GET | Informações da API | ❌ |
| `/main` | GET | Interface web | ❌ |
| `/health` | GET | Health check + modelo status | ❌ |
| `/predict` | POST | Classifica sentimento | ❌ |
| `/docs` | GET | Swagger UI | ❌ |

---

## 🚀 Começar Local

### 1️⃣ Clonar e ambiente
```bash
git clone https://github.com/BayesTheory/sentiment-analysis-api.git
cd sentiment-analysis-api

python -m venv venv
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

### 2️⃣ Instalar dependências
```bash
pip install -r requirements.txt
```

### 3️⃣ Configurar variáveis
Crie `.env.local` (não commitar):
```bash
cp .env .env.local
```

Edite se necessário (modelo, host, porta, etc).

### 4️⃣ Rodar API
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse:
- **UI**: http://127.0.0.1:8000/main
- **Swagger Docs**: http://127.0.0.1:8000/docs
- **Health**: http://127.0.0.1:8000/health

---

## 📦 Estrutura do Projeto

```
sentiment-analysis-api/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configurações (env vars)
│   ├── logger.py              # Setup de logging
│   ├── models.py              # Schemas Pydantic
│   ├── utils.py               # Funções auxiliares (predict, load_model)
│   ├── firestore_client.py    # Integração Firestore
│   ├── dash.py                # Router de dashboard (opcional)
│   └── main.py                # FastAPI app principal
├── static/
│   ├── index.html             # UI web
│   └── style.css              # Estilos
├── training/
│   └── download_model.py      # Script para baixar modelo
├── models/
│   └── Sentiment-Model/       # Modelo RoBERTa (local)
├── tests/
│   └── test_api.py            # Testes unitários
├── Dockerfile                 # Container image
├── requirements.txt           # Dependências Python
├── .env                       # Template de variáveis (não commitar)
├── .env.local                 # Variáveis locais (não commitar)
├── .gitignore                 # Arquivos ignorados no Git
├── deploy_gcp.sh              # Script deploy Cloud Run
└── README.md                  # Este arquivo
```

---

## 🧠 Modelo

- **Versão**: `cardiffnlp/twitter-roberta-base-sentiment-latest` (HuggingFace)
- **Classes**: `positive`, `neutral`, `negative`
- **Idioma**: English only
- **Tamanho**: ~330 MB
- **Localização**: `./models/Sentiment-Model/`

### Baixar modelo (primeira execução)
```bash
python training/download_model.py
```

---

## 📊 Logging & Observabilidade

### Local
Logs aparecem no stdout (console) com timestamps e níveis (INFO, WARNING, ERROR).

### Cloud Run
- Logs automáticos no **Cloud Logging**
- Inferences salvas no **Firestore** (com ID, score, tempo de inferência)
- Acesse via: `gcloud logging read "resource.type=cloud_run_revision" --limit=50`


---

## ⚙️ Stack Tecnológico

| Componente | Tecnologia |
|-----------|-----------|
| **Backend** | FastAPI + Uvicorn |
| **ML** | Transformers (HuggingFace) + PyTorch |
| **Frontend** | HTML + CSS + Vanilla JS |
| **Container** | Docker |
| **Cloud** | Google Cloud Run |
| **Banco de dados** | Firestore (optional) |
| **Logging** | Python logging + Cloud Logging |

---

## 📝 Performance

- **Tempo médio de inferência**: 40–50 ms (CPU)
- **Throughput**: ~20 req/s (single worker)
- **Memory**: ~2 GB (modelo + runtime)

Para aumentar throughput em produção, aumente `WORKERS` ou replicas no Cloud Run.

---

## 📄 Licença

MIT License — veja [LICENSE](./LICENSE) para detalhes.

