#!/bin/env sh
set -ev

p=`realpath test/testing_config.py`
env BEEVENUE_CONFIG_FILE=$p coverage run --branch --source=beevenue -m pytest $@ test
coverage report -m --skip-covered
