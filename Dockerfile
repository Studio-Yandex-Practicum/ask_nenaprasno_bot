FROM python:3.10-slim
WORKDIR /code
<<<<<<< HEAD
# Разделяем копирование requirements.txt от общего, так как он меняется гораздо реже, нежели основной код.
# Нет смысла пересобирать слой с зависимостями так же часто, как и основные слои.
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
CMD uvicorn src.run_webhook_api:api --host 0.0.0.0 --port 8000 --reload
=======
COPY requirements.txt .
RUN pip3 install -r /code/requirements.txt --no-cache-dir
COPY . /code
CMD gunicorn -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker src.run_webhook_api:api
>>>>>>> 1294be9 (Dockerfile support added)
