from django.db import models

from Apps.GestionDeClientes import models as gcmodels

# Create your models here.

class Mascota(models.Model):
    patente = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=35)
    cliente = models.ForeignKey(gcmodels.Cliente, null=False, blank=False, on_delete=models.CASCADE)
    fechaNacimiento = models.DateTimeField()
    especie = models.CharField(max_length=40)
    raza = models.CharField(max_length=40)

    def __str__ (self):
        return "{0}, {1}, {2}".format(self.nombre,self.especie,self.raza)

