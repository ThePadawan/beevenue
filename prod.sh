#!/bin/env sh
set -ev
source beevenueenv/bin/activate
p=`realpath beevenue_config.prod.py`
env BEEVENUE_CONFIG_FILE=$p gunicorn -b 0.0.0.0:7000 main:app