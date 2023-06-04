FROM python:latest
LABEL authors="dankulakovich"
COPY ./bot.py bot.py
COPY ./config.json config.json
COPY ./database.py database.py
COPY ./requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
CMD ls