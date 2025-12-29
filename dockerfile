# STAGE 1: THE BUILDER
FROM python:3.11-slim as builder

# ⚠️ CRITICAL FIX: Use --copies to avoid broken symlinks
RUN python -m venv /opt/venv --copies
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --only-binary=:all: rpyc
RUN pip install --no-cache-dir --no-deps mt5linux
RUN pip install --no-cache-dir python-telegram-bot aiohttp

# STAGE 2: THE BOT
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# Copy the FIXED venv (Real files, no shortcuts)
COPY --from=builder /opt/venv /opt/venv

# Run using the absolute path
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec /opt/venv/bin/python bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
