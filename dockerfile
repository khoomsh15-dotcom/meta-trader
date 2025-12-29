# Use the specialized MT5-Wine image
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# STEP 1: Upgrade Pip internally (No internet update needed)
RUN python3 -m pip install --upgrade pip

# STEP 2: Install Pandas as a BINARY only (The Magic Fix)
# We force it to use a pre-built file so we don't need the broken 'gcc' tools
RUN pip3 install --no-cache-dir --only-binary=:all: pandas numpy

# STEP 3: Install the rest of your bot
RUN pip3 install --no-cache-dir \
    python-telegram-bot[job-queue] \
    pymongo[srv] \
    pandas-ta \
    python-dotenv \
    mt5linux

# STEP 4: Start the Bot Service
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec python3 bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
