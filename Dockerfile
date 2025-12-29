# Use the specialized MT5-Wine image
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# Install dependencies (Linux compatible)
RUN pip3 install --no-cache-dir -r requirements.txt

# Start the bot
CMD ["python3", "bot.py"]
