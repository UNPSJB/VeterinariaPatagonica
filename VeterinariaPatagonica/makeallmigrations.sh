#!/bin/bash

for f in GestionDeMascotas GestionDePracticas
do
  python3 manage.py makemigrations $f
done
python3 manage.py migrate
