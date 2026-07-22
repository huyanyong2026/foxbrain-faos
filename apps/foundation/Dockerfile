FROM python:3.12-slim
WORKDIR /app
COPY apps/foundation/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/foundation /app/apps/foundation
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "apps.foundation.app:app", "--host", "0.0.0.0", "--port", "8000"]
