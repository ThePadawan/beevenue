#!/bin/env sh
set -ev

p=$(realpath beevenue_config.py)
q=$(realpath main.py)
env BEEVENUE_CONFIG_FILE="$p" FLASK_APP="$q" flask "$@"
