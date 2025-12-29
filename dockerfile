# Use the specialized MT5-Wine image
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# STEP 1: Fix Network & Install Builders (Crucial for Pandas)
# We use '|| true' to prevent the build from crashing if update server is slow
RUN apt-get update || true
RUN apt-get install -y build-essential python3-dev gcc

# STEP 2: Upgrade Pip (Solves 'Failed to build wheel' errors)
RUN pip3 install --upgrade pip setuptools wheel

# STEP 3: Install Your Packages (Directly here, no requirements.txt needed)
RUN pip3 install --no-cache-dir \
    python-telegram-bot[job-queue] \
    pymongo[srv] \
    pandas \
    pandas-ta \
    python-dotenv \
    mt5linux

# STEP 4: Start the Bot automatically with MT5
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec python3 bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
