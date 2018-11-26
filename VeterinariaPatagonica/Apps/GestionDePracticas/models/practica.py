from decimal import Decimal
from enum import Enum

from django.db import models
from django.core.validators import MinValueValidator, DecimalValidator

from VeterinariaPatagonica.errores import VeterinariaPatagonicaError
from VeterinariaPatagonica.tools import paramsToFilter, VeterinariaPatagonicaQuerySet, R
from VeterinariaPatagonica.areas import Areas
from Apps.GestionDeServicios.models import Servicio
from Apps.GestionDeProductos.models import Producto
from Apps.GestionDeClientes.models import Cliente
from Apps.GestionDeTiposDeAtencion.models import TipoDeAtencion
from Apps.GestionDeMascotas.models import Mascota
from Apps.GestionDeClientes import models as gcmodels
from Apps.GestionDeServicios import models as gsmodels
from Apps.GestionDeTiposDeAtencion import models as gtdamodels
from Apps.GestionDeMascotas import models as gmmodels
import Apps.GestionDePracticas.models.estado


__all__ = [ "Practica", "PracticaServicio", "PracticaProducto", "Adelanto" ]



class PracticaBaseManager(models.Manager):

    def __init__(self, tipo=None):
        super().__init__()
        self.tipo = tipo

    def get_queryset(self):
        qs = super().get_queryset()
        if self.tipo is not None:
            qs = qs.filter(tipo=self.tipo)
        return qs

class PracticaQuerySet(VeterinariaPatagonicaQuerySet):

    def enEstado(self, estados):

        if type(estados) != list:
            estados = [estados]

        return self.annotate(max_id=models.models.Max('estado__id')).filter(
            estado__id=models.F('max_id'),
            estado__tipo__in=[ e.TIPO for e in estados])

    def ordenarPorEstado(self, ascendente=True):

        Estado = Apps.GestionDePracticas.models.estado.Estado
        orden = "nombre_estado"
        if not ascendente:
            orden = "-" + orden

        traducciones = []
        for tipo, nombre in Estado.TIPOS:
            traducciones.append(
                models.When(tipo_estado=tipo, then=models.Value(nombre))
            )

        practicas = self.annotate(
            max_id=models.Max("estado__id"),
            tipo_estado=models.Subquery(
                Estado.objects.filter(practica=models.OuterRef('pk')).order_by("-id").values("tipo")[:1]
            )
        ).filter(
            estado__id=models.F("max_id")
        )

        practicas = practicas.annotate(
            nombre_estado=models.Case(*traducciones, output_field=models.CharField())
        )

        return practicas.order_by(orden)

    def ordenarPorCliente(self, ascendente=True):

        orden = ["cliente__apellidos", "cliente__nombres"]
        if not ascendente:
            orden = ["-" + field for field in orden ]

        return self.order_by(*orden)

    def ordenarPorCreacion(self, ascendente=True):

        orden = "primera_mod"
        if not ascendente:
            orden = "-" + orden

        return self.annotate(
            primera_mod=models.Min('estado__marca')
        ).filter(
            estado__marca=models.F('primera_mod')
        ).order_by(orden)

    def ordenarPorModificacion(self, ascendente=True):

        orden = "ultima_mod"
        if not ascendente:
            orden = "-" + orden

        return self.annotate(
            ultima_mod=models.Max('estado__marca')
        ).filter(
            estado__marca=models.F('ultima_mod')
        ).order_by(orden)

    def ordenar(self, criterio, ascendente):

        funciones = {
            "cliente" : "ordenarPorCliente",
            "estado" : "ordenarPorEstado",
            "creacion" : "ordenarPorCreacion",
            "modificacion" : "ordenarPorModificacion",
        }

        if criterio:
            funcion = getattr(self, funciones[criterio])
            return funcion(ascendente)

        return self

    def filtrar(self, filtros):

        practicas = self

        if ("estado" in filtros and filtros["estado"]) or \
        ("desde" in filtros and filtros["desde"]) or \
        ("hasta" in filtros and filtros["hasta"]):
            practicas = practicas.annotate(max_id=models.Max('estado__id'))

        return practicas.filter(paramsToFilter(filtros, Practica))



PracticaManager = PracticaBaseManager.from_queryset(PracticaQuerySet)



