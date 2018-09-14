from django.db import models
from VeterinariaPatagonica.Apps.GestionDeInsumos.models import Insumo
from django.views.generic.list import ListView
# Create your models here.
class ListaCantidades(ListView):
    l_cantidadInsumos = models.PositiveSmallIntegerField()

class ListaInsumos(ListView):
    l_insumos = Insumo

class Servicio(models.Model):
    t_tipo = (('C','Consulta'),('Q','Quirurgica'))
    tipo = models.CharField(max_length=25, choices=t_tipo, default='Tipo de Práctica aqui')
    nombre = models.CharField(max_length=50, null=False, blank=False,help_text="Ingresa el nombre del Servicio")
    descripcion = models.CharField(max_length=200)
    tiempoEstimado = models.TimeField(auto_now_add=False,help_text="Tiempo de Duración del Servicio")
    precioManoDeObra = models.PositiveSmallIntegerField()
    insumos = ListaInsumos
    cantidadInsumos = ListaCantidades


    def __str__(self):
        cadena = 'Nombre de Servicio: {0}, Duración Estimada: {1} Precio: {2}.'
        return cadena.format(self.nombre, self.tiempoEstimado, self.precioManoDeObra)
