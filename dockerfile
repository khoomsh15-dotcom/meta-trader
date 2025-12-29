# ---------------------------------------------------------
# STAGE 1: THE HEAVY FACTORY (Full Python Image)
# We changed 'slim' to the full version so it has ALL build tools.
# ---------------------------------------------------------
FROM python:3.10 AS factory
WORKDIR /build

# 1. Update Pip to the latest version
RUN pip install --upgrade pip

# 2. Download wheels (Binaries)
# We use --prefer-binary to tell it: "Don't build if you don't have to."
RUN pip wheel --no-cache-dir --wheel-dir=/build/wheels --prefer-binary \
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

# 3. "Smuggle" the files from the Factory to here
COPY --from=factory /build/wheels /app/wheels

# 4. Install from the local folder (Offline Mode)
# The --no-index flag forces it to use ONLY our smuggled files.
RUN pip3 install --no-cache-dir --no-index --find-links=/app/wheels /app/wheels/*.whl

# 5. Create the Service to run the bot
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec python3 bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
