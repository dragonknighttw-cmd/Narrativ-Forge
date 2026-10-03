FROM python:3.12-slim AS runtime-base

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --create-home app

WORKDIR /app
COPY requirements.txt requirements-real-processing.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-real-processing.txt

FROM runtime-base AS runtime
WORKDIR /app
COPY --chown=app:app app ./app
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app alembic.ini ./
COPY --chown=app:app scripts ./scripts

ENV PYTHONUNBUFFERED=1
USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
