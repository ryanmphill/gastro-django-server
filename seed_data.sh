#!/bin/bash

rm db.sqlite3
rm -rf ./gastrognome_api/migrations
python3 manage.py migrate
python3 manage.py makemigrations gastrognome_api
python3 manage.py migrate gastrognome_api
python3 manage.py loaddata users
python3 manage.py loaddata tokens