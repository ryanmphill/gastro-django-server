#!/bin/bash

rm db.sqlite3
rm -rf ./gastrognome_api/migrations
python3 manage.py migrate
python3 manage.py makemigrations gastrognome_api
python3 manage.py migrate gastrognome_api
python3 manage.py loaddata users
python3 manage.py loaddata tokens
python3 manage.py loaddata gastro_users
python3 manage.py loaddata categories
python3 manage.py loaddata ingredients
python3 manage.py loaddata genres
python3 manage.py loaddata recipes
python3 manage.py loaddata recipe_categories
python3 manage.py loaddata recipe_ingredients
python3 manage.py loaddata favorites
python3 manage.py loaddata follows