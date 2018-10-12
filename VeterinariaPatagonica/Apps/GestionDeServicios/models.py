from django.db import models
from Apps.GestionDeInsumos import models as imodels
from decimal import Decimal

class Servicio(models.Model):
    TIPO = (('C','Consulta'), ('Q','Quirurgica'))
    MAXNOMBRE = 50
    MAXDESCRIPCION = 200

    tipo = models.CharField(
        help_text="Tipo de Servicio (Consulta-Cirugia)",
        max_length=1,
        unique=False,
        null=False,
        blank=False,
        choices=TIPO,
        default='Q',
        error_messages={
            'blank': "El tipo de servicio es obligarotio"
        }
    )

    nombre = models.CharField(
        help_text='Ingrese el nombre del Servicio',
        max_length=MAXNOMBRE,
        unique=True,
        null=False,
        blank=False,
        error_messages={
            'blank': "El nombre de servicio es obligarotio",
            'max_length': "El nombre puede tener a lo sumo {} caracteres".format(MAXNOMBRE)
        }

    )

    descripcion = models.CharField(
        help_text='Ingrese la descripcion del Servicio',
        max_length=MAXDESCRIPCION,
        unique=False,
        null=True,
        blank=True,
        error_messages={
            'max_length': "La descripcion puede tener a lo sumo {} caracteres".format(MAXDESCRIPCION)
        }
    )

    tiempoEstimado = models.PositiveSmallIntegerField(
        help_text='Tiempo en minutos de Duración del Servicio',
        unique=False,
        null=False,
        blank=False,
        error_messages={
            'blank': "El tiempo estimado del servicio es obligarotio"
        }
    )

    precioManoDeObra = models.DecimalField(
        max_digits = 7,
        decimal_places = 2)

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
