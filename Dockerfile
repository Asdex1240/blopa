FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /blopa

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

CMD ["python", "-m", "app.cli"]

FROM base AS dev

COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY pytest.ini .
COPY tests ./tests

CMD ["pytest", "-q"]
