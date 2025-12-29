# STAGE 1: THE BUILDER (Old Linux "Bullseye")
FROM python:3.10-slim-bullseye as builder

# Setup virtual environment
RUN python -m venv /opt/venv --copies
ENV PATH="/opt/venv/bin:$PATH"

# Install libraries (with Numpy)
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --only-binary=:all: numpy
RUN pip install --no-cache-dir --only-binary=:all: rpyc
RUN pip install --no-cache-dir --no-deps mt5linux
RUN pip install --no-cache-dir python-telegram-bot aiohttp python-dotenv

# STAGE 2: THE BOT (Optimized for Low RAM)
FROM ghcr.io/gmag11/metatrader5-docker:latest

# 👇 RAM SAVING SETTINGS 👇
ENV VNC_RESOLUTION=800x600
ENV VNC_DEPTH=16
ENV NO_AUDIO=true
ENV WINE_LOG_LEVEL=error

USER root
WORKDIR /app
COPY . /app

# Copy necessary files from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=builder /usr/local/lib/libpython3.10.so.1.0 /usr/lib/libpython3.10.so.1.0
COPY --from=builder /usr/lib/x86_64-linux-gnu/libssl.so.1.1 /usr/lib/libssl.so.1.1
COPY --from=builder /usr/lib/x86_64-linux-gnu/libcrypto.so.1.1 /usr/lib/libcrypto.so.1.1

# Startup script
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "export LD_LIBRARY_PATH=/usr/lib:\$LD_LIBRARY_PATH" >> /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec /opt/venv/bin/python bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
