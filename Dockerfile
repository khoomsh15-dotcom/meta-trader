FROM ghcr.io/gmag11/metatrader5-docker:latest

USER root
WORKDIR /app
COPY . /app

# Linux-compatible libraries install karega
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "bot.py"]
