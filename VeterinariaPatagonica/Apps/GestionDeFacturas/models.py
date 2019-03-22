from django.db import models
from Apps.GestionDeProductos import models as proModel
from Apps.GestionDeClientes import models as cliModel
from django.core.validators import RegexValidator
from decimal import Decimal
from django.db.models import Q
from django.utils import timezone as djangotimezone
from Apps.GestionDePracticas import models as praModel
#from Apps.GestionDePagos import models as pagModel
# Create your models here.

from Apps.GestionDePracticas.models.practica import Practica

REGEXTIPO = '^[A-B-C]{1}$'
MAXTIPO = 1
MAXDECIMAL = 2
MAXDIGITO = 6

MAX_DIGITOS_AJUSTES = 5
MAX_DECIMALES_AJUSTES = 2

class Factura(models.Model):


    MAPPER = {
        "tipo": "tipo__icontains",
        "cliente": lambda value: Q(cliente__nombres__icontains=value) | Q(cliente__apellidos__icontains=value),
        "fecha": "fecha_icontains"
    }

    TIPODEFACTURA = (('A','A'), ('B','B'), ('C', 'C'))

    tipo = models.CharField(
        choices=TIPODEFACTURA,
        default='B',
        help_text= "Tipo de Factura.",
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
        help_text="Fecha de la Factura.",
        unique=False,
        null=False,
        blank=False,
        default=djangotimezone.now,
        error_messages={
            'blank': "La fecha es obligatoria"
        }
    )

    productos = models.ManyToManyField(
        proModel.Producto,
        through='DetalleFactura',
        through_fields=('factura', 'producto'),
    )

    total = models.IntegerField(
        help_text="Importe total de la Factura.",
        unique=False,
        null=False,
        default=0,
        blank=False,
        error_messages={
            'blank': "El importe es obligatorio"
        }
    )
    recargo = models.DecimalField(
            blank=False,
            null = False,
            default=Decimal(0),
            max_digits = MAX_DIGITOS_AJUSTES,
            decimal_places = MAX_DECIMALES_AJUSTES,
            error_messages = {},
            validators = []
    )

    descuento = models.DecimalField(
            blank=False,
            null = False,
            default=Decimal(0),
            max_digits = MAX_DIGITOS_AJUSTES,
            decimal_places = MAX_DECIMALES_AJUSTES,
            error_messages = {},
            validators = []
    )

    '''pago = models.OneToOneField(
        pagModel.Pago,
        on_delete = models.CASCADE,
        null = True,
        blank = True
    )'''

    practica = models.ForeignKey(
        praModel.Practica,
        on_delete = models.CASCADE,
        null = True,
        blank = True
    )

    baja = models.BooleanField(default=False)

    def __str__(self):
        cadena = 'Tipo de Factura: {0}, Cliente: {1} Total: {2}.'
        return cadena.format(self.tipo, self.cliente, self.total)

    def precioTotal(self, detalles):

        productos = Decimal("0")
        adelanto = Decimal("0")
        if not self.practica == None:
            practica = self.practica.precio
            print("PRECIO PRACTICA", practica)
            if self.practica.adelanto:
                adelanto = self.practica.adelanto.importe
            if (self.descuento!=0):
                descuentoPractica = (practica*self.descuento)/100
                practica = practica-descuentoPractica

                if (self.recargo!=0):
                    recargoPractica = practica/self.recargo
                    practica = practica+recargoPractica
        else:
            practica = 0
        for detalle in detalles:
            productos += detalle.subtotal
        print(practica,productos,adelanto)
        total = practica + productos - adelanto
        self.total = total
        # if self.tipo == "C":
        #     iva = round((total*21)/100)
        #     self.total = total-iva
        self.save()
        print("DESDE FACTURA",self.total)
        return self.total

    def calcular_subtotales(self, detalles):

        totalGuardado = self.total
        self.total = Decimal("0")
        # self.save()
        for detalle in detalles:
            detalle.factura = self
            detalle.save()
            self.total += detalle.subtotal
        # self.save()

    def calcular_descuento_practica(self):
        if not self.practica == None:
            practica = self.practica.precio

            if (self.descuento!=0):
                descuentoPractica = (practica*self.descuento)/100
                return descuentoPractica
            else:
                return 0
        else:
            return 0

    def calcular_recargo_practica(self):
        if not self.practica == None:
            practica = self.practica.precio
            if (self.recargo!=0):
                recargoPractica = (practica*self.recargo)/100
                return recargoPractica
            else:
                return 0
        else:
            return 0

    def calcular_iva(self):
        iva = round((self.total*21)/100)
        return iva

    def restar_iva(self):
        iva = Factura.calcular_iva(self)
        nuevoTotal = self.total - iva
        return nuevoTotal

    def importeVentas(self):
        return sum([
            detalle.subtotal for detalle in self.factura_productos.all()
        ])

    def importeServicios(self):
        return self.practica.estados.realizacion().total()

    def ajusteDescuento(self):
        importe = self.importeVentas() + self.importeServicios()
        return -( importe * self.descuento / Decimal(100) )

    def ajusteRecargo(self):
        importe = self.importeVentas() + self.importeServicios()
        return importe * self.recargo / Decimal(100)

    def importe(self):
        importe = self.importeVentas() + self.importeServicios()
        recargo = importe * self.recargo / Decimal(100)
        descuento = -(importe * self.descuento / Decimal(100))
        return importe + recargo + descuento


    class Meta:
        ordering = ["tipo", "fecha"]

    '''def  __unicode__(self):
        return self.total'''

class DetalleFactura(models.Model):

    class Meta:
        unique_together = ("factura", "producto")
        index_together = ["factura", "producto"]

    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        help_text="Ingrese numero de Factura",
        unique=False,
        null=False,
        blank=False,
        related_name="detalles_producto",
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
        related_name="detalles_factura",
        error_messages={
            'blank': "Debe ingresar al menos un producto"
        }
    )
    cantidad = models.PositiveIntegerField()

    subtotal = models.DecimalField(
        null= True,
        #help_text="Ingrese precio del producto",
        max_digits= MAXDIGITO,
        decimal_places= MAXDECIMAL,
    )

    def  __unicode__(self):
        return self.subtotal

    def precio(self):
        if self.cantidad != 0:
            return self.subtotal // self.cantidad

    """def save(self, *args, **kwargs):
        print("GUARDANDO...........")
        if (not "commit" in kwargs) or (kwargs["commit"]):
            if (self.subtotal is None):
                precio = self.producto.precioPorUnidad
                self.subtotal = precio * self.cantidad
                print("Precio: {}, Cantidad: {}, Subtotal: {}".format(precio, self.cantidad, self.subtotal))

        super().save(*args, **kwargs)"""

    def precioPorUnidad(self):
        return self.subtotal / Decimal(self.cantidad)

    def save(self, *args, **kwargs):
        if (not "commit" in kwargs) or kwargs["commit"]:
            self.subtotal = self.cantidad * self.producto.precioPorUnidad
        super().save(*args, **kwargs)