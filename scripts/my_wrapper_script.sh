#!/bin/bash

./src/bot.py &

./src/bot_health_check.py &

wait -n

exit $?