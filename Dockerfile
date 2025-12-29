# Use a pre-configured image for MT5 on Linux
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
RUN apt-get update && apt-get install -y python3-pip
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt

# Start the bot
CMD ["python3", "bot.py"]
