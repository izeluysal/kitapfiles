FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

COPY . .

RUN mkdir -p /app/data /app/instance

EXPOSE 5003

CMD ["sh", "-c", "python -c \"from application import init_db; init_db()\" && gunicorn --bind 0.0.0.0:5003 --workers 2 application:app"]
