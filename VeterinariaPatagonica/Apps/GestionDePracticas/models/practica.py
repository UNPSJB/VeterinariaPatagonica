from decimal import Decimal
from enum import Enum

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ObjectDoesNotExist

from VeterinariaPatagonica.tools import R
from VeterinariaPatagonica.areas import Areas
from Apps.GestionDeServicios.models import Servicio
from Apps.GestionDeProductos.models import Producto
from Apps.GestionDeClientes.models import Cliente
from Apps.GestionDeMascotas.models import Mascota
from Apps.GestionDeTiposDeAtencion.models import TipoDeAtencion

__all__ = ("Practica", "PracticaServicio", "PracticaProducto", "Adelanto")


class PracticaBaseManager(models.Manager):

    def __init__(self, tipo=None):
        super().__init__()
        self.tipo = tipo

    def get_queryset(self):
        qs = super().get_queryset()
        if self.tipo is not None:
            qs = qs.filter(tipo=self.tipo)
        return qs

class PracticaQuerySet(models.QuerySet):

    MAPEO_FILTRADO = {
        "tipo" : "tipo",
        "cliente" : lambda value: R(cliente__nombres__icontains=value,
                                    cliente__apellidos__icontains=value,
                                    cliente__dniCuit__contains=value) ,
        "mascota" : lambda value: R(mascota__nombre__icontains=value,
                                    mascota__patente__contains=value),
        "tipo_de_atencion" : "tipoDeAtencion__nombre__icontains",
        "estados" : lambda value:   models.Q(estado__id=models.F('id_estado_actual')) & \
                                    models.Q(estado__tipo__in=value),
        "estado" : lambda value:   models.Q(estado__id=models.F('id_estado_actual')) & \
                                   models.Q(estado__tipo=value),
        "actualizacion_desde" : lambda value:  models.Q(estado__id=models.F('id_estado_actual')) & \
                                            models.Q(estado__marca__date__gte=value),
        "actualizacion_hasta" : lambda value:  models.Q(estado__id=models.F('id_estado_actual')) & \
                                            models.Q(estado__marca__date__lte=value),
        "realizada_por" : "estado__realizada__usuario__username__icontains",
        "realizada_desde" : "estado__realizada__finalizacion__gte",
        "realizada_hasta" : "estado__realizada__inicio__lte",
        "programada_por" : lambda value:  models.Q(estado__id=models.F('id_estado_actual')) & \
                                          models.Q(nombre_programada_por__icontains=value),
        "programada_desde" : lambda value:  models.Q(estado__id=models.F('id_estado_actual')) & \
                                            models.Q(finalizacion_turno__gte=value),
        "programada_hasta" : lambda value:  models.Q(estado__id=models.F('id_estado_actual')) & \
                                            models.Q(inicio_turno__lte=value),
    }

    MAPEO_ORDEN = {
        "id" : ["id"],
        "cliente" : ["cliente__apellidos", "cliente__nombres"],
        "mascota" : ["mascota__nombre"],
        "marcaultimaactualizacion" : ["marca_ultima_actualizacion"],
        "marcacreacion" : ["marca_creacion"],
        "tipodeatencion" : ["tipoDeAtencion"],
        "precio" : ["precio"],
        "creadapor" : ["nombre_creada_por"],
        "atendidapor" : ["nombre_atendida_por"],
        "estadoactual" : ["nombre_estado_actual"],
        "realizadapor" : ["nombre_realizada_por"],
        "programadapor" : ["nombre_programada_por"],
        "iniciorealizacion" : ["inicio_realizacion"],
        "duracionrealizacion" : ["duracion_realizacion"],
        "inicioturno" : ["inicio_turno", "finalizacion_turno"],
        "duracionturno" : ["duracion_turno"],
        "reprogramaciones" : ["reprogramaciones"],
        "tiemporestante" : ["inicio_turno"],
    }

    def conEstadoInicial(self):
        return self.annotate(
            id_estado_inicial=models.Min('estado__id')
        )

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

    def atendidasPor(self, usuario):

        return self.conEstadoActual().filter(
            estado__id=models.F('id_estado_actual'),
            estado__usuario=usuario
        )

    def creadasPor(self, usuario):

        return self.conEstadoInicial().filter(
            estado__id=models.F('id_estado_inicial'),
            estado__usuario=usuario
        )

    def realizadasPor(self, usuario):

        return self.filter(
            estado__realizada__usuario=usuario
        )


