FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python", "telebot_service.py"]
