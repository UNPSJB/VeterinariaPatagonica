import os
from django.test import TestCase

from . import models

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ProductosTestCase(TestCase):
    fixtures = [os.path.join(BASE_DIR, "../fixtures/datos.json")]
    
    def test_practica(self):
        self.assertEqual(models.Producto.objects.exists(), True)