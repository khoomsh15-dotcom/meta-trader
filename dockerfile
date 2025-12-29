# STAGE 1: THE BUILDER (Old Linux "Bullseye")
FROM python:3.10-slim-bullseye as builder

# Setup virtual environment
RUN python -m venv /opt/venv --copies
ENV PATH="/opt/venv/bin:$PATH"

# Install libraries (ONLY ESSENTIALS)
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --only-binary=:all: numpy
RUN pip install --no-cache-dir --only-binary=:all: rpyc
RUN pip install --no-cache-dir --no-deps mt5linux
RUN pip install --no-cache-dir python-telegram-bot aiohttp

# STAGE 2: THE BOT (SURVIVAL MODE)
FROM ghcr.io/gmag11/metatrader5-docker:latest

# 👇 EXTREME RAM SAVING SETTINGS 👇
# Screen size of a 1990s Gameboy to save RAM
ENV VNC_RESOLUTION=320x240
ENV VNC_DEPTH=8
ENV NO_AUDIO=true
ENV WINE_LOG_LEVEL=error

USER root
WORKDIR /app
COPY . /app

# Copy files
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=builder /usr/local/lib/libpython3.10.so.1.0 /usr/lib/libpython3.10.so.1.0
COPY --from=builder /usr/lib/x86_64-linux-gnu/libssl.so.1.1 /usr/lib/libssl.so.1.1
COPY --from=builder /usr/lib/x86_64-linux-gnu/libcrypto.so.1.1 /usr/lib/libcrypto.so.1.1

# 👇 SLEEP 10 MINUTES
# This ensures the Installer has 100% of the RAM to finish.
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "export LD_LIBRARY_PATH=/usr/lib:\$LD_LIBRARY_PATH" >> /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "echo '💤 Sleeping for 10 minutes (Survival Mode)...'" >> /etc/services.d/telegram-bot/run && \
    echo "sleep 600" >> /etc/services.d/telegram-bot/run && \
    echo "echo '🚀 Waking up Python Bot!'" >> /etc/services.d/telegram-bot/run && \
    echo "exec /opt/venv/bin/python bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
