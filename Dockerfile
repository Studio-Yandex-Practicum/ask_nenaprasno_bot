FROM python:3.10-slim
WORKDIR /code
# Разделяем копирование requirements.txt от общего, так как он меняется гораздо реже, нежели основной код.
# Нет смысла пересобирать слой с зависимостями так же часто, как и основные слои.
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
WORKDIR ./src
CMD uvicorn run_webhook_api:api --host 0.0.0.0 --port 8000 --reload
