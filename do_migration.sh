#!/bin/sh

python manage.py makemigrations
echo
echo "==== migrations made ===="
echo
python manage.py migrate
echo
echo "==== migrations done ===="
echo
python createadmin.py
echo
echo "==== admins made ===="
echo