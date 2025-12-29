# STAGE 1: THE BUILDER (Old Linux "Bullseye")
FROM python:3.10-slim-bullseye as builder

# Create venv
RUN python -m venv /opt/venv --copies
ENV PATH="/opt/venv/bin:$PATH"

# Install libraries
RUN pip install --no-cache-dir --upgrade pip

# 1. CRITICAL FIX: Install Numpy (The Missing Muscle)
# We force binary to ensure it installs instantly without building.
RUN pip install --no-cache-dir --only-binary=:all: numpy

# 2. Install other libs
RUN pip install --no-cache-dir --only-binary=:all: rpyc
RUN pip install --no-cache-dir --no-deps mt5linux
RUN pip install --no-cache-dir python-telegram-bot aiohttp

# STAGE 2: THE BOT
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# 1. Copy the Venv
COPY --from=builder /opt/venv /opt/venv

# 2. Copy the Standard Library
COPY --from=builder /usr/local/lib/python3.10 /usr/local/lib/python3.10

# 3. Copy the System Library
COPY --from=builder /usr/local/lib/libpython3.10.so.1.0 /usr/lib/libpython3.10.so.1.0

# 4. Copy SSL Security Libraries
COPY --from=builder /usr/lib/x86_64-linux-gnu/libssl.so.1.1 /usr/lib/libssl.so.1.1
COPY --from=builder /usr/lib/x86_64-linux-gnu/libcrypto.so.1.1 /usr/lib/libcrypto.so.1.1

# 5. Run Script
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "export LD_LIBRARY_PATH=/usr/lib:\$LD_LIBRARY_PATH" >> /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec /opt/venv/bin/python bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
