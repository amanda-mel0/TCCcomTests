import hashlib
import os
import sys

# ── MODO OFFLINE (para testes sem Firebase) ────────────────────────────────────
# Mude para True para usar modo offline com mock local
MODO_OFFLINE = True

# Se está em modo offline, usa firebase_mock (sem importar firebase_admin)
if MODO_OFFLINE:
    import firebase_mock as firebase_service
else:
    # Só importa Firebase se não estiver em modo offline
    import firebase_admin
    from firebase_admin import credentials, db
    firebase_service = None

_initialized = False


def resource_path(relative_path):
    """ Busca o caminho real do arquivo, seja no script ou no .exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def init_firebase():
    global _initialized
    if MODO_OFFLINE or _initialized:
        return
    
    if not _initialized:
        # Mudança aqui: usamos a função resource_path
        cred_path = resource_path("firebase_credentials.json")
        
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://ler-brincando-default-rtdb.firebaseio.com"
        })
        _initialized = True


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def cadastrar(dados: dict) -> dict:
    try:
        # Modo offline
        if MODO_OFFLINE:
            return firebase_service.cadastrar(dados)
        
        # Modo online (Firebase)
        init_firebase()
        ref = db.reference("usuarios")
        todos = ref.get() or {}
        for uid, u in todos.items():
            if u.get("email") == dados["email"]:
                return {"ok": False, "erro": "E-mail já cadastrado!"}

        novo = ref.push({
            "nome":               dados["nome_responsavel"],
            "email":              dados["email"],
            "senha":              _hash(dados["senha"]),
            "telefone":           dados.get("telefone", ""),
            "cidade":             dados.get("cidade", ""),
            "estado":             dados.get("estado", ""),
            "aceite_termos":      dados.get("aceite_termos", False),
            "aceite_privacidade": dados.get("aceite_privacidade", False),
            "aceite_dados":       dados.get("aceite_dados_crianca", False),
            "crianca": {
                "nome":     dados["nome_crianca"],
                "apelido":  dados["apelido"],
                "nascimento": dados["data_nascimento"],
                "sexo":     dados.get("sexo", ""),
                "avatar":   dados.get("avatar", "Herói"),
                "serie":    dados.get("serie_escolar", ""),
                "escola":   dados.get("escola", ""),
                "turno":    dados.get("turno", ""),
            },
            "aprendizagem": {
                "nivel":       dados.get("nivel_leitura", ""),
                "dificuldades": dados.get("dificuldades", []),
                "objetivo":    dados.get("objetivo", ""),
            },
            "fases_liberadas": 1,
        })
        return {"ok": True, "uid": novo.key,
                "nome": dados["nome_responsavel"],
                "apelido": dados["apelido"]}
    except Exception as e:
        return {"ok": False, "erro": str(e)}
    



def login(email: str, senha: str) -> dict:
    try:
        # Modo offline
        if MODO_OFFLINE:
            return firebase_service.login(email, senha)
        
        # Modo online (Firebase)
        init_firebase()
        ref = db.reference("usuarios")
        todos = ref.get() or {}
        h = _hash(senha)
        for uid, u in todos.items():
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
        return {"ok": False, "erro": str(e)}
