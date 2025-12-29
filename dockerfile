# STAGE 1: THE BUILDER (Slim Image = More RAM available)
FROM python:3.11-slim as builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 1. Upgrade Pip (Small step)
RUN pip install --no-cache-dir --upgrade pip

# 2. Install RPYC first (The engine for MT5)
# We force binary to ensure it doesn't compile.
RUN pip install --no-cache-dir --only-binary=:all: rpyc

# 3. Install MT5Linux ALONE (No Dependencies)
# This prevents the RAM crash because it doesn't scan other files.
RUN pip install --no-cache-dir --no-deps mt5linux

# 4. Install Telegram Bot ALONE
RUN pip install --no-cache-dir python-telegram-bot

# STAGE 2: THE BOT (Final)
# Copy the installed files and run.
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# Copy the "Brain" from Stage 1
COPY --from=builder /opt/venv /opt/venv

# Run the bot
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "export PATH=/opt/venv/bin:\$PATH" >> /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec python bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
