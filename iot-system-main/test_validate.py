#!/usr/bin/env python3
"""
Script de validação rápida do modo offline
Testa cadastro, login e salvamento de dados
"""

import firebase_mock as mock
import os
import json


def test_modo_offline():
    print("🧪 TESTANDO MODO OFFLINE\n")
    
    # Teste 1: Limpar dados anteriores
    print("1️⃣  Limpando dados de teste anteriores...")
    mock.limpar_dados_teste()
    print("   ✅ OK\n")
    
    # Teste 2: Cadastrar usuário
    print("2️⃣  Testando cadastro...")
    dados = {
        "nome_responsavel": "Maria Silva",
        "email": "maria@teste.com",
        "senha": "senha123",
        "nome_crianca": "Pedro",
        "apelido": "Pedrinho",
        "data_nascimento": "15/05/2015",
        "telefone": "11999999999",
        "avatar": "Herói",
    }
    
    resultado = mock.cadastrar(dados)
    if not resultado["ok"]:
        print(f"   ❌ ERRO: {resultado['erro']}")
        return False
    
    uid = resultado["uid"]
    print(f"   ✅ Usuário criado: {uid}")
    print(f"      Nome: {resultado['nome']}")
    print(f"      Apelido da criança: {resultado['apelido']}\n")
    
    # Teste 3: Tentar cadastrar mesmo e-mail (deve falhar)
    print("3️⃣  Testando duplicação de e-mail (deve falhar)...")
    resultado2 = mock.cadastrar(dados)
    if resultado2["ok"]:
        print(f"   ❌ ERRO: Deveria ter falhado!")
        return False
    
    print(f"   ✅ Bloqueio funcionou: {resultado2['erro']}\n")
    
    # Teste 4: Fazer login com dados corretos
    print("4️⃣  Testando login com dados corretos...")
    login_ok = mock.login("maria@teste.com", "senha123")
    if not login_ok["ok"]:
        print(f"   ❌ ERRO: {login_ok['erro']}")
        return False
    
    print(f"   ✅ Login bem-sucedido!")
    print(f"      UID: {login_ok['uid']}")
    print(f"      Apelido: {login_ok['apelido']}\n")
    
    # Teste 5: Fazer login com senha errada
    print("5️⃣  Testando login com senha errada (deve falhar)...")
    login_erro = mock.login("maria@teste.com", "senhaerrada")
    if login_erro["ok"]:
        print(f"   ❌ ERRO: Deveria ter falhado!")
        return False
    
    print(f"   ✅ Bloqueio funcionou: {login_erro['erro']}\n")
    
    # Teste 6: Verificar arquivo JSON local
    print("6️⃣  Verificando arquivo de dados local...")
    usuarios_file = os.path.join(os.path.dirname(__file__), "data", "usuarios_mock.json")
    if not os.path.exists(usuarios_file):
        print(f"   ❌ ERRO: Arquivo não foi criado!")
        return False
    
    with open(usuarios_file, "r", encoding="utf-8") as f:
        dados_salvos = json.load(f)
    
    if uid not in dados_salvos:
        print(f"   ❌ ERRO: Usuário não foi salvo!")
        return False
    
    print(f"   ✅ Arquivo criado e salvo corretamente")
    print(f"      Localização: {usuarios_file}")
    print(f"      Usuários: {len(dados_salvos)}\n")
    
    # Teste 7: Listar usuários
    print("7️⃣  Testando listagem...")
    lista = mock.listar_usuarios_test()
    print(f"   ✅ Total de usuários: {len(lista)}")
    for u, dados_u in lista:
        print(f"      - {u}: {dados_u.get('email', 'N/A')}\n")
    
    print("="*50)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("="*50)
    print("\nO modo offline está funcionando corretamente.\n")
    print("Próximos passos:")
    print("1. Mude MODO_OFFLINE = True em firebase_auth.py")
    print("2. Execute: python main.py")
    print("3. Teste o cadastro e login no jogo\n")
    
    return True


if __name__ == "__main__":
    try:
        test_modo_offline()
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {str(e)}")
        import traceback
        traceback.print_exc()
