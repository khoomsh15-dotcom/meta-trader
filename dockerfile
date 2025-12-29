# STAGE 1: THE BUILDER (Old Linux "Bullseye" for Compatibility)
FROM python:3.10-slim-bullseye as builder

# Create the virtual environment
RUN python -m venv /opt/venv --copies
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --only-binary=:all: rpyc
RUN pip install --no-cache-dir --no-deps mt5linux
RUN pip install --no-cache-dir python-telegram-bot aiohttp

# STAGE 2: THE BOT (The Patient)
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# 1. Copy the Virtual Environment (The Brain)
COPY --from=builder /opt/venv /opt/venv

# 2. Copy the Shared Library (The Blood)
# We use Python 3.10 now because it is more stable with Wine
COPY --from=builder /usr/local/lib/libpython3.10.so.1.0 /usr/lib/libpython3.10.so.1.0

# 3. Startup Script
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "export LD_LIBRARY_PATH=/usr/lib:\$LD_LIBRARY_PATH" >> /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec /opt/venv/bin/python bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
