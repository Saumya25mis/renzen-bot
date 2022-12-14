#!/bin/bash

chmod +x src/bot/bot.py
chmod +x src/bot/bot_health_check.py

python3 src/bot/bot.py &
python3 src/bot/bot_health_check.py &
wait -n

exit $?
