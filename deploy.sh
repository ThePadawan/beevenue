#!/bin/bash
set -ev

sudo service supervisor stop
sudo killall gunicorn -s TERM || true

source beevenueenv/bin/activate
pip install -r requirements.txt
pip install -r requirements.linuxonly.txt

sed -i 's/\(COMMIT_ID = \)\(.*\)/\1\"'${REVISION:0:8}'\"/g' beevenue_config.prod.py

echo "Running migrations"
/bin/bash ./flask.prod.sh db upgrade

sudo service supervisor start
