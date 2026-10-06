FROM python:3.13-slim

# Boas práticas de runtime Python em container
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Instala as dependências a partir do pyproject.toml (fonte de verdade).
# Copiamos o código junto porque o build backend precisa dele para
# empacotar o projeto.
COPY pyproject.toml README.md ./
COPY api ./api
COPY core ./core
COPY domains ./domains
COPY main.py ./

RUN pip install --upgrade pip && pip install .

# Alembic não faz parte do pacote, mas o container precisa dele para
# rodar as migrations.
COPY alembic.ini ./
COPY alembic ./alembic

# Usuário não-root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
