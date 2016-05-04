#!/bin/sh

rm -f db.sqlite3
rm -f user_manager/migrations/*.py
touch user_manager/migrations/__init__.py
rm -f appt_mgmt/migrations/*.py
touch appt_mgmt/migrations/__init__.py

