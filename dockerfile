# STAGE 1: THE BUILDER (Clean Room)
# We use a perfect Linux image to compile the libraries.
FROM python:3.11-bookworm as builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install libraries safely here
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir mt5linux python-telegram-bot

# STAGE 2: THE BOT (Final)
# We just copy the libraries. No installation happens here.
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# Copy the "Brain" from Stage 1
COPY --from=builder /opt/venv /opt/venv

# Run the bot
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "export PATH=/opt/venv/bin:\$PATH" >> /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec python bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
