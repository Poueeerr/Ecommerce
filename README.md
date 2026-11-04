# Ecommerce

Projeto dividido em duas aplicações independentes:

- [`backend/`](./backend): API FastAPI, banco PostgreSQL, migrations Alembic e
  regras de negócio organizadas por domínio.
- [`frontend/`](./frontend): aplicação React + TypeScript + Vite para catálogo
  e autenticação.

## Estrutura e Git

Cada aplicação tem seu próprio `.git`, dependências, variáveis de ambiente,
testes e README. O diretório raiz é apenas um organizador. Para trabalhar em
uma aplicação, entre no diretório correspondente antes de executar comandos
Git ou criar commits:

```bash
cd backend && git status
cd ../frontend && git status
```

## Executar localmente

### Backend

```bash
cd backend
uv sync
cp .env.example .env
uv run uvicorn main:app --reload
```

O backend usa `http://localhost:8000`; Swagger: `http://localhost:8000/docs`.
Para PostgreSQL e RabbitMQ, use `docker compose up -d`.

### Frontend

Em outro terminal:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

O frontend usa `VITE_API_BASE_URL=http://localhost:8000/api/v1`. A API já
permite as origens de desenvolvimento `localhost:5173` e `127.0.0.1:5173`.

## Quality gates

```bash
cd backend && uv run pytest && uv run ruff check .
cd frontend && npm run typecheck && npm run lint && npm test && npm run build
```

O frontend atualmente integra o catálogo paginado (`GET /products/paginated`)
e o fluxo de login/perfil (`POST /users/login`, `GET /users/me`). As demais
rotas da API permanecem disponíveis no Swagger para evolução das próximas
features.
