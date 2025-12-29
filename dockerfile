# STAGE 1: THE BUILDER (Healthy Python Image)
FROM python:3.11-slim as builder

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

# 2. CRITICAL FIX: Copy the missing Shared Library (The Blood)
# We take this file from the builder because the MT5 image doesn't have it.
COPY --from=builder /usr/local/lib/libpython3.11.so.1.0 /usr/lib/libpython3.11.so.1.0

# 3. Create the startup script with the library path linked
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "export LD_LIBRARY_PATH=/usr/lib:\$LD_LIBRARY_PATH" >> /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec /opt/venv/bin/python bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
