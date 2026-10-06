DC = docker compose
API = $(DC) run --rm api

.PHONY: help up up-d down logs build restart ps \
        migration migrate downgrade history current \
        psql db-shell shell

help: 
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

## --- App ---
up: 
	$(DC) up

up-d:
	$(DC) up -d

down: 
	$(DC) down

logs: 
	$(DC) logs -f api

build: 
	$(DC) build

restart: 
	$(DC) restart api

ps: 
	$(DC) ps

## --- Migrations (Alembic) ---
migration: ## Cria migration via autogenerate. Uso: make migration m="msg"
	$(API) alembic revision --autogenerate -m "$(m)"

migrate: 
	$(API) alembic upgrade head

downgrade: 
	$(API) alembic downgrade -1

history: 
	$(API) alembic history

current: ## Mostra a revisão aplicada atualmente
	$(API) alembic current

## --- Acesso / debug ---
psql: ## Abre o psql no banco
	$(DC) exec db psql -U ecommerce -d ecommerce

db-shell: ## Abre um shell no container do Postgres
	$(DC) exec db bash

shell: ## Abre um shell no container da API
	$(API) bash
