# Arquitetura

Guia do padrão do projeto. A ideia é que qualquer feature nova caiba
numa dessas gavetas sem inventar estrutura nova.

## Organização por domínio

O código é agrupado por **domínio de negócio**, não por tipo de arquivo.
Tudo que fala de usuário mora em `domains/users/`:

```
domains/
  users/
    users_controller.py            # rotas HTTP + as factories de DI do domínio
    models/
      users_model.py               # tabelas (SQLAlchemy)
    repositories/
      users_auth_repository.py     # acesso ao banco
    schemas/
      users_schemas.py             # contratos de entrada/saída (Pydantic)
    services/
      users_auth_service.py        # regra de negócio
  health/
    health_controller.py           # domínio simples: só o controller

api/v1/routers.py                  # junta os routers de todos os domínios
core/
  config.py                        # settings (env vars)
  database.py                      # engine, SessionLocal, Base, get_db
main.py                            # cria o app, monta /api/v1 e o /docs
```

Nem todo domínio precisa de todas as camadas. `health` tem só um
controller porque não tem regra nem tabela. Crie a pasta quando tiver o
primeiro arquivo dela, não antes.

## As camadas e o que cada uma pode saber

| Camada | Responsabilidade | Pode importar | **Não** pode |
|---|---|---|---|
| **Controller** | Falar HTTP: receber request, devolver response, status code | schemas, services, repositories (só para montar a DI) | escrever query SQL |
| **Service** | Regra de negócio: validar, orquestrar, decidir | schemas, models, repositories | `fastapi` (nada de `HTTPException`, `Request`, `Depends`) |
| **Repository** | Conversar com o banco | models, `Session` | schemas, services |
| **Model** | Formato da tabela no banco | `core.database.Base`, SQLAlchemy | schemas, services |
| **Schema** | Contrato da API: o que entra e o que sai | pydantic | models, services |

A regra que resume tudo: **o controller não escreve query, e o service
não sabe que existe HTTP.** Se um dia a API virar CLI ou worker, os
services continuam funcionando sem tocar em nada.

Consequência prática: service não levanta `HTTPException`. Ele devolve um
valor (`None`, `False`, um objeto) ou levanta uma exceção própria, e o
controller traduz isso para HTTP.

## Injeção de dependência

A fiação fica **no próprio controller**, numa função `get_*` logo acima
das rotas, e as rotas pedem o que precisam com `Depends`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from domains.users.repositories.users_auth_repository import UsersAuthRepository
from domains.users.schemas.users_schemas import UsersAuth
from domains.users.services.users_auth_service import UsersAuthService

router = APIRouter()


def get_auth_service(db: Session = Depends(get_db)) -> UsersAuthService:
    return UsersAuthService(UsersAuthRepository(db))


@router.post("/register")
def register_user(
    user_data: UsersAuth,
    auth_service: UsersAuthService = Depends(get_auth_service),
) -> bool:
    return auth_service.register(user_data)
```

Três coisas para guardar:

- **`get_db` é a única fonte da `Session`.** Ninguém abre sessão na mão.
- **A cadeia é montada uma vez**, em `get_auth_service`. Se amanhã o
  service precisar de mais um colaborador, muda só essa função — nenhuma
  rota é tocada.
- **O service continua trocável em teste**, porque quem constrói ele é a
  dependência, não o corpo da rota:
  `app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()`.

> Existia antes um `users_dependencies.py` com aliases
> `Annotated[..., Depends(...)]`. Foi removido: para o tamanho deste
> projeto era um arquivo a mais para abrir só para descobrir de onde vinha
> o objeto. `Depends` direto na assinatura diz tudo ali mesmo.

### Dependência que não devolve nada

Para guard (checar token, exigir permissão), não polua a assinatura da
rota — registre no router, em `api/v1/routers.py`:

```python
router.include_router(
    users_controller,
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(verify_token)],
)
```

Vale para todas as rotas daquele grupo de uma vez.

## Registrando um router

Todo controller expõe um `router = APIRouter()` **sem prefixo**. O prefixo
é decidido em `api/v1/routers.py`:

```python
router.include_router(users_controller, prefix="/users", tags=["users"])
```

Assim o mesmo controller pode ser remontado em outra versão da API sem
edição. A versão (`/api/v1`) entra no `main.py`, no `include_router`.

## Checklist: adicionar um domínio novo

Exemplo com `products`:

1. `domains/products/models/products_model.py` — a tabela, herdando de
   `core.database.Base`.
2. `alembic/env.py` — importar o novo pacote de models (`import
   domains.products.models`), senão o autogenerate não enxerga a tabela.
3. `make migration m="create products"` e depois `make migrate` — a
   migration gerada em `alembic/versions/` **precisa ser commitada**.
4. `domains/products/schemas/products_schemas.py` — o que entra e o que
   sai pela API.
5. `domains/products/repositories/products_repository.py` — as queries.
6. `domains/products/services/products_service.py` — a regra. Recebe as
   dependências pelo `__init__`, sem importar `fastapi`.
7. `domains/products/products_controller.py` — `router = APIRouter()`, a
   factory `get_products_service` e as rotas.
8. `api/v1/routers.py` — `include_router` com prefixo e tag.

Os passos que costumam ser esquecidos são o 2 e o 8: sem o 2 a migration
sai vazia, e sem o 8 a rota simplesmente não existe — nos dois casos sem
erro nenhum na tela.

## Convenções de nome

- **Arquivos**: `snake_case`, prefixados pelo domínio —
  `users_controller.py`, `users_schemas.py`, `users_auth_service.py`.
  O prefixo evita cinco abas chamadas `controller.py` abertas ao mesmo tempo.
- **Classes**: `PascalCase`, sempre — `UsersAuthService`,
  `UsersAuthRepository`, `UsersAuth`. (Nada de `Users_auth_service`.)
- **Models**: sufixo `Model` e nome no plural da tabela — `UsersModel`,
  com `__tablename__ = "users"`.
- **Factories de DI**: `get_<papel>` — `get_db`, `get_auth_service`.

## Anti-padrões

**Rota dentro de classe.** O decorator registra a função crua, antes de
existir qualquer instância — o FastAPI vê `self` como um parâmetro sem
tipo e transforma em **query param obrigatório**, que aparece no Swagger e
quebra a rota em runtime:

```python
# NÃO
class UsersController:
    @router.post("/register")
    def register_user(self, user_data: UsersAuth): ...
```

Rota é função de módulo. O que você queria guardar no `self` vira uma
dependência.

**Instanciar o service dentro da rota.** `service = UsersAuthService(...)`
no corpo da função mata a testabilidade — não tem como substituir por um
fake. Passe pela dependência.

**Model vazando pela API.** Não devolva um objeto SQLAlchemy direto na
resposta sem um schema no `-> ` da rota; o schema é o que corta as colunas
que não devem sair (a começar por `password`).

**Regra de negócio no controller.** Se a rota tem `if` decidindo negócio
(e não só traduzindo `None` para 404), ela provavelmente está fazendo o
trabalho do service.
