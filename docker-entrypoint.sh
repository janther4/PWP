#!/bin/sh
set -e

python test/mockdata.py

exec flask run --host=0.0.0.0 --port=5000
