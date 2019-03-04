#!/bin/bash
set -ev

sudo service supervisor stop
sudo killall gunicorn -s TERM || true

source beevenueenv/bin/activate
pip install -r requirements.txt
pip install -r requirements.linuxonly.txt

echo "Running migrations"
/bin/bash ./flask.prod.sh db upgrade

sudo service supervisor start
