# -----------------------------------------------------------------
# STAGE 1: THE BUILDER (The "Clean Kitchen")
# We use a healthy Python system to download and prepare everything.
# -----------------------------------------------------------------
FROM python:3.10-slim AS builder
WORKDIR /build

# 1. Download libraries into a folder called /wheels
# This happens in a clean environment, so it WON'T fail.
RUN pip install --upgrade pip
RUN pip wheel --no-cache-dir --wheel-dir=/build/wheels \
    pandas \
    pandas-ta \
    numpy \
    pymongo[srv] \
    python-telegram-bot[job-queue] \
    python-dotenv \
    mt5linux

# -----------------------------------------------------------------
# STAGE 2: THE RUNNER (The "MT5 Room")
# Now we switch to the MT5 image and just copy the files over.
# -----------------------------------------------------------------
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# 2. Copy the pre-made files from the Builder stage
COPY --from=builder /build/wheels /app/wheels

# 3. Install from the local folder (No internet download needed here!)
RUN pip3 install --no-cache-dir --no-index --find-links=/app/wheels /app/wheels/*.whl

# 4. Setup the bot service
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec python3 bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
