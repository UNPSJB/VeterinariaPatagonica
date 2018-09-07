from django.db import models

# Create your models here.

class Insumo (models.Model):
    nombre = models.CharField(max_length = 50, null = False, blank = False, primary_key = True)
    formaDePresentacion = models.CharField(max_length = 50, null = False, blank = False)
    precioPorUnidad = models.DecimalField(max_digits = 7, decimal_places = 2)
    rubro = models.CharField(max_length = 50, blank = False)
    baja = models.BooleanField(default = False)


    def __str__(self):
        return "Insumo: {0}.\nForma de Presentación: {1}.\nPrecio: {2}".format(self.nombre,self.formaDePresentacion,self.precioPorUnidad)
