"""
Mock do Firebase para modo offline - permite testes sem credenciais reais.
Armazena dados em um arquivo JSON local (data/usuarios_mock.json)
"""

import json
import os
import hashlib
from pathlib import Path


# Diretório para armazenar dados offline
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
USUARIOS_FILE = os.path.join(DATA_DIR, "usuarios_mock.json")


def _ensure_data_dir():
    """Cria o diretório data se não existir"""
    Path(DATA_DIR).mkdir(exist_ok=True)


def _load_usuarios():
    """Carrega usuários do arquivo JSON local"""
    _ensure_data_dir()
    if os.path.exists(USUARIOS_FILE):
        try:
            with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_usuarios(usuarios):
    """Salva usuários no arquivo JSON local"""
    _ensure_data_dir()
    try:
        with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar usuários: {e}")


def _hash(password: str) -> str:
    """Hash SHA256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()


def cadastrar(dados: dict) -> dict:
    """
    Cadastra novo usuário no mock local
    
    Retorna:
        {"ok": True, "uid": "<id>", "nome": "<nome>", "apelido": "<apelido>"}
        ou
        {"ok": False, "erro": "<mensagem>"}
    """
    try:
        usuarios = _load_usuarios()
        
        # Verifica se email já existe
        for uid, u in usuarios.items():
            if u.get("email") == dados.get("email"):
                return {"ok": False, "erro": "E-mail já cadastrado!"}
        
        # Gera UID simples (timestamp + contador)
        uid = f"user_{len(usuarios) + 1}_{hash(dados.get('email', ''))}"
        
        # Cria novo usuário
        novo_usuario = {
            "nome":               dados.get("nome_responsavel", ""),
            "email":              dados.get("email", ""),
            "senha":              _hash(dados.get("senha", "")),
            "telefone":           dados.get("telefone", ""),
            "cidade":             dados.get("cidade", ""),
            "estado":             dados.get("estado", ""),
            "aceite_termos":      dados.get("aceite_termos", False),
            "aceite_privacidade": dados.get("aceite_privacidade", False),
            "aceite_dados":       dados.get("aceite_dados_crianca", False),
            "crianca": {
                "nome":         dados.get("nome_crianca", ""),
                "apelido":      dados.get("apelido", ""),
                "nascimento":   dados.get("data_nascimento", ""),
                "sexo":         dados.get("sexo", ""),
                "avatar":       dados.get("avatar", "Herói"),
                "serie":        dados.get("serie_escolar", ""),
                "escola":       dados.get("escola", ""),
                "turno":        dados.get("turno", ""),
            },
            "aprendizagem": {
                "nivel":         dados.get("nivel_leitura", ""),
                "dificuldades":  dados.get("dificuldades", []),
                "objetivo":      dados.get("objetivo", ""),
            },
            "fases_liberadas": 1,
        }
        
        usuarios[uid] = novo_usuario
        _save_usuarios(usuarios)
        
        return {
            "ok": True,
            "uid": uid,
            "nome": dados.get("nome_responsavel", ""),
            "apelido": dados.get("apelido", "")
        }
    
    except Exception as e:
        return {"ok": False, "erro": f"Erro ao cadastrar: {str(e)}"}


def login(email: str, senha: str) -> dict:
    """
    Faz login com email e senha no mock local
    
    Retorna:
        {"ok": True, "uid": "<id>", "nome": "<nome>", "apelido": "<apelido>", "avatar": "<avatar>"}
        ou
        {"ok": False, "erro": "<mensagem>"}
    """
    try:
        usuarios = _load_usuarios()
        h = _hash(senha)
        
        for uid, u in usuarios.items():
            if u.get("email") == email and u.get("senha") == h:
                crianca = u.get("crianca", {})
                return {
                    "ok":     True,
                    "uid":    uid,
                    "nome":   u.get("nome", "Responsável"),
                    "apelido": crianca.get("apelido", "Jogador"),
                    "avatar": crianca.get("avatar", "Herói"),
                }
        
        return {"ok": False, "erro": "E-mail ou senha incorretos!"}
    
    except Exception as e:
        return {"ok": False, "erro": f"Erro ao fazer login: {str(e)}"}


def get_usuario(uid: str) -> dict:
    """Obtém dados de um usuário pelo UID"""
    try:
        usuarios = _load_usuarios()
        return usuarios.get(uid, {})
    except Exception:
        return {}


def listar_usuarios_test() -> list:
    """Lista todos os usuários (apenas para testes)"""
    usuarios = _load_usuarios()
    return list(usuarios.items())


def limpar_dados_teste():
    """Limpa todos os dados de teste (apenas para testes)"""
    try:
        if os.path.exists(USUARIOS_FILE):
            os.remove(USUARIOS_FILE)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "erro": str(e)}
