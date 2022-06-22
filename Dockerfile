FROM python:3.10-slim
WORKDIR /code
COPY requirements.txt .
RUN pip3 install -r /code/requirements.txt --no-cache-dir
COPY . /code
CMD ["python3", "src/run_webhook_api.py"]
