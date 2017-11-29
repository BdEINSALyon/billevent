#!/bin/sh
yes yes | python3 manage.py migrate && python3 manage.py collectstatic --noinput && gunicorn billetterie.wsgi -b 0.0.0.0:8000 --log-file -