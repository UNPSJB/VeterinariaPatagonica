from django.db import models
from Apps.GestionDeProductos import models as proModel
from Apps.GestionDeClientes import  models as cliModel
from django.core.validators import RegexValidator

# Create your models here.

REGEXTIPO = '^[A-B-C]{1}$'
MAXTIPO = 1

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

    def  __unicode__(self):
        return self.total

class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    producto = models.ForeignKey(proModel.Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.IntegerField()

    def  __unicode__(self):
        return self.subtotal

