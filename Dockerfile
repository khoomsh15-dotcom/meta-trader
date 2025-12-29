# Use the specialized MT5-Wine environment
FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root

# Bypassing the network lock with forced flags
RUN apt-get clean && \
    DEBIAN_FRONTEND=noninteractive apt-get update -y --fix-missing && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3-pip \
    python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Upgrade pip and install the bot framework
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Start your Multi-User Bot OS
CMD ["python3", "bot.py"]
