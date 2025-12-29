# ==========================================
# STAGE 1: THE CLEAN ROOM (The "Builder")
# We use a full-sized Python image that has ALL compilers pre-installed.
# This ensures 'mt5linux' builds successfully without errors.
# ==========================================
FROM python:3.11-bookworm as builder

# 1. Create a "Virtual Environment" (The Brain)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 2. Install libraries safely here
# We use the clean room to compile/download everything.
RUN pip install --no-cache-dir --upgrade pip
# Force binary for numpy to save time/memory
RUN pip install --no-cache-dir --only-binary=:all: numpy
# Install the problem child: mt5linux
RUN pip install --no-cache-dir mt5linux python-telegram-bot python-dotenv

# ==========================================
# STAGE 2: THE BOT (The Final Container)
# We do NOT run 'pip install' here. We just copy the finished brain.
# ==========================================
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# 3. TRANSPLANT: Copy the entire library folder from Stage 1
# This puts the pre-built libraries directly into the bot.
COPY --from=builder /opt/venv /opt/venv

# 4. Setup the bot to use the transplanted Python
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "export PATH=/opt/venv/bin:\$PATH" >> /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec python bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
