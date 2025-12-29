# ---------------------------------------------------------
# STAGE 1: THE FACTORY (Standard Python Image)
# This image works perfectly. We use it to download the files.
# ---------------------------------------------------------
FROM python:3.10-slim AS factory
WORKDIR /build

# 1. Download all dependencies into a folder called /wheels
# Since this is a clean Linux, it will NOT fail.
RUN pip install --upgrade pip
RUN pip wheel --no-cache-dir --wheel-dir=/build/wheels \
    pandas \
    pandas-ta \
    numpy \
    pymongo[srv] \
    python-telegram-bot[job-queue] \
    python-dotenv \
    mt5linux

# ---------------------------------------------------------
# STAGE 2: THE DESTINATION (The MT5 Image)
# We switch to the restricted image but we DON'T download anything.
# ---------------------------------------------------------
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# 2. "Smuggle" the files from the Factory to here
COPY --from=factory /build/wheels /app/wheels

# 3. Install from the local folder (Offline Mode)
# We tell pip: "Don't go to the internet. Just use the files in /wheels"
RUN pip3 install --no-cache-dir --no-index --find-links=/app/wheels /app/wheels/*.whl

# 4. Create the Service to run the bot
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec python3 bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
