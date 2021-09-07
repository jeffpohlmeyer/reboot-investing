FROM python:3.8.10

WORKDIR /api

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY server/requirements.txt .
RUN pip install -r requirements.txt

COPY server .