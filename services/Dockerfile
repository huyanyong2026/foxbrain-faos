FROM python:3.12-alpine
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY packages /app/packages
COPY services /app/services
ENV PYTHONPATH=/app
ARG SERVICE_MODULE
ENV SERVICE_MODULE=${SERVICE_MODULE}
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 CMD wget -qO- http://127.0.0.1:8080/health >/dev/null || exit 1
CMD ["sh", "-c", "python -m services.${SERVICE_MODULE}.app"]
