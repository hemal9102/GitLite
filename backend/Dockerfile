FROM python:3.11-slim

WORKDIR /app

# system deps for psycopg2 and build
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV WEB_PORT=8080
ENV START_CMD="uvicorn app.main:app --host 0.0.0.0 --port ${WEB_PORT}"
CMD ["python", "wait_for_db.py"]
