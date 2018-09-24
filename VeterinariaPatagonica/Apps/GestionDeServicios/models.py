from django.db import models
from Apps.GestionDeInsumos.models import Insumo
from django.views.generic.list import ListView

# Create your models here.
#class CantidadList(ListView):
#   cantidadInsumos = models.PositiveSmallIntegerField()


class InsumosList(ListView):
    insumo = models.ForeignKey(Insumo, null=False, blank=False, on_delete=models.CASCADE)
    cantidadInsumo = models.PositiveSmallIntegerField

class Servicio(models.Model):
    t_tipo = (('C','Consulta'),('Q','Quirurgica'))
    tipo = models.CharField(max_length=25, choices=t_tipo, default='Tipo de Práctica aqui')
    nombre = models.CharField(max_length=50, null=False, blank=False, help_text='Ingresa el nombre del Servicio')
    descripcion = models.CharField(max_length=200)
    insumos = InsumosList
    #cantidadInsumos = CantidadList
    tiempoEstimado = models.TimeField(auto_now=False, help_text='Tiempo de Duración del Servicio')
    precioManoDeObra = models.PositiveSmallIntegerField()


    def __str__(self):
        cadena = 'Nombre de Servicio: {0}, Duración Estimada: {1} Precio: {2}.'
        return cadena.format(self.nombre, self.tiempoEstimado, self.precioManoDeObra)
