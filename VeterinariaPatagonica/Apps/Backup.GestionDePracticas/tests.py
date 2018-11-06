from decimal import Decimal
from datetime import datetime
from django.test import TestCase
from . import models
from Apps.GestionDeServicios import models as srmodels
from Apps.GestionDeClientes import models as clmodels
from Apps.GestionDeTiposDeAtencion import models as tamodels
from Apps.GestionDeMascotas import models as mmodels

class PracticaTests(TestCase):
    def setUp(self):
        self.cliente = clmodels.Cliente.objects.create(
            nombres="Pepe",
            descuentoServicio=10,
            descuentoProducto=10,
            cuentaCorriente=0
        )
        self.servicio = srmodels.Servicio.objects.create(
            tiempoEstimado=120,
            precioManoDeObra=Decimal("300.00")
        )
        self.tipoAtencion = tamodels.TipoDeAtencion.objects.create(
            inicio_franja_horaria=datetime.now(),
            fin_franja_horaria=datetime.now()
        )
        self.mascota = mmodels.Mascota.objets.create(
            patente="ABC123"
            nombre="Snoopy"
            cliente=self.cliente
            fechaNacimiento=datetime.now()
            especie="Mestizo"
            )

        self.practica = models.Practica.new(
            nombre="Castracion",
            precio=100,
            cliente=self.cliente,
            servicio=self.servicio,
            tipoDeAtencion=self.tipoAtencion
        )

    def test_precio(self):
        #self.assertEqual(self.practica.precioReal(), Decimal("300.00"))
        pass

    def test_instanciar(self):
        p = models.Practica.objects.create(
            nombre="p1",
            precio=100,
            cliente=self.cliente,
            mascota=self.mascota,
            servicio=self.servicio,
            tipoDeAtencion=self.tipoAtencion)
        self.assertEquals(p.nombre, "p1")

    def test_crear(self):
        self.assertEqual(str(self.practica.estado()), "Creada")

    def test_presupuestar(self):
        self.practica.hacer("presupuestar",self.mascota, 10, 20)
        self.assertEqual(str(self.practica.estado()), "Presupuestada")

    def test_confirmar_presupuesto(self):
        self.practica.hacer("presupuestar",self.mascota, 10, 20)
        self.practica.hacer("confirmar", datetime.now())
        self.assertEqual(str(self.practica.estado()), "Programada")

    def test_confirmar(self):
        self.practica.hacer("programar", datetime.now())
        self.assertEqual(str(self.practica.estado()), "Programada")

    def test_confirmar(self):
        self.practica.hacer("presupuestar", 10, 20)
        self.practica.hacer("confirmar", datetime.now())
        self.practica.hacer("reprogramar", datetime.now(), "Falta veterinario")
        self.practica.hacer("reprogramar", datetime.now(), "Falta cliente")
        self.assertEqual(str(self.practica.estado()), "Programada")
