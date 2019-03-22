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

    MAPEO_ORDEN = {
        "orden_id" : ["id"],
        "orden_cliente" : ["cliente__apellidos", "cliente__nombres"],
        "orden_mascota" : ["mascota__nombre"],
        "orden_actualizacion" : ["ultima_mod"],
    }

    def conEstadoActual(self):
        return self.annotate(
            id_estado_actual=models.Max('estado__id')
        )

    def enEstado(self, estados):

        if type(estados) != list:
            estados = [estados]

        return self.conEstadoActual().filter(
            estado__id=models.F('id_estado_actual'),
            estado__tipo__in=[ estado.TIPO for estado in estados]
        )



PracticaManager = PracticaBaseManager.from_queryset(PracticaQuerySet)



class Practica(models.Model):

    objects = PracticaManager()
    consultas = PracticaManager(Areas.C.codigo)
    quirurgicas = PracticaManager(Areas.Q.codigo)
    internaciones = PracticaManager(Areas.I.codigo)

    class Acciones(Enum):

        presupuestar = "presupuestar"
        programar = "programar turno"
        reprogramar = "reprogramar turno"
        realizar = "registrar realizacion"
        cancelar = "cancelar"
        facturar = "facturar"

        #[TODO]: Crear permisos para las transiciones de estado
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
        "cliente" : lambda value: R(cliente__nombres__icontains=value,
                                    cliente__apellidos__icontains=value,
                                    cliente__dniCuit__contains=value) ,

        "mascota" : lambda value: R(mascota__nombre__icontains=value,
                                    mascota__patente__contains=value),

        "tipo_de_atencion" : "tipoDeAtencion__nombre__icontains",

        "estados" : lambda value:   models.Q(estado__id=models.F('id_estado_actual')) & \
                                    models.Q(estado__tipo__in=value),

        "ultima_mod_desde" : lambda value:  models.Q(estado__id=models.F('id_estado_actual')) & \
                                            models.Q(estado__marca__date__gte=value),

        "ultima_mod_hasta" : lambda value:  models.Q(estado__id=models.F('id_estado_actual')) & \
                                            models.Q(estado__marca__date__lte=value),

        "servicios" : lambda values:    R(*[R(**{
            "servicios__nombre__icontains" : value,
            "servicios__descripcion__icontains" : value
        }) for value in values]),

        "productos" : lambda values:    R(*[R(**{
            "productos__nombre__icontains" : value,
            "productos__marca__icontains" : value,
            "productos__descripcion__icontains" : value,
            "productos__rubro__nombre__icontains" : value
        }) for value in values]),

        "servicios_realizados" : lambda values: R(*[R(**{
            "estado__realizada__servicios__nombre__icontains" : value,
            "estado__realizada__servicios__descripcion__icontains" : value,
        }) for value in values]),

        "productos_utilizados" : lambda values: R(*[R(**{
            "estado__realizada__productos__nombre__icontains" : value,
            "estado__realizada__productos__marca__icontains" : value,
            "estado__realizada__productos__descripcion__icontains" : value,
            "estado__realizada__productos__rubro__nombre__icontains" : value,
        }) for value in values]),
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



    def importeServicios(self):
        return sum([
            detalle.precioTotal() for detalle in self.practica_servicios.all()
        ])



    def importeProductos(self):
        return sum([
            detalle.precioTotal() for detalle in self.practica_productos.all()
        ])



    def ajusteServicios(self):
        return self.importeServicios() * self.tipoDeAtencion.recargo / Decimal(100)



    def ajusteProductos(self):
        return self.importeProductos() * self.tipoDeAtencion.recargo / Decimal(100)



    def totalServicios(self):

        servicios = [ detalle for detalle in self.practica_servicios.all() ]
        total = sum([ detalle.precioTotal() for detalle in servicios ])
        ajuste = total * self.tipoDeAtencion.recargo / Decimal(100)
        return total + ajuste



    def totalProductos(self):

        productos = [ detalle for detalle in self.practica_productos.all() ]
        total = sum([ detalle.precioTotal() for detalle in productos ])
        ajuste = total * self.tipoDeAtencion.recargo / Decimal(100)
        return total + ajuste



    def total(self):
        return self.totalProductos() + self.totalServicios()



    def duracionTotalServicios(self):
        return sum([
            (detalle.servicio.tiempoEstimado * detalle.cantidad) for detalle in self.practica_servicios.all()
        ])



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
