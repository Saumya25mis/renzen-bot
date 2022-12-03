#!/bin/bash

chmod +x src/bot.py
chmod +x src/bot_health_check.py

python3 src/bot.py &
python3 src/bot_health_check.py &
wait -n

exit $?
