FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
EXPOSE 5010
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5010/ops-api/health', timeout=4)" || exit 1

CMD ["sh", "-c", "python -c 'from app import init_db; init_db()' && exec gunicorn -w 2 -b 0.0.0.0:5010 --timeout 30 wsgi:app"]
