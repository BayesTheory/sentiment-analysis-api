"""
Script para pré-carregar o modelo durante build do Docker.
Reduz cold start na primeira requisição.
"""

import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from app.logger import get_logger

logger = get_logger(__name__)

def download_model():
    """Baixa e cacheia modelo do Hugging Face"""
    model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    cache_dir = "./models"
    
    try:
        logger.info(f"📥 Baixando modelo: {model_name}")
        
        # Criar diretório se não existir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Baixar tokenizer
        logger.info("Baixando tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        
        # Baixar modelo
        logger.info("Baixando modelo...")
        model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=cache_dir)
        
        logger.info("✅ Modelo baixado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao baixar modelo: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    download_model()