class Practica(models.Model):

    objects = PracticaManager()
    consultas = PracticaManager(Areas.C.codigo)
    quirurgicas = PracticaManager(Areas.Q.codigo)
    internaciones = PracticaManager(Areas.I.codigo)

    class Acciones(Enum):

        presupuestar = 0
        programar = 1
        reprogramar = 2
        realizar = 3
        cancelar = 4
        facturar = 5

        def idPermiso(self):
            return "GestionDePracticas.can_"+self.name

        @classmethod
        def iniciales(cls, codigo):
            generales = set([
                Practica.Acciones.presupuestar,
                Practica.Acciones.programar,
                Practica.Acciones.realizar,
            ])
            return generales.intersection(Practica.Acciones.para(codigo))

        @classmethod
        def para(cls, codigo):
            acciones = {
                Areas.Q.codigo : set([
                    Practica.Acciones.presupuestar,
                    Practica.Acciones.programar,
                    Practica.Acciones.reprogramar,
                    Practica.Acciones.realizar,
                    Practica.Acciones.cancelar,
                    Practica.Acciones.facturar,
                ]),
                Areas.C.codigo : set([
                    Practica.Acciones.presupuestar,
                    Practica.Acciones.realizar,
                    Practica.Acciones.cancelar,
                    Practica.Acciones.facturar,
                ]),
            }
            return acciones.get(codigo, set())

    MAX_NOMBRE = 100
    MAX_MOTIVO = 300
    MAX_DIGITOS = 8
    MAX_DECIMALES = 2
    MAX_DIGITOS_AJUSTES = 5
    MAX_DECIMALES_AJUSTES = 2
    MIN_PRECIO = Decimal(0)
    MAX_PRECIO = Decimal( (pow(10,MAX_DIGITOS)-1)/pow(10,MAX_DECIMALES) )

    MAPPER = {
        "cliente" : lambda value: models.Q(cliente__nombres__icontains=value) | models.Q(cliente__apellidos__icontains=value),
        "tipoDeAtencion" : "tipoDeAtencion__nombre__icontains",
        "estado" :  lambda value: models.Q(estado__id=models.F('max_id')) & models.Q(estado__tipo=value),
        "desde" : lambda value: models.Q(estado__id=models.F('max_id')) & models.Q(estado__marca__date__gte=value),
        "hasta" : lambda value: models.Q(estado__id=models.F('max_id')) & models.Q(estado__marca__date__lte=value),
        "servicios" : lambda values: R(*[R(**{"servicios__nombre__icontains" : value, "servicios__descripcion__icontains" : value}) for value in values]),
    }

    tipo = models.CharField(
        max_length=Areas.caracteresCodigo(),
        editable=False,
        choices=Areas.choices(),
    )

    id = models.AutoField(
        primary_key=True,
        unique=True,
        editable=False
    )

    # Es mejor guardar el precio que sacar la cuenta en funcion de los subtotales?
    precio = models.DecimalField(
            blank=True,
            default=Decimal(0),
            max_digits = MAX_DIGITOS,
            decimal_places = MAX_DECIMALES,
            validators = [
                MinValueValidator(0, "El precio de la practica no puede ser negativo"),
            ],
    )

    cliente = models.ForeignKey(
        Cliente,
        related_name='practicas',
        on_delete=models.CASCADE,
        error_messages={
            'null' : 'El cliente no puede ser null',
            'blank' : 'El cliente es obligatorio'
        }
    )

    mascota = models.ForeignKey(
        Mascota,
        related_name='practicas',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    tipoDeAtencion = models.ForeignKey(
        TipoDeAtencion,
        related_name='practicas',
        on_delete=models.CASCADE,
        error_messages={
            'null' : 'El tipo de atencion no puede ser null',
            'blank' : 'El tipo de atencion es obligatorio'
        }
    )

    servicios = models.ManyToManyField(
        Servicio,
        through='PracticaServicio',
        through_fields=('practica','servicio'),
        related_name='practicas',
        related_query_name='practica',
    )

    productos = models.ManyToManyField(
        Producto,
        through='PracticaProducto',
        through_fields=('practica','producto'),
        related_name='practicas',
        related_query_name='practica',
    )



    adelanto = models.OneToOneField(
        "Adelanto",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="practica",
    )



    turno = models.DateTimeField(
        blank=True,
        null=True,
    )



    def __str__(self):
        return "Practica numero {} tipo {}".format( self.id, Areas[self.tipo].nombre )



    def save(self, *args, **kwargs):

        pk = self.pk
        super().save(*args, **kwargs)

        if (not "commit" in kwargs) or (kwargs["commit"]):
            if (pk is None) and (self.estado() is None):
                self.estados.inicializar()



    def estado(self):
        if self.estados.exists():
            return self.estados.latest().related()



    def estados_related(self):
        return [estado.related() for estado in self.estados.all()]



    def hacer(self, accion, *args, **kwargs):

        estado_actual = self.estado()

        if estado_actual is None:
            raise Exception("La practica no fue inicializada todavia")

        if hasattr(estado_actual, accion):
            metodo = getattr(estado_actual, accion)
            estado_nuevo = metodo(*args, **kwargs)
            return estado_nuevo

        else:
            raise Exception("La accion: %s solicitada no se pudo realizar sobre el estado %s" % (accion, estado_actual))



    def acciones(self):
        return Practica.Acciones.para(self.tipo)



    def duracion(self):
        return sum([servicio.servicio.tiempoEstimado * servicio.cantidad for servicio in self.practica_servicios.all()])



    def esPosible(self, accion):
        estadoActual = self.estado()
        return accion in estadoActual.accionesPosibles()



    def enEstado(self, estado):
        return isinstance(self.estado(), estado)



    def nombreEstado(self):
        return self.estado().__class__.__name__.lower()



    def nombreTipo(self):
        return Areas[self.tipo].nombre



    def totalServicios(self):

        servicios = [ detalle for detalle in self.practica_servicios.all() ]
        return sum([ detalle.precioTotal() for detalle in servicios ])



    def totalProductos(self):

        productos = [ detalle for detalle in self.practica_productos.all() ]
        return sum([ detalle.precioTotal() for detalle in productos ])



    def total(self):
        return self.totalProductos() + self.totalServicios()


    """
    def precios(self):

        # Servicios
        totalInsumos = Decimal("0")
        totalServicios = Decimal("0")
        if self.estado().esRealizada():
            # Si la practica esta realizada, debo tomar los servicios practicados
            # y los productos utilizados
            insumos = self.practica_productos.all()
            for insumo in insumos:
                totalInsumos += insumo.precioTotal()
            servicios = self.practica_servicios.all()
            for servicio in servicios:
                totalServicios += servicio.precioTotal()
        else:
            # Si no esta realizada, debo tomar el total por los servicios contratados
            servicios = self.servicios.all()
            for servicio in servicios:
                totalServicios += servicio.precioTotal()

        # Recargos tipo de atencion
        recargo = self.tipoDeAtencion.recargo

        # Descuetos, solo los de servicio, los de producto son para la facturacion de productos
        descuento = self.cliente.descuentoServicio

        # Faltan los adelantos en concepto de senia o pago antes de realizar la practica
        adelanto = Decimal("0")

        # Estos campos son tranquilamente de la factura
        self.precio
        self.descuento
        self.recargo
        return totalInsumos, totalServicios, adelanto, recargo, descuento



    def precioTotal(self):
        insumos, servicios, adelanto, recargo, descuento = self.precios()
        total = insumos + servicios - adelanto
        totalRecargo = (total * recargo / 100) if recargo else Decimal("0")
        totalDescuento = (total * descuento / 100) if descuento else Decimal("0")
        return total + totalRecargo - totalDescuento
    """



class Adelanto(models.Model):

    importe = models.DecimalField(
            blank=True,
            default=Decimal(0),
            max_digits = Practica.MAX_DIGITOS,
            decimal_places = Practica.MAX_DECIMALES,
            validators = [
                MinValueValidator(0, "El importe del adelanto no puede ser negativo"),
            ],
    )

    turno = models.OneToOneField(
        "GestionDePracticas.Programada",
        null=True,
        on_delete=models.SET_NULL,
        related_name="adelanto",
    )



class PracticaServicio(models.Model):

    class Meta:
        unique_together = ("practica", "servicio")
        index_together = ["practica", "servicio"]

    practica = models.ForeignKey(
        Practica,
        on_delete=models.CASCADE,
        related_name='practica_servicios'
    )

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name='servicio_practicas'
    )

    cantidad = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1,"La cantidad debe ser mayor que cero")
        ],
    )

    precio = models.DecimalField(
        max_digits=Practica.MAX_DIGITOS,
        decimal_places=Practica.MAX_DECIMALES,
        validators = [
            MinValueValidator(
                Practica.MIN_PRECIO,
                message=("El precio no puede ser menor a {:.%df}" % (Practica.MAX_DECIMALES)).format(Practica.MIN_PRECIO)
            ),
        ]
    )

    def precioTotal(self):
        return self.precio * self.cantidad

    def save(self, *args, **kwargs):

        if (not "commit" in kwargs) or (kwargs["commit"]):
            if (self.precio is None) and (not self.servicio is None):
                self.precio = self.servicio.precioManoDeObra

        super().save(*args, **kwargs)

    def __str__(self):
        return "{} x {}".format(self.servicio.nombre, self.cantidad)



class PracticaProducto(models.Model):

    class Meta:
        unique_together = ("practica", "producto")
        index_together = ["practica", "producto"]

    practica = models.ForeignKey(
        Practica,
        on_delete=models.CASCADE,
        related_name='practica_productos'
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='producto_practicas'
    )

    cantidad = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1,"La cantidad debe ser mayor que cero")
        ],
    )

    precio = models.DecimalField(
        max_digits=Practica.MAX_DIGITOS,
        decimal_places=Practica.MAX_DECIMALES,
        validators = [
            MinValueValidator(
                Practica.MIN_PRECIO,
                message=("El precio no puede ser menor a {:.%df}" % (Practica.MAX_DECIMALES)).format(Practica.MIN_PRECIO)
            ),
        ]
    )

    def precioTotal(self):
        return self.precio * self.cantidad

    def save(self, *args, **kwargs):

        if (not "commit" in kwargs) or (kwargs["commit"]):
            if (self.precio is None) and (not self.producto is None):
                self.precio = self.producto.precioPorUnidad

        super().save(*args, **kwargs)

    def __str__(self):
        return "{} x {}".format(self.producto.nombre, self.cantidad)
