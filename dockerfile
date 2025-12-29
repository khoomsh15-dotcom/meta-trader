FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Start the bot
CMD ["python3", "bot.py"]