PracticaManager = PracticaBaseManager.from_queryset(PracticaQuerySet)


class Practica(models.Model):

    objects = PracticaManager()
    consultas = PracticaManager(Areas.C.codigo())
    quirurgicas = PracticaManager(Areas.Q.codigo())

    class Acciones(Enum):

        presupuestar = "presupuestar"
        programar = "programar turno"
        reprogramar = "reprogramar turno"
        realizar = "registrar realizacion"
        cancelar = "cancelar"
        facturar = "facturar"
        crear = "crear practicas"
        modificar = "modificar realizacion"
        modificar_informacion_clinica = "modificar informacion clinica de la realizacion"
        ver_informacion_general = "ver informacion general de la practica"
        ver_detalle_estado = "ver detalles del estado de la practica"
        ver_informacion_clinica = "ver informacion clinica de la realizacion"
        listar = "mostrar practica al listar"
        exportar_txt = "exportar practica en listado con formato txt"
        exportar_xlsx = "exportar practica en listado con formato xlsx"

        def iniciales(codigo):
            generales = set([
                Practica.Acciones.presupuestar,
                Practica.Acciones.programar,
                Practica.Acciones.realizar,
            ])
            return generales.intersection(Practica.Acciones.actualizaciones(codigo))

        def actualizaciones(codigo):
            areas = {
                Areas.Q.codigo() : set([
                    Practica.Acciones.presupuestar,
                    Practica.Acciones.programar,
                    Practica.Acciones.reprogramar,
                    Practica.Acciones.realizar,
                    Practica.Acciones.cancelar,
                    Practica.Acciones.facturar,
                ]),
                Areas.C.codigo() : set([
                    Practica.Acciones.presupuestar,
                    Practica.Acciones.realizar,
                    Practica.Acciones.cancelar,
                    Practica.Acciones.facturar,
                ]),
            }
            return areas.get(codigo, set())

        def acciones(codigo):
            areas = {
                Areas.Q.codigo() : set([
                    Practica.Acciones.presupuestar,
                    Practica.Acciones.programar,
                    Practica.Acciones.reprogramar,
                    Practica.Acciones.realizar,
                    Practica.Acciones.cancelar,
                    Practica.Acciones.facturar,
                    Practica.Acciones.listar,
                    Practica.Acciones.ver_informacion_general,
                    Practica.Acciones.ver_informacion_clinica,
                    Practica.Acciones.ver_detalle_estado,
                    Practica.Acciones.modificar,
                    Practica.Acciones.modificar_informacion_clinica,
                ]),
                Areas.C.codigo() : set([
                    Practica.Acciones.presupuestar,
                    Practica.Acciones.realizar,
                    Practica.Acciones.cancelar,
                    Practica.Acciones.facturar,
                    Practica.Acciones.listar,
                    Practica.Acciones.ver_informacion_general,
                    Practica.Acciones.ver_informacion_clinica,
                    Practica.Acciones.ver_detalle_estado,
                    Practica.Acciones.modificar,
                    Practica.Acciones.modificar_informacion_clinica,
                ]),
            }
            return areas.get(codigo, set())

        def __str__(self):
            return self.value

    class Meta:
        permissions = (
            ("crear_consulta_atendida", "Permiso para crear consultas"),
            ("crear_cirugia_atendida", "Permiso para crear cirugias"),
            ("listar_consulta_atendida", "Permiso para listar consultas"),
            ("listar_cirugia_atendida", "Permiso para listar cirugias"),
            ("listar_consulta_no_atendida", "Permiso para listar consultas atendidas por otro usuario"),
            ("listar_cirugia_no_atendida", "Permiso para listar cirugias atendidas por otro usuario"),
            ("ver_informacion_general_consulta_atendida", "Permiso para ver informacion general de consultas"),
            ("ver_informacion_general_consulta_no_atendida", "Permiso para ver informacion general de consultas atendidas por otro usuario"),
            ("ver_informacion_general_cirugia_atendida", "Permiso para ver informacion general de cirugias"),
            ("ver_informacion_general_cirugia_no_atendida", "Permiso para ver informacion general de cirugias atendidas por otro usuario"),
            ("ver_informacion_clinica_consulta_atendida", "Permiso para ver informacion clinica de consultas"),
            ("ver_informacion_clinica_consulta_no_atendida", "Permiso para ver informacion clinica de consultas atendidas por otro usuario"),
            ("ver_informacion_clinica_cirugia_atendida", "Permiso para ver informacion clinica de cirugias"),
            ("ver_informacion_clinica_cirugia_no_atendida", "Permiso para ver informacion clinica de cirugias atendidas por otro usuario"),
            ("ver_detalle_estado_consulta_atendida", "Permiso para ver informacion detallada de consultas"),
            ("ver_detalle_estado_consulta_no_atendida", "Permiso para ver informacion detallada de consultas atendidas por otro usuario"),
            ("ver_detalle_estado_cirugia_atendida", "Permiso para ver informacion detallada de cirugias"),
            ("ver_detalle_estado_cirugia_no_atendida", "Permiso para ver informacion detallada de cirugias atendidas por otro usuario"),
            ("ver_reporte_consulta", "Permiso para ver reporte de consultas"),
            ("ver_reporte_cirugia", "Permiso para ver reporte de cirugias"),
            ("exportar_xlsx_consulta_atendida", "Permiso para exportar en xlsx consultas"),
            ("exportar_xlsx_consulta_no_atendida", "Permiso para exportar en xlsx consultas atendidas por otro usuario"),
            ("exportar_xlsx_cirugia_atendida", "Permiso para exportar en xlsx cirugias"),
            ("exportar_xlsx_cirugia_no_atendida", "Permiso para exportar en xlsx cirugias atendidas por otro usuario"),
        )
        default_permissions = ()

    MAX_NOMBRE = 100
    MAX_MOTIVO = 300
    MAX_DIGITOS = 8
    MAX_DECIMALES = 2
    MAX_DIGITOS_AJUSTES = 5
    MAX_DECIMALES_AJUSTES = 2
    MIN_PRECIO = Decimal(0)
    MAX_PRECIO = Decimal( (pow(10,MAX_DIGITOS)-1)/pow(10,MAX_DECIMALES) )


    tipo = models.CharField(
        max_length=1,
        editable=False,
        choices=Areas.paresOrdenados(),
    )

    id = models.AutoField(
        primary_key=True,
        unique=True,
        editable=False
    )

    precio = models.DecimalField(
            blank=True,
            null=True,
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
        return "%s número %d" % ( self.nombreTipo(), self.id )


    def save(self, *args, usuario=None, **kwargs):

        pk = self.pk
        super().save(*args, **kwargs)

        if (not "commit" in kwargs) or (kwargs["commit"]):
            if (pk is None) and (self.estado() is None):
                self.estados.inicializar(usuario)


    def estado(self):
        if self.estados.exists():
            return self.estados.latest().related()


    def estados_related(self):
        return [estado.related() for estado in self.estados.all()]


    def hacer(self, usuario, accion, *args, **kwargs):

        estado_actual = self.estado()

        if estado_actual is None:
            raise Exception("La practica no fue inicializada todavia")

        if hasattr(estado_actual, accion):
            metodo = getattr(estado_actual, accion)
            estado_nuevo = metodo(usuario, *args, **kwargs)
            return estado_nuevo

        else:
            raise Exception("La accion: %s solicitada no se pudo realizar sobre el estado %s" % (accion, estado_actual))


    def actualizaciones(self):
        return Practica.Acciones.actualizaciones(self.tipo)


    def acciones(self):
        return Practica.Acciones.acciones(self.tipo)


    def duracion(self):
        return sum([servicio.servicio.tiempoEstimado * servicio.cantidad for servicio in self.practica_servicios.all()])


    def esPosible(self, accion):
        return accion in self.estado().accionesPosibles()


    def enEstado(self, estado):
        return isinstance(self.estado(), estado)


    def nombreEstado(self):
        return str(self.estado())


    def nombreTipo(self):
        return Areas[self.tipo].nombre()


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


    def factura(self):
        try:
            factura = self.factura_set.get(practica=self)
        except ObjectDoesNotExist:
            factura = None
        return factura


class Adelanto(models.Model):

    class Meta:
        default_permissions = ()

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
        on_delete=models.CASCADE,
        related_name="adelanto",
    )


class PracticaServicio(models.Model):

    class Meta:
        unique_together = (("practica", "servicio"),)
        index_together = (("practica", "servicio"),)
        default_permissions = ()

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

    def cantidadesProductos(self):
        return [
            (
                item.producto,
                self.cantidad * item.cantidad
            ) for item in self.servicio.servicio_productos.all()
        ]

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
        unique_together = (("practica", "producto"),)
        index_together = (("practica", "producto"),)
        default_permissions = ()

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
