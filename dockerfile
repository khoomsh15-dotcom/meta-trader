# ==========================================
# STAGE 1: THE CLEAN ROOM (Healthy Linux)
# We use a perfect OS to create the library folder.
# ==========================================
FROM python:3.11-slim-bookworm as builder

# 1. Create a "Virtual Environment" (The Brain)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 2. Install libraries safely here
# We force BINARY install for numpy so it never compiles (0% RAM crash risk)
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --only-binary=:all: numpy
RUN pip install --no-cache-dir mt5linux python-telegram-bot python-dotenv

# ==========================================
# STAGE 2: THE BOT (The Final Container)
# We do NOT run 'pip install' here. We just copy the brain.
# ==========================================
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# 3. TRANSPLANT: Copy the entire library folder from Stage 1
COPY --from=builder /opt/venv /opt/venv

# 4. Setup the bot to run automatically
# We tell it to use the python from our transplanted folder (/opt/venv)
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "export PATH=/opt/venv/bin:\$PATH" >> /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec python bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
