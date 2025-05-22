FROM python:3.12-alpine AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /project

COPY ./uv.lock ./pyproject.toml ./
RUN uv sync --compile-bytecode --no-cache --no-dev
ENV PATH="/project/.venv/bin:$PATH"

COPY . .

FROM base AS migrate
ENTRYPOINT ["alembic", "upgrade", "head"]

FROM base AS app
CMD ["fastapi", "run", "main.py"]
