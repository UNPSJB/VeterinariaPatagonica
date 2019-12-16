from decimal import Decimal
from datetime import datetime

from django.db import models
from django.core.validators import RegexValidator, MinValueValidator

from VeterinariaPatagonica.tools import R
from Apps.GestionDeProductos import models as proModel
from Apps.GestionDeClientes import models as cliModel
from Apps.GestionDePracticas.models.practica import Practica
from Apps.GestionDePagos.models import Pago

REGEXTIPO = '^[A-B-C]{1}$'
MAXTIPO = 1
MAXDECIMAL = 2
MAXDIGITO = 8

MAX_DIGITOS_AJUSTES = 5
MAX_DECIMALES_AJUSTES = 2



class ListadosQuerySet(models.QuerySet):

    def listado(self, campos=[], cabeceras=[], funciones=[]):
        retorno = ""
        for i in range(len(campos)):
            cabecera = cabeceras[i]
            retorno = retorno + cabecera + ","
        retorno = retorno + "\n"
        for obj in self:
            for i in range(len(campos)):
                campo = campos[i]
                valor = getattr(obj, campo)
                funcion = funciones[i]
                retorno = retorno + funcion(valor) + ","
            retorno = retorno + "\n"
        return retorno

    MAPEO_ORDEN = {
        "id" : ["id"],
        "tipo" : ["tipo"],
        "total" : ["total"],
        "fecha" : ["fecha"],
        "cliente" : ["cliente__apellidos", "cliente__nombres"],
        "precioPractica" : ["practica__precio"],
        "pago" : ["pago__importeTotal"],
        "fechaPago" : ["pago__fecha"],
        "importeVentas" : ["importe_ventas"],
    }

    MAPEO_FILTRADO = {
        "importe_desde" : "total__gte",
        "importe_hasta" : "total__lte",
        "tipo": "tipo",
        "cliente": lambda value: R(
            cliente__dniCuit__icontains=value,
            cliente__nombres__icontains=value,
            cliente__apellidos__icontains=value
        ),
        "fecha_desde": "fecha__gte",
        "fecha_hasta": "fecha__lte",
        "productos" : lambda values: R(*[
            R(
                productos__nombre__icontains=value,
                productos__descripcion__icontains=value,
                productos__marca__icontains=value
            ) for value in values
        ]),
        "rubros" : lambda values: R(*[
            R(
                productos__rubro__nombre__icontains=value,
                productos__rubro__descripcion__icontains=value
            ) for value in values
        ])
    }


ListadoManager = models.Manager.from_queryset(ListadosQuerySet)


