#!/bin/bash

cd /bot || exit
python3 bot.py >> logs_bot.txt &
python3 is_online.py >> logs_online.txt
echo "something"
