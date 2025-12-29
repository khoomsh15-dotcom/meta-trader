# Specialized Wine/MT5 image for Linux servers
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root

# Fix for Exit Code 100: Adding retries and clearing cache
RUN apt-get clean && \
    apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends python3-pip python3-setuptools && \
    rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "bot.py"]
