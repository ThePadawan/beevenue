#!/bin/sh
set -ev
ARR=""

{%- for id in medium_ids %}
ARR="${ARR} {{ id }}"
{%- endfor %}

for i in ${ARR}; do
  curl {{ base_url }}medium/$i/backup --cookie "session={{session_cookie}}" -O -J -L
done
