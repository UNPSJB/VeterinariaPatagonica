#!/bin/bash

for f in GestionDeInsumos GestionDeClientes \
GestionDeMascotas GestionDePracticas \
GestionDeServicios GestionDeTiposDeAtencion
do
  rm ./Apps/$f/migrations -r
  mkdir ./Apps/$f/migrations
  touch ./Apps/$f/migrations/__init__.py
done
