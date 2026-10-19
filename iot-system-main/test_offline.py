#!/usr/bin/env python3
"""
Script de teste rápido para modo offline
Permite cadastrar e testar login sem Firebase
"""

import firebase_mock as mock
import json


def menu_principal():
    while True:
        print("\n" + "="*50)
        print("TESTE OFFLINE - LER BRINCANDO")
        print("="*50)
        print("1. Cadastrar novo usuário")
        print("2. Fazer login")
        print("3. Listar usuários cadastrados")
        print("4. Limpar dados de teste")
        print("0. Sair")
        print("-"*50)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            cadastrar_usuario()
        elif opcao == "2":
            fazer_login()
        elif opcao == "3":
            listar_usuarios()
        elif opcao == "4":
            limpar_dados()
        elif opcao == "0":
            print("\nSaindo...\n")
            break
        else:
            print("❌ Opção inválida!")


def cadastrar_usuario():
    print("\n" + "-"*50)
    print("CADASTRO DE NOVO USUÁRIO")
    print("-"*50)
    
    try:
        nome_responsavel = input("Nome do responsável: ").strip()
        if not nome_responsavel:
            print("❌ Nome do responsável é obrigatório!")
            return
        
        email = input("E-mail: ").strip()
        if not email:
            print("❌ E-mail é obrigatório!")
            return
        
        senha = input("Senha: ").strip()
        if not senha:
            print("❌ Senha é obrigatória!")
            return
        
        nome_crianca = input("Nome da criança: ").strip()
        if not nome_crianca:
            print("❌ Nome da criança é obrigatório!")
            return
        
        apelido = input("Apelido da criança: ").strip()
        if not apelido:
            print("❌ Apelido é obrigatório!")
            return
        
        dados = {
            "nome_responsavel": nome_responsavel,
            "email": email,
            "senha": senha,
            "nome_crianca": nome_crianca,
            "apelido": apelido,
            "data_nascimento": input("Data de nascimento (DD/MM/AAAA): ").strip() or "01/01/2015",
            "telefone": input("Telefone (opcional): ").strip() or "",
            "avatar": "Herói",
            "sexo": "Indefinido",
        }
        
        resultado = mock.cadastrar(dados)
        
        if resultado["ok"]:
            print(f"\n✅ Usuário cadastrado com sucesso!")
            print(f"   UID: {resultado['uid']}")
            print(f"   Nome: {resultado['nome']}")
            print(f"   Apelido da criança: {resultado['apelido']}")
        else:
            print(f"\n❌ Erro ao cadastrar: {resultado['erro']}")
    
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")


def fazer_login():
    print("\n" + "-"*50)
    print("LOGIN")
    print("-"*50)
    
    try:
        email = input("E-mail: ").strip()
        if not email:
            print("❌ E-mail é obrigatório!")
            return
        
        senha = input("Senha: ").strip()
        if not senha:
            print("❌ Senha é obrigatória!")
            return
        
        resultado = mock.login(email, senha)
        
        if resultado["ok"]:
            print(f"\n✅ Login realizado com sucesso!")
            print(f"   UID: {resultado['uid']}")
            print(f"   Nome do responsável: {resultado['nome']}")
            print(f"   Apelido da criança: {resultado['apelido']}")
            print(f"   Avatar: {resultado['avatar']}")
        else:
            print(f"\n❌ Erro: {resultado['erro']}")
    
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")


def listar_usuarios():
    print("\n" + "-"*50)
    print("USUÁRIOS CADASTRADOS")
    print("-"*50)
    
    try:
        usuarios = mock.listar_usuarios_test()
        
        if not usuarios:
            print("Nenhum usuário cadastrado ainda.")
            return
        
        for uid, user in usuarios:
            print(f"\nUID: {uid}")
            print(f"  Responsável: {user.get('nome', 'N/A')}")
            print(f"  E-mail: {user.get('email', 'N/A')}")
            crianca = user.get('crianca', {})
            print(f"  Criança: {crianca.get('nome', 'N/A')}")
            print(f"  Apelido: {crianca.get('apelido', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Erro: {str(e)}")


def limpar_dados():
    print("\n" + "-"*50)
    print("LIMPAR DADOS DE TESTE")
    print("-"*50)
    
    confirma = input("Tem certeza? Isso vai deletar TODOS os usuários cadastrados. (S/N): ").strip().lower()
    
    if confirma == 's':
        resultado = mock.limpar_dados_teste()
        if resultado["ok"]:
            print("✅ Dados de teste removidos!")
        else:
            print(f"❌ Erro: {resultado['erro']}")
    else:
        print("Operação cancelada.")


if __name__ == "__main__":
    print("\n🎮 TESTE DO SISTEMA OFFLINE\n")
    print("Este script testa o cadastro e login em modo offline.")
    print("Os dados são salvos em: data/usuarios_mock.json\n")
    
    menu_principal()
