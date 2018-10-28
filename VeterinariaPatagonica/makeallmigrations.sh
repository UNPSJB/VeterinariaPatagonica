#!/bin/bash

for f in GestionDeRubros GestionDeClientes \
GestionDeFormasDePagos GestionDeProductos \
GestionDeMascotas GestionDeTiposDeAtencion \
GestionDeServicios GestionDePracticas
do
  python3 manage.py makemigrations $f
done
python3 manage.py migrate
