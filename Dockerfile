FROM python:3.8.13-slim-buster

ENV PYTHONUNBUFFERED 1

WORKDIR /mqtt-api

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update
RUN apt-get install -y netcat

COPY . .

EXPOSE 8000