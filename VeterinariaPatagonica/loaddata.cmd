echo "Load Gestion de Rubros"
python manage.py loaddata ./Apps/GestionDeRubros/fixtures/GestionDeRubros.json

echo "Load Gestion de Insumos"
python manage.py loaddata ./Apps/GestionDeProductos/fixtures/GestionDeProductos.json

echo "Load Gestion de Clientes"
python manage.py loaddata ./Apps/GestionDeClientes/fixtures/GestionDeClientes.json

echo "Load Gestion de Mascotas"
python manage.py loaddata ./Apps/GestionDeMascotas/fixtures/GestionDeMascotas.json

echo "Load Gestion de Servicios"
python manage.py loaddata ./Apps/GestionDeServicios/fixtures/GestionDeServicios.json

echo "Load Gestion de TiposDeAtencion"
python manage.py loaddata ./Apps/GestionDeTiposDeAtencion/fixtures/GestionDeTiposDeAtencion.json

echo "Load Gestion de Practicas"
python manage.py loaddata ./Apps/GestionDePracticas/fixtures/GestionDePracticas.json

echo "Load Gestion de Facturas"
python manage.py loaddata ./Apps/GestionDeFacturas/fixtures/GestionDeFacturas.json

python manage.py loaddata ./fixtures/auth.json
python manage.py loaddata ./Apps/Usuarios/fixtures/Usuarios.json