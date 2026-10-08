#!/bin/sh

set -e

python manager.py wait_for_db
python manager.py collectstatic --noinput
python manager.py migrate

uwsgi --socket :9000 --workers 4 --master --enable-theads --module app.wsgi