#!/bin/bash
echo "Dumpdataeando auth"
python3 manage.py dumpdata auth > ./fixtures/auth.json
for f in GestionDeClientes GestionDeMascotas \
GestionDeRubros GestionDeFormasDePagos \
Usuarios GestionDePagos \
GestionDeProductos GestionDeServicios \
GestionDeTiposDeAtencion GestionDePracticas \
GestionDeFacturas
do 
 echo "Dumpdataeando $f"
 mkdir -p ./Apps/$f/fixtures
 python3 manage.py dumpdata $f > ./Apps/$f/fixtures/$f.json
done
