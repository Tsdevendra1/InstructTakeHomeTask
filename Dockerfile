FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /app

WORKDIR /app
RUN uv sync --frozen --no-cache

# NOTE: I'm running using "dev" here but if we wanted in prod mode we would use "run"
CMD ["/app/.venv/bin/fastapi", "dev", "main.py", "--port", "8000", "--host", "0.0.0.0"]
