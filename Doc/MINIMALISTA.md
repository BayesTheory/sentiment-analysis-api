# 🎯 VERSÃO MINIMALISTA - Apenas o Essencial

## 📦 Total: 10 Arquivos (reduzido de 24)

```
sentiment-api/
├── 📖 README.md              ← Documentação TUDO EM UM
│
├── app/
│   ├── __init__.py           (vazio)
│   ├── main.py               (FastAPI completo)
│   ├── config.py             (configurações)
│   └── utils.py              (modelo + inferência)
│
├── tests/
│   └── test_api.py           (testes básicos)
│
├── models/                   (pasta para cache do modelo)
│
├── requirements.txt          (dependências)
├── Dockerfile               (Docker)
├── .gitignore               (Git ignore)
└── deploy.sh                (Deploy GCP)
```

---

## 🚀 Setup Rápido (3 linhas)

```bash
cd sentiment-api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && python -c "from app.utils import load_model; load_model()"
uvicorn app.main:app --reload --port 8000
```

Tudo pronto! Confira em: http://localhost:8000/docs

---

## 🐳 Deploy GCP (1 comando)

```bash
bash deploy.sh SEU_PROJECT_ID
```

Pronto! URL pública gerada automaticamente.

---

## 📚 Tudo em 1 README

O `README.md` contém:
- Instruções de setup
- Exemplos de API
- Troubleshooting
- Deploy passo-a-passo
- Tudo que você precisa

---

**✅ Simples, prático, sem bloat!**
