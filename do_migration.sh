#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python createadmin.py