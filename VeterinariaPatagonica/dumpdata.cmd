echo "Dumpdataeando Gestion de Insumos"
python manage.py dumpdata GestionDeInsumos > ./Apps/GestionDeInsumos/fixtures/GestionDeInsumos.json

echo "Dumpdataeando Gestion de Clientes"
python manage.py dumpdata GestionDeClientes > ./Apps/GestionDeClientes/fixtures/GestionDeClientes.json

echo "Dumpdataeando Gestion de Mascotas"
python manage.py dumpdata GestionDeMascotas > ./Apps/GestionDeMascotas/fixtures/GestionDeMascotas.json

echo "Dumpdataeando Gestion de Practicas"
python manage.py dumpdata GestionDePracticas > ./Apps/GestionDePracticas/fixtures/GestionDePracticas.json

echo "Dumpdataeando Gestion de Servicios"
python manage.py dumpdata GestionDeServicios > ./Apps/GestionDeServicios/fixtures/GestionDeServicios.json

echo "Dumpdataeando Gestion de TiposDeAtencion"
python manage.py dumpdata GestionDeTiposDeAtencion > ./Apps/GestionDeTiposDeAtencion/fixtures/GestionDeTiposDeAtencion.json