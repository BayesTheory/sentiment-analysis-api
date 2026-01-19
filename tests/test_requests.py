#!/usr/bin/env python3
"""
Script de teste rápido para a API
Teste local: python test_requests.py http://localhost:8000
Teste produção: python test_requests.py https://seu-deploy.run.app
"""

import sys
import requests
import json
from typing import Optional

def test_health(base_url: str):
    """Testa o endpoint /health"""
    print(f"\n📋 Testando /health")
    print("-" * 50)
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"Response:\n{json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_predict(base_url: str, text: str, lang: str = "pt"):
    """Testa o endpoint /predict"""
    print(f"\n🤖 Testando /predict")
    print("-" * 50)
    print(f"Texto: {text}")
    print(f"Idioma: {lang}")
    
    try:
        payload = {
            "text": text,
            "lang": lang
        }
        
        response = requests.post(
            f"{base_url}/predict",
            json=payload,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso!")
            print(f"Sentimento: {data['label']}")
            print(f"Confiança: {data['score']:.2%}")
            print(f"Tempo: {data['inference_time_ms']:.2f}ms")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Executa suite de testes"""
    
    if len(sys.argv) < 2:
        print("❌ Uso: python test_requests.py <URL>")
        print("   Exemplo: python test_requests.py http://localhost:8000")
        print("   Exemplo: python test_requests.py https://sentiment-api-xxxxx.run.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip("/")
    
    print(f"\n🚀 Iniciando testes para: {base_url}\n")
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health(base_url)))
    
    # Test 2: Positivo (PT)
    results.append(("Positivo PT", test_predict(
        base_url,
        "Este produto é excelente! Adorei!",
        "pt"
    )))
    
    # Test 3: Negativo (PT)
    results.append(("Negativo PT", test_predict(
        base_url,
        "Péssimo produto. Não recomendo.",
        "pt"
    )))
    
    # Test 4: Neutro (PT)
    results.append(("Neutro PT", test_predict(
        base_url,
        "O céu está azul.",
        "pt"
    )))
    
    # Test 5: Positivo (EN)
    results.append(("Positivo EN", test_predict(
        base_url,
        "This is amazing! I love it!",
        "en"
    )))
    
    # Test 6: Negativo (EN)
    results.append(("Negativo EN", test_predict(
        base_url,
        "Terrible product. Would not recommend.",
        "en"
    )))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam")
        return 1

if __name__ == "__main__":
    sys.exit(main())
