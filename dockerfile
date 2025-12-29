# Use the specialized MT5-Wine image
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# ---------------------------------------------------
# THE NUCLEAR FIX:
# NO APT UPDATE. NO PIP UPGRADE.
# JUST INSTALL THE LIBRARIES DIRECTLY.
# ---------------------------------------------------

# 1. Install Pandas & Numpy as BINARIES (Pre-built)
# We skip the 'upgrade pip' step that was crashing your build.
RUN pip3 install --no-cache-dir --only-binary=:all: pandas numpy

# 2. Install the rest of the libraries
RUN pip3 install --no-cache-dir \
    python-telegram-bot[job-queue] \
    pymongo[srv] \
    pandas-ta \
    python-dotenv \
    mt5linux

# 3. Setup the bot service to run alongside MT5
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec python3 bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
