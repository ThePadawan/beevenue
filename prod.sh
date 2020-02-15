#!/bin/env sh
set -ev
source beevenueenv/bin/activate
p=$(realpath beevenue_config.prod.py)
# Some requests may run longer than the default timout of 30s
env BEEVENUE_CONFIG_FILE="$p" gunicorn --workers 4 --timeout 90 -b 0.0.0.0:7000 main:app