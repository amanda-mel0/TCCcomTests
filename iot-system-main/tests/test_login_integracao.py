
import pytest
from unittest.mock import Mock
import firebase_mock as mock
import firebase_auth as svc
import test_offline as cli

pytestmark = pytest.mark.integracao


@pytest.fixture(autouse=True)
def preparar(monkeypatch, tmp_path):
    pasta = tmp_path / "data"
    monkeypatch.setattr(mock, "DATA_DIR", str(pasta))
    monkeypatch.setattr(mock, "USUARIOS_FILE", str(pasta / "usuarios_mock.json"))
    monkeypatch.setattr(svc, "MODO_OFFLINE", True)
    monkeypatch.setattr(svc, "firebase_service", mock)


def cadastrar(email="maria@teste.com", senha="123456",
              nome="Maria Silva", apelido="Joãozinho"):
    r = mock.cadastrar({
        "nome_responsavel": nome,
        "email": email,
        "senha": senha,
        "nome_crianca": "João",
        "apelido": apelido,
        "data_nascimento": "01/01/2015",
        "telefone": "",
        "avatar": "Herói",
        "sexo": "Indefinido"
    })
    assert r["ok"]
    return r


# CT19 - Cadastro e login
def test_cadastro_login():
    cad = cadastrar()
    r = svc.login("maria@teste.com", "123456")
    assert r["ok"] and r["uid"] == cad["uid"]
    assert (r["nome"], r["apelido"]) == ("Maria Silva", "Joãozinho")


# CT20, CT21 e CT22 - Logins inválidos
@pytest.mark.parametrize("email,senha,cadastra", [
    ("maria@teste.com", "errada", True),
    ("fulano@teste.com", "123456", True),
    ("maria@teste.com", "123456", False)
])
def test_login_invalido(email, senha, cadastra):
    if cadastra:
        cadastrar()
    assert svc.login(email, senha)["ok"] is False


# CT23 - Dois usuários
def test_dois_usuarios():
    cadastrar("ana@teste.com", "aaa111", "Ana", "Aninha")
    cadastrar("bia@teste.com", "bbb222", "Bia", "Bibi")

    a = svc.login("ana@teste.com", "aaa111")
    b = svc.login("bia@teste.com", "bbb222")

    assert (a["apelido"], b["apelido"]) == ("Aninha", "Bibi")
    assert a["uid"] != b["uid"]


# CT24 - Limpeza do banco
def test_limpar_dados():
    cadastrar()
    assert svc.login("maria@teste.com", "123456")["ok"]
    mock.limpar_dados_teste()
    assert not svc.login("maria@teste.com", "123456")["ok"]


# CT25 e CT26 - Tela de login
@pytest.mark.parametrize("senha,sucesso", [
    ("123456", True),
    ("errada", False)
])
def test_tela_login(monkeypatch, capsys, senha, sucesso):
    cadastrar()
    respostas = iter(["maria@teste.com", senha])
    monkeypatch.setattr("builtins.input", lambda *_: next(respostas))

    cli.fazer_login()
    saida = capsys.readouterr().out

    assert ("Login realizado com sucesso" in saida) == sucesso
    assert ("Joãozinho" in saida) if sucesso else ("Erro" in saida)


# CT27 e CT28 - Campos vazios
@pytest.mark.parametrize("respostas,mensagem", [
    ([""], "E-mail é obrigatório"),
    (["maria@teste.com", ""], "Senha é obrigatória")
])
def test_campos_vazios(monkeypatch, capsys, respostas, mensagem):
    espiao = Mock()
    monkeypatch.setattr(cli.mock, "login", espiao)
    entradas = iter(respostas)
    monkeypatch.setattr("builtins.input", lambda *_: next(entradas))

    cli.fazer_login()

    assert mensagem in capsys.readouterr().out
    espiao.assert_not_called()


# CT29 - Senha protegida
def test_senha_hash():
    cadastrar(senha="S3nhaSecreta!")
    with open(mock.USUARIOS_FILE, encoding="utf-8") as f:
        conteudo = f.read()

    assert "S3nhaSecreta!" not in conteudo
    assert mock._hash("S3nhaSecreta!") in conteudo


# CT30 - Arquivo corrompido
def test_arquivo_corrompido():
    cadastrar()
    with open(mock.USUARIOS_FILE, "w", encoding="utf-8") as f:
        f.write("{ json invalido")

    assert svc.login("maria@teste.com", "123456") == {
        "ok": False, "erro": "E-mail ou senha incorretos!"
    }


# CT31 - Mensagem de erro segura
def test_erro_seguro():
    cadastrar()
    a = svc.login("maria@teste.com", "errada")
    b = svc.login("fulano@teste.com", "123456")

    assert a["erro"] == b["erro"] == "E-mail ou senha incorretos!"