#[TODO]: Agregar descuentos de cliente al calcular importes
class Factura(models.Model):

    class Meta:
        ordering = ["-fecha", "tipo"]
        permissions=(
            ("factura_crear", "crear"),
            ("factura_ver_pagas", "ver"),
            ("factura_ver_no_pagas", "ver"),
            ("factura_listar_pagas", "listar pagas"),
            ("factura_listar_no_pagas", "listar no pagas"),
            ("factura_exportar_xlsx_pagas", "exportar a formato xlsx pagas"),
            ("factura_exportar_xlsx_no_pagas", "exportar a formato xlsx no pagas"),
        )
        default_permissions = ()
        unique_together = (
            ("id", "practica"),
        )

    MAPPER = {
        "tipo": "tipo__icontains",
        "cliente": lambda value: models.Q(cliente__nombres__icontains=value) | models.Q(cliente__apellidos__icontains=value),
        "fecha": "fecha_icontains"
    }

    TIPODEFACTURA = (('A','A'), ('B','B'), ('C', 'C'))

    objects = ListadoManager()

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
        default=datetime.now,
        error_messages={
            'blank': "La fecha es obligatoria"
        }
    )

    productos = models.ManyToManyField(
        proModel.Producto,
        through='DetalleFactura',
        through_fields=('factura', 'producto'),
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

    practica = models.ForeignKey(
        Practica,
        on_delete = models.CASCADE,
        null = True,
        blank = True
    )
    #baja = models.BooleanField(default=False)
    # total = models.IntegerField(
    #     help_text="Importe total de la Factura.",
    #     unique=False,
    #     null=False,
    #     default=0,
    #     blank=False,
    #     error_messages={
    #         'blank': "El importe es obligatorio"
    #     }
    # )
    total = models.DecimalField(
            blank=False,
            null = False,
            default=Decimal(0),
            max_digits = Practica.MAX_DIGITOS,
            decimal_places = Practica.MAX_DECIMALES,
            error_messages = {},
            validators = [
                MinValueValidator(0, "El precio de la factura no puede ser negativo"),
            ]
    )




    def calcularTotal(self, detalles=[], descuento=0, recargo=0, practica=None):
        importe = Decimal(0)
        if practica is not None:
            importe += practica.precio
        for detalle in detalles:
            importe += detalle.subtotal
        if (descuento != recargo):
            importe += importe * (recargo-descuento) / 100
        return importe

    def totalAdeudado(self):
        importeAdelanto = 0
        if self.practica.adelanto:
            importeAdelanto = min(self.total, self.practica.adelanto.importe)
        return self.total - importeAdelanto

    def importeDescuento(self):
        a = self.recargo - self.descuento
        if a != -100:
            retorno = self.total * self.descuento / Decimal(100+a)
        else:
            practica = self.practica.precio if self.practica else Decimal(0)
            productos = sum( detalle.subtotal for detalle in self.detalles_producto.all() )
            retorno = (practica + productos) * self.descuento / Decimal(100)
        return -retorno

    def importeRecargo(self):
        a = self.recargo - self.descuento
        if a != -100:
            retorno = self.total * self.recargo / Decimal(100+a)
        else:
            practica = self.practica.precio if self.practica else Decimal(0)
            productos = sum( detalle.subtotal for detalle in self.detalles_producto.all() )
            retorno = (practica + productos) * self.recargo / Decimal(100)
        return retorno

    def importeNeto(self):
        return self.total * 100 / Decimal(121)

    def importeIVA(self):
        return self.total - self.importeNeto()

    def estaPaga(self):
        return Pago.objects.filter(factura=self).exists()

    def __str__(self):
        cadena = 'Tipo de Factura: {0}, Cliente: {1} Total: {2}.'
        return cadena.format(self.tipo, self.cliente, self.total)

    # def precioTotal(self, detalles):

    #     productos = Decimal("0")
    #     adelanto = Decimal("0")
    #     if not self.practica == None:
    #         practica = self.practica.precio

    #         if self.practica.adelanto:
    #             adelanto = self.practica.adelanto.importe
    #         if (self.descuento!=0):
    #             descuentoPractica = (practica*self.descuento)/100
    #             practica = practica-descuentoPractica

    #             if (self.recargo!=0):
    #                 recargoPractica = practica/self.recargo
    #                 practica = practica+recargoPractica
    #     else:
    #         practica = 0
    #     for detalle in detalles:
    #         productos += detalle.subtotal

    #     total = practica + productos - adelanto
    #     self.total = total
    #     # if self.tipo == "C":
    #     #     iva = round((total*21)/100)
    #     #     self.total = total-iva
    #     self.save()

    #     return self.total

    # def calcular_subtotales(self, detalles):

    #     totalGuardado = self.total
    #     self.total = Decimal("0")
    #     # self.save()
    #     for detalle in detalles:
    #         detalle.factura = self
    #         detalle.save()
    #         self.total += detalle.subtotal
    #     # self.save()

    # def calcular_iva(self):
    #     iva = round((self.total*21)/100)
    #     return iva

    # def restar_iva(self):
    #     iva = Factura.calcular_iva(self)
    #     nuevoTotal = self.total - iva
    #     return nuevoTotal


    # def sumar_total_adelanto(self):
    #     if self.practica.adelanto:
    #         adelanto = self.practica.adelanto.importe
    #     else:
    #         adelanto = 0
    #     if self.tipo == "C":
    #         total = Factura.restar_iva(self)
    #     else:
    #         total = self.total

    #     valorFinal = total + adelanto # '+ adelanto'?
    #     return valorFinal



    # '''def  __unicode__(self):
    #     return self.total'''

    # """def importeVentas(self):
    #     return sum([
    #         detalle.subtotal for detalle in self.detalles_producto.all()
    #     ])

    # def importeServicios(self):
    #     return self.practica.estados.realizacion().total()

    # def ajusteDescuento(self):
    #     importe = self.importeVentas() + self.importeServicios()
    #     return -( importe * self.descuento / Decimal(100) )

    # def ajusteRecargo(self):
    #     importe = self.importeVentas() + self.importeServicios()
    #     return importe * self.recargo / Decimal(100)

    # def importe(self):
    #     importe = self.importeVentas() + self.importeServicios()
    #     recargo = importe * self.recargo / Decimal(100)
    #     descuento = -(importe * self.descuento / Decimal(100))
    #     return importe + recargo + descuento


    # def obtener_adelanto(self):
    #     adelanto = self.practica.adelanto.importe
    #     return adelanto"""

    # """def calcular_descuento_practica(self):
    #     if not self.practica == None:
    #         practica = self.practica.precio

    #         if (self.descuento!=0):
    #             descuentoPractica = (practica*self.descuento)/100
    #             return descuentoPractica
    #         else:
    #             return 0
    #     else:
    #         return 0

    # def calcular_recargo_practica(self):
    #     if not self.practica == None:
    #         practica = self.practica.precio
    #         if (self.recargo!=0):
    #             recargoPractica = (practica*self.recargo)/100
    #             return recargoPractica
    #         else:
    #             return 0
    #     else:
    #         return 0"""

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


    def precioPorUnidad(self):
        return self.subtotal / Decimal(self.cantidad)

    def save(self, *args, **kwargs):
        if (not "commit" in kwargs) or kwargs["commit"]:
            self.subtotal = self.cantidad * self.producto.precioPorUnidad
        super().save(*args, **kwargs)

    # """def precio(self):
    #     if self.cantidad != 0:
    #         return self.subtotal // self.cantidad"""

    # """def save(self, *args, **kwargs):

    #     if (not "commit" in kwargs) or (kwargs["commit"]):
    #         if (self.subtotal is None):
    #             precio = self.producto.precioPorUnidad
    #             self.subtotal = precio * self.cantidad


    #     super().save(*args, **kwargs)"""
