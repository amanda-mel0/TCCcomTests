# Modo Offline - Testes sem Firebase

Este projeto agora suporta **modo offline** para testes sem credenciais do Firebase. Perfeito para desenvolvimento e testes locais.

## Como Ativar

### Opção 1: Teste Rápido com Script Interativo

Execute o script de teste:

```bash
python test_offline.py
```

Este script oferece um menu interativo para:
- ✅ Cadastrar novo usuário
- ✅ Fazer login
- ✅ Listar usuários cadastrados
- ✅ Limpar dados de teste

### Opção 2: Ativar Modo Offline no Jogo

Abra `firebase_auth.py` e mude a linha:

```python
MODO_OFFLINE = False
```

Para:

```python
MODO_OFFLINE = True
```

Depois rode o jogo normalmente:

```bash
python main.py
```

## Como Funciona

- **Dados locais**: Usuários são salvos em `data/usuarios_mock.json` (criado automaticamente)
- **Sem rede**: Funciona 100% offline, sem dependência do Firebase
- **Mesma interface**: Usa as mesmas funções `cadastrar()` e `login()` do Firebase

## Estrutura de Dados (Offline)

Arquivo `data/usuarios_mock.json`:

```json
{
  "user_1_abc123": {
    "nome": "João Silva",
    "email": "joao@email.com",
    "senha": "<hash>",
    "crianca": {
      "nome": "Lucas",
      "apelido": "Luc",
      "avatar": "Herói",
      ...
    },
    ...
  }
}
```

## Dados de Teste Pré-carregados

Para entrar rapidinho no jogo, cadastre um usuário com:
- **E-mail**: teste@teste.com
- **Senha**: 123456
- **Nome da criança**: Lucas
- **Apelido**: Luc

Depois faça login com essas credenciais.

## Alternando Entre Modos

| Modo | Arquivo | Flag |
|------|---------|------|
| **Online (Firebase)** | `firebase_auth.py` | `MODO_OFFLINE = False` |
| **Offline (Mock)** | `firebase_mock.py` | `MODO_OFFLINE = True` |

Mude apenas 1 linha em `firebase_auth.py` para alternar!

## Estrutura de Arquivos

```
lerbrincando/
├── firebase_auth.py        # ← Mude MODO_OFFLINE aqui
├── firebase_mock.py        # ← Mock do Firebase (novo)
├── test_offline.py         # ← Script de teste interativo
├── data/
│   └── usuarios_mock.json  # ← Dados locais (criado automaticamente)
└── main.py
```

## Troubleshooting

**P: Os dados não estão sendo salvos?**
- R: Verifique permissões na pasta `data/`. O script cria automaticamente se não existir.

**P: Quero resetar os dados de teste?**
- R: Use a opção "4" no `test_offline.py`, ou delete `data/usuarios_mock.json` manualmente.

**P: Como voltar para Firebase?**
- R: Mude `MODO_OFFLINE = False` em `firebase_auth.py` e certifique-se que `firebase_credentials.json` está válido.

---

**Dica:** Use modo offline para testes rápidos e desenvolvimento. Mude para online quando tiver credenciais Firebase válidas!
