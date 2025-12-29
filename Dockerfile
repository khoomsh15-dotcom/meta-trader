# Specialized MT5-Wine image for Linux servers
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# Install only Linux-compatible requirements
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "bot.py"]
