FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# Install ONLY the essentials
RUN pip3 install --no-cache-dir mt5linux python-telegram-bot

# Run the bot
CMD ["python3", "bot.py"]
