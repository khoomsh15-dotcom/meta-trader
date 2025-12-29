# Use the specialized MT5-Wine environment
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root

# Skip apt-get and go straight to app setup
WORKDIR /app
COPY . /app

# Install only Linux-compatible requirements
RUN pip3 install --no-cache-dir -r requirements.txt

# Start your Multi-User Bot OS
CMD ["python3", "bot.py"]
