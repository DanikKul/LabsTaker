FROM python:latest
LABEL authors="dankulakovich"
RUN mkdir "/bot"
COPY ./bot.py /bot/bot.py
COPY ./config.json /bot/config.json
COPY ./database.py /bot/database.py
COPY ./is_online.py /bot/is_online.py
COPY ./requirements.txt /bot/requirements.txt
COPY ./run_bot.sh /bot/run_bot.sh
WORKDIR "/bot"
RUN chmod +x run_bot.sh
RUN pip3 install -r requirements.txt
CMD ls