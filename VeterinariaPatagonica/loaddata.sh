#!/bin/bash

python3 manage.py loaddata ./fixtures/auth.json
for f in GestionDeRubros GestionDeClientes \
GestionDeMascotas GestionDeTiposDeAtencion \
Usuarios GestionDeFormasDePagos \
GestionDeProductos \
GestionDeServicios GestionDePracticas \
GestionDeFacturas
do
  echo "Load $f"
  python3 manage.py loaddata ./Apps/$f/fixtures/$f.json
done
