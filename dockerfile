# STAGE 1: THE BUILDER (Slim Image)
FROM python:3.11-slim as builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies (One by one to save RAM)
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --only-binary=:all: rpyc
RUN pip install --no-cache-dir --no-deps mt5linux
RUN pip install --no-cache-dir python-telegram-bot

# STAGE 2: THE BOT (Run it)
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# Copy the libraries
COPY --from=builder /opt/venv /opt/venv

# Run using the FULL PATH to python (Fixes the crash)
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec /opt/venv/bin/python bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
