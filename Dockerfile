FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=webstore:create_app

WORKDIR /app

COPY setup.py /app/setup.py
COPY webstore /app/webstore
COPY test /app/test
COPY auxiliary_service.py /app/auxiliary_service.py
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir . \
    && chmod +x /app/docker-entrypoint.sh \
    && mkdir -p /app/instance

EXPOSE 5000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
