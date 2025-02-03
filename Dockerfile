FROM python:3.9.12-slim AS builder
LABEL author=VolkanAkcora
LABEL "application_environment"="Production"
LABEL "version"=1.0
WORKDIR /usr/src/app
COPY ansible/roles/backend_stock_collector/files/stock_collector-1.0.0-py3-none-any.whl .

# Install dependencies and application
RUN apt-get update && apt-get install -y --no-install-recommends vim \
    && pip install --no-cache-dir stock_collector-1.0.0-py3-none-any.whl \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*

# Add non-root user
RUN useradd -m appuser
USER appuser
