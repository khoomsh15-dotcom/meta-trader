FROM ghcr.io/gmag11/metatrader5-docker:latest
USER root
RUN apt-get update && apt-get install -y python3-pip
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
CMD ["python3", "bot.py"]
