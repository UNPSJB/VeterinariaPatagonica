from django.db import models

# Create your models here.

class Mascota(models.Model):

    patente = models.AutoField(max_length=4)
    nombre = models.CharField(max_length=35)
    fechaNacimiento = models.DateTimeField()
    especie = models.CharField(max_length=40)
    raza = models.CharField(max_length=40)

