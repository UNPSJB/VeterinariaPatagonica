from django.db import models

from VeterinariaPatagonica.Apps.GestionDeClientes.models import *

# Create your models here.

class Mascota(models.Model):
    patente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=35)
    cliente = models.ForeignKey(Cliente, null=False, blank=False, on_delete=models.CASCADE)
    fechaNacimiento = models.DateTimeField()
    especie = models.CharField(max_length=40)
    raza = models.CharField(max_length=40)

    def __str__ (self):
        return "{0}, {1}, {2}".format(self.nombre,self.especie,self.raza)

