FROM python:3.10-slim
WORKDIR /code
# Разделяем копирование requirements.txt от общего, так как он меняется гораздо реже, нежели основной код.
# Нет смысла пересобирать слой с зависимостями так же часто, как и основные слои.
COPY requirements.txt .
RUN pip3 install -r /code/requirements.txt --no-cache-dir
COPY . /code
CMD gunicorn -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker src.run_webhook_api:api
