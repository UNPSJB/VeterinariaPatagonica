from django.db import models
from Apps.GestionDeProductos import models as pmodels
from decimal import Decimal
from VeterinariaPatagonica import tools


class BaseServicioManager(models.Manager):
    pass

ServicioManager = BaseServicioManager.from_queryset(tools.BajasLogicasQuerySet)


class Servicio(models.Model):

    MAPPER ={
    "nombre": "nombre__icontains",
    }

    TIPO = (('C','Consulta'), ('Q','Quirurgica'),('I','Internación') )
    MAX_NOMBRE = 50
    MIN_NOMBRE = 2
    MAX_DESCRIPCION = 200
    MAX_PRECIO = 7
    MAX_DECIMAL = 2
    REGEX_NOMBRE = '^[0-9a-zA-Z-_ .]{1,100}$'

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
        max_length=MAX_NOMBRE,
        unique=True,
        null=False,
        blank=False,
        error_messages={
            'blank': "El nombre de servicio es obligarotio",
            'max_length': "El nombre puede tener a lo sumo {} caracteres".format(MAX_NOMBRE)
        }
    )
    descripcion = models.CharField(
        help_text='Ingrese la descripcion del Servicio',
        max_length=MAX_DESCRIPCION,
        unique=False,
        null=True,
        blank=True,
        error_messages={
            'max_length': "La descripcion puede tener a lo sumo {} caracteres".format(MAX_DESCRIPCION)
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
        max_digits = MAX_PRECIO,
        decimal_places = MAX_DECIMAL,
        unique=False,
        null=False,
        blank=False,
        error_messages={
            'blank': "El precio del servicio es obligarotio"
        }
    )

    productos = models.ManyToManyField(pmodels.Producto,
        through='ServicioProducto',
        through_fields=('servicio', 'producto'),
    )
    baja = models.BooleanField(
        help_text='Deshabilitado',
        default=False
        )

    objects = ServicioManager()

    def __str__(self):
        cadena = 'Nombre de Servicio: {0}, Duración Estimada: {1} Precio: {2}.'
        return cadena.format(self.nombre, self.tiempoEstimado, self.precioManoDeObra)

    def precio(self):
        productos = Decimal("0")
        for sproducto in self.servicioproducto_set.all():
            productos += sproducto.producto.precioEnUnidad(sproducto.cantidad)
        return self.precioManoDeObra + productos

class ServicioProducto(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    producto = models.ForeignKey(pmodels.Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
