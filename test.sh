#!/bin/env sh
set -ev

p=`realpath test/testing_config.py`
env STRAWBERRY_CONFIG_FILE=$p coverage run --branch --source=beevenue -m pytest test
