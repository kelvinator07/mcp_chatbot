FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install Python deps first so the layer caches across code-only changes.
COPY pyproject.toml ./
COPY app.py agent_config.py guardrails.py ./
RUN pip install -e .

# Copy the rest of the runtime files (welcome page + Chainlit config).
COPY chainlit.md ./
COPY .chainlit ./.chainlit

# Hugging Face Spaces routes traffic to port 7860.
EXPOSE 7860

CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "7860", "--headless"]
