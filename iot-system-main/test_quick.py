#!/usr/bin/env python3
"""
Script de teste rápido - verifica se o modo offline está funcionando
sem erros de JWT Signature
"""

import sys
print("1️⃣  Testando importação de firebase_auth em modo offline...")

try:
    import firebase_auth
    print("   ✅ firebase_auth importado com sucesso (sem erros de JWT)\n")
except Exception as e:
    print(f"   ❌ ERRO: {str(e)}\n")
    sys.exit(1)

print("2️⃣  Testando cadastro...")
try:
    resultado = firebase_auth.cadastrar({
        "nome_responsavel": "João",
        "email": "joao@teste.com",
        "senha": "123456",
        "nome_crianca": "Lucas",
        "apelido": "Luc",
        "data_nascimento": "01/01/2015",
    })
    
    if resultado["ok"]:
        print(f"   ✅ Cadastro bem-sucedido!")
        print(f"      UID: {resultado['uid'][:30]}...\n")
    else:
        print(f"   ❌ Erro: {resultado['erro']}\n")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ ERRO: {str(e)}\n")
    sys.exit(1)

print("3️⃣  Testando login...")
try:
    resultado = firebase_auth.login("joao@teste.com", "123456")
    
    if resultado["ok"]:
        print(f"   ✅ Login bem-sucedido!")
        print(f"      UID: {resultado['uid'][:30]}...")
        print(f"      Apelido: {resultado['apelido']}\n")
    else:
        print(f"   ❌ Erro: {resultado['erro']}\n")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ ERRO: {str(e)}\n")
    sys.exit(1)

print("="*50)
print("✅ TUDO FUNCIONANDO EM MODO OFFLINE!")
print("="*50)
print("\nAgora você pode rodar:")
print("  python main.py\n")
print("E testar o jogo sem erros de JWT Signature!\n")
