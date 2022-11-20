#!/bin/bash

chmod +x src/bot.py
chmod +x src/bot_health_check.py

./src/bot.py &
./src/bot_health_check.py &

wait -n

exit $?