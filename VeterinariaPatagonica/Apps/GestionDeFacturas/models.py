from django.db import models
from Apps.GestionDeProductos import models as proModel
from Apps.GestionDeClientes import models as cliModel
from django.core.validators import RegexValidator
from decimal import Decimal

# Create your models here.

REGEXTIPO = '^[A-B-C]{1}$'
MAXTIPO = 1
MAXDECIMAL = 2
MAXDIGITO = 6

class Factura(models.Model):

    tipo = models.CharField(
        help_text= "Tipo de factura",
        max_length=MAXTIPO,
        unique=False,
        null=False,
        blank=False,
        validators=[RegexValidator(regex=REGEXTIPO)],
        error_messages={
            'max_length': "El tipo de factura puede tener a lo sumo {} caracteres".format(MAXTIPO),
            'blank': "El tipo es obligatorio"
        }
    )

    cliente = models.ForeignKey(
        cliModel.Cliente,
        unique=False,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        error_messages={
            'blank': "El cliente es obligatorio"
        }
    )

    fecha = models.DateField(
        help_text="Fecha de la Factura",
        unique=False,
        null=False,
        blank=False,
        error_messages={
            'blank': "La fecha es obligatoria"
        }
    )

    deatalles = models.ManyToManyField(
        proModel.Producto,
        through='DetalleFactura',

    )
    
    total = models.IntegerField(
        help_text="Importe total de la Factura",
        unique=False,
        null=False,
        blank=False,
        error_messages={
            'blank': "El importe es obligatorio"
        }
    )

    baja = models.BooleanField(default=False)

    def __str__(self):
        cadena = 'Tipo de Factura: {0}, Cliente: {1} Total: {2}.'
        return cadena.format(self.tipo, self.cliente, self.total)

    def precioTotal(self):
        productos = Decimal("0")
        for detalle in self.detalleFactura.set.all():
            productos += detalle.producto.precioEnUnidad(detalle.producto, detalle.cantidad)
        return self.productos

    '''def  __unicode__(self):
        return self.total'''

class DetalleFactura(models.Model):
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        help_text="Ingrese numero de Factura",
        unique=False,
        null=False,
        blank=False,
        error_messages={
            'blank': "La Factura es obligatoria"
        }
    )

    producto = models.ForeignKey(
        proModel.Producto,
        on_delete=models.CASCADE,
        #help_text="Ingrese Producto",
        unique=False,
        null=False,
        blank=False,
        error_messages={
            'blank': "Debe ingresar al menos un producto"
        }
    )
    cantidad = models.IntegerField(
        help_text="Ingrese Cantidad",
        unique=False,
        null=False,
        blank=False,
        error_messages={
            'blank': "La cantidad es obligatoria"
        }
    )
    subtotal = models.DecimalField(
        null= True,
        help_text="Ingrese precio del producto",
        max_digits= MAXDIGITO,
        decimal_places= MAXDECIMAL,
    )

    def  __unicode__(self):
        return self.subtotal

