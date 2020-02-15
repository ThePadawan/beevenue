#!/bin/env sh
set -ev

p=$(realpath beevenue_config.py)
env BEEVENUE_CONFIG_FILE="$p" python main.py