# Ecommerce API

API em FastAPI.

O padrão de código (camadas, injeção de dependência, como adicionar um
domínio novo) está em [ARCHITECTURE.md](ARCHITECTURE.md).

## Rodar localmente

```bash
python -m venv .venv
.venv/Scripts/Activate.ps1        # Windows PowerShell
pip install -e .
uvicorn main:app --reload
```

Acesse:

- http://127.0.0.1:8000/api/v1/ — endpoint raiz
- http://127.0.0.1:8000/docs — Swagger UI

## Rodar com Docker

```bash
docker build -t ecommerce-api .
docker run --rm -p 8000:8000 ecommerce-api
```

Ou em modo dev com hot-reload:

```bash
docker compose up
```

## Migrations (Alembic) via Docker

Os comandos abaixo rodam o Alembic **dentro** do container `api`, então
não precisa de Python/venv na máquina e funcionam **igual no Windows
(PowerShell ou cmd) e no Linux** — é só `docker compose`.

O Postgres sobe sozinho como dependência; `--rm` remove o container
temporário ao final.

```bash
# Subir o banco (deixe rodando em outro terminal, ou use -d)
docker compose up -d db

# Criar uma migration a partir das mudanças nos models (autogenerate)
docker compose run --rm api alembic revision --autogenerate -m "descricao"

# Aplicar todas as migrations pendentes
docker compose run --rm api alembic upgrade head

# Reverter a última migration
docker compose run --rm api alembic downgrade -1

# Ver a revisão aplicada atualmente / histórico
docker compose run --rm api alembic current
docker compose run --rm api alembic history
```

> A URL de conexão vem de `core/config.py` (`sqlalchemy_url`), montada a
> partir das variáveis `POSTGRES_*` já definidas no `docker-compose.yml`.
> Os arquivos gerados em `alembic/versions/` devem ser commitados.

## Comandos úteis

### Banco de dados (psql)

```bash
# Abrir o psql direto no banco
docker compose exec db psql -U ecommerce -d ecommerce

# Rodar um SQL sem entrar no shell interativo
docker compose exec db psql -U ecommerce -d ecommerce -c "\dt"
```

Dentro do psql: `\dt` lista tabelas, `\d <tabela>` descreve uma tabela,
`\l` lista os bancos, `\q` sai.

### Containers

```bash
docker compose up -d          # sobe tudo em background
docker compose ps             # lista os containers do projeto
docker compose logs -f api    # segue os logs da API
docker compose exec api bash  # shell dentro do container da API
docker compose down           # para e remove os containers
docker compose down -v        # idem, apagando também o volume do Postgres (zera o banco)
```

### Atalhos com `make`

Se você tem `make` (Linux/Mac/WSL/git-bash), os comandos acima têm atalhos.
No **Windows nativo** (PowerShell/cmd) sem `make`, use os comandos
`docker compose ...` acima — eles funcionam em qualquer sistema.

```bash
make help                          # lista todos os atalhos
make up-d                          # docker compose up -d
make migration m="create products"    # cria migration (autogenerate)
make migrate                       # aplica migrations (upgrade head)
make psql                          # abre o psql
make logs                          # segue os logs da API
```
