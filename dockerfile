FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# 1. Install Numpy as a BINARY (Crucial Step)
# This forces the pre-built version so it doesn't use RAM to compile.
RUN pip3 install --no-cache-dir --only-binary=:all: numpy

# 2. Install mt5linux WITHOUT dependencies
# This stops it from checking for things that might break the build.
RUN pip3 install --no-cache-dir --no-deps mt5linux

# 3. Install the rest (rpyc is the engine for mt5linux)
RUN pip3 install --no-cache-dir rpyc python-telegram-bot python-dotenv

# Start the bot
CMD ["python3", "bot.py"]
