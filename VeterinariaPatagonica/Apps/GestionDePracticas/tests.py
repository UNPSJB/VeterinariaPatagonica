import os
from django.test import TestCase

from . import models

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class PracticasTestCase(TestCase):
    fixtures = [os.path.abspath(os.path.join(BASE_DIR, "../fixtures/datos.json"))]
    
    def test_existen_practicas(self):
        self.assertEqual(models.Practica.objects.exists(), True)
    
    def test_precio(self):
        p = models.Practica.objects.first()
        self.assertEqual(p.precioTotal(), 470)