FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

#https://stackoverflow.com/questions/72417541/docker-compose-how-to-create-a-volume-to-save-only-one-file/72418667#72418667
RUN touch /app/db.sqlite
