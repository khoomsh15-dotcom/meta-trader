# Use the pre-configured MT5-Wine environment which has Python
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root

# Skip apt-get to avoid Exit 100. The image already has Python
WORKDIR /app
COPY . /app

# Upgrade pip and install your bot requirements
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Start your Multi-User Bot OS
CMD ["python3", "bot.py"]
