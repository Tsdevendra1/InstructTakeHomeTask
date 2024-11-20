FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /app

WORKDIR /app
RUN uv sync --frozen --no-cache

# NOTE: I'm running using "dev" here but if we wanted in prod mode we would use "run". However, I think there are more general improvements I could make to the Dockerfile to make it production ready. This is just a quick example to get it running.
CMD ["/app/.venv/bin/fastapi", "dev", "main.py", "--port", "8000", "--host", "0.0.0.0"]
