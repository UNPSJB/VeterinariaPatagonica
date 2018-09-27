from django.db import models
from Apps.GestionDeInsumos import models as imodels
from decimal import Decimal

class Servicio(models.Model):
    TIPO = (('C','Consulta'), ('Q','Quirurgica'))

    tipo = models.CharField(max_length=1, choices=TIPO, default='Q')
    nombre = models.CharField(max_length=50, null=False, blank=False, help_text='Ingresa el nombre del Servicio')
    descripcion = models.CharField(max_length=200)
    tiempoEstimado = models.PositiveSmallIntegerField(help_text='Tiempo en minutos de Duración del Servicio')
    precioManoDeObra = models.DecimalField(max_digits = 7, decimal_places = 2)
    insumos = models.ManyToManyField(imodels.Insumo, 
        through='ServicioInsumo',
        through_fields=('servicio', 'insumo'), 
    )

    def __str__(self):
        cadena = 'Nombre de Servicio: {0}, Duración Estimada: {1} Precio: {2}.'
        return cadena.format(self.nombre, self.tiempoEstimado, self.precioManoDeObra)

    def precio(self):
        insumos = Decimal("0")
        for sinsumo in self.servicioinsumo_set.all():
            insumos += sinsumo.insumo.precioEnUnidad(sinsumo.cantidad)
        return self.precioManoDeObra + insumos

class ServicioInsumo(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    insumo = models.ForeignKey(imodels.Insumo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
