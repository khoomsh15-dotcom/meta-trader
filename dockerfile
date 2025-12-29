# ---------------------------------------------------------
# STAGE 1: THE CLEAN BUILDER (Low Memory Mode)
# We use a standard Python image to prepare the environment safely.
# ---------------------------------------------------------
FROM python:3.10-slim AS builder

# 1. Create a "Virtual Environment" (Sandbox)
RUN python -m venv /opt/venv
# Activate the sandbox
ENV PATH="/opt/venv/bin:$PATH"

# 2. Upgrade pip inside the sandbox
RUN pip install --upgrade pip

# 3. INSTALL STEP A: HEAVY LIBRARIES (Binary Only)
# We force binary to prevent RAM spikes that crash Render.
RUN pip install --no-cache-dir --only-binary=:all: pandas numpy

# 4. INSTALL STEP B: LIGHT LIBRARIES
# We install these separately to keep the build stable.
RUN pip install --no-cache-dir \
    python-telegram-bot[job-queue] \
    pymongo[srv] \
    pandas-ta \
    python-dotenv \
    mt5linux

# ---------------------------------------------------------
# STAGE 2: THE FINAL BOT (MT5 Image)
# We just copy the Sandbox. No downloading, no building.
# ---------------------------------------------------------
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# 5. COPY the entire Sandbox folder from Stage 1
COPY --from=builder /opt/venv /opt/venv

# 6. Tell the system to use our Sandbox Python
ENV PATH="/opt/venv/bin:$PATH"

# 7. Start the bot using the Sandbox Python
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec python bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
