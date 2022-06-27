FROM python:3.10-slim
WORKDIR /code
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
CMD uvicorn src.run_webhook_api:api --host 0.0.0.0 --port 8000 --reload
