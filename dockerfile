FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# Upgrade pip to be safe
RUN pip3 install --no-cache-dir --upgrade pip

# Install the LITE requirements (No heavy Pandas)
RUN pip3 install --no-cache-dir -r requirements.txt

# Start the bot
RUN mkdir -p /etc/services.d/telegram-bot && \
    echo "#!/usr/bin/with-contenv bash" > /etc/services.d/telegram-bot/run && \
    echo "cd /app" >> /etc/services.d/telegram-bot/run && \
    echo "exec python3 bot.py" >> /etc/services.d/telegram-bot/run && \
    chmod +x /etc/services.d/telegram-bot/run
