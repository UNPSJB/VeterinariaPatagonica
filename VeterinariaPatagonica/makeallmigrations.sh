#!/bin/bash

for f in GestionDeRubros GestionDeClientes \
GestionDeFormasDePagos GestionDeProductos \
GestionDeMascotas GestionDeTiposDeAtencion \
GestionDeFacturas Usuarios \
GestionDeServicios GestionDePracticas
do
  python manage.py makemigrations $f
done
python manage.py migrate
