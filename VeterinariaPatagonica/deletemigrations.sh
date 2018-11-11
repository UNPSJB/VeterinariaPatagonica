#!/bin/bash

for f in GestionDeRubros GestionDeClientes \
GestionDeFormasDePagos GestionDeProductos \
GestionDeMascotas GestionDeTiposDeAtencion \
GestionDeFacturas Usuarios \
GestionDeServicios GestionDePracticas
do
  rm ./Apps/$f/migrations -r
  mkdir ./Apps/$f/migrations
  touch ./Apps/$f/migrations/__init__.py
done
