FROM python:3.13-slim
WORKDIR /app
RUN pip install --no-cache-dir uv==0.12.9
COPY pyproject.toml uv.lock ./
COPY rates_brief ./rates_brief
RUN uv sync --frozen --no-dev
COPY config ./config
COPY data ./data
COPY evals ./evals
ENV PATH="/app/.venv/bin:$PATH" LLM_MODE=offline PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-m", "rates_brief"]
