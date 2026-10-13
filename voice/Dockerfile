FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HUB_DISABLE_TELEMETRY=1 \
    HF_HOME=/models/.huggingface

WORKDIR /voice

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

RUN useradd --system --no-create-home whisper \
    && mkdir -p /models \
    && chown whisper /models
USER whisper

EXPOSE 9000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:9000/health', timeout=4)"

CMD ["uvicorn", "app.server:create_app", "--factory", "--host", "0.0.0.0", "--port", "9000"]
