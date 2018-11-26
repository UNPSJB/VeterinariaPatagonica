from datetime import timedelta, date

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, DecimalValidator
from django.db import transaction
from django.utils import timezone

from Apps.GestionDeServicios.models import Servicio
from Apps.GestionDeProductos.models import Producto
from .practica import *



__all__ = [
    "Estado", "Creada", "Presupuestada", "Programada",
    "Realizada", "RealizadaServicio", "RealizadaProducto",
    "Cancelada", "Facturada"
]



class EstadoManager(models.Manager):

    def inicializar(self):

        if hasattr(self, "instance") and (not self.instance is None):

            if self.get_queryset().count() == 0:
                Creada.objects.create(practica=self.instance)
            else:
                raise Exception("La practica tiene estados asociados, no puede ser inicializada")
        else:
            raise Exception("La practica a inicializar no es accesible desde el model manager")

    def inicial(self):

        if hasattr(self, "instance") and (not self.instance is None):

            queryset = self.get_queryset()
            if queryset.count() != 0:
                return queryset.get(tipo=Creada.TIPO)
            else:
                raise Exception("La practica no fue inicializada, no tiene estados asociados")
        else:
            raise Exception("La practica a inicializar no es accesible desde el model manager")



class Estado(models.Model):

    class Meta:
        get_latest_by = 'marca'

    @classmethod
    def register(cls, klass):
        cls.TIPOS.append((klass.TIPO, klass.__name__.lower()))

    TIPO = 0
    TIPOS = [
        (0, 'Estado')
    ]

    objects = EstadoManager()

    marca = models.DateTimeField(auto_now_add=True)

    practica = models.ForeignKey(
        Practica,
        related_name="estados",
        related_query_name="estado",
        on_delete=models.CASCADE
    )

    tipo = models.PositiveSmallIntegerField(choices=TIPOS)

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="practica_estados",
        related_query_name="practica_estado",
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    @classmethod
    def acciones(cls):
        return set()

    def accionesPosibles(self):
        if not self.esUltimo():
            return set()
        permitidas = self.practica.acciones()
        return self.acciones().intersection(permitidas)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.tipo = self.__class__.TIPO
        super(Estado, self).save(*args, **kwargs)

    def related(self):
        return self.__class__ != Estado and self or getattr(self, self.get_tipo_display())

    def esRealizada(self):
        return self.tipo == Realizada.TIPO or self.tipo == Facturada.TIPO

    def esUltimo(self):
        return (self.practica.estado().id == self.related().id)

    def siguienteEstado(self):
        if self.esUltimo():
            return None
        siguiente = Estado.objects.filter(practica=self.practica, id__gt=self.pk).first()
        return siguiente.related()

    def anteriorEstado(self):
        anterior = Estado.objects.filter(practica=self.practica, id__lt=self.pk).last()
        return anterior.related()

    def __str__(self):
        return self.__class__.__name__



class EstadoCancelable(Estado):

    class Meta:
        abstract = True

    def cancelar(self, motivo=""):

        return Cancelada.objects.create(
            practica=self.practica,
            motivo=motivo
        )



class EstadoRealizable(Estado):

    class Meta:
        abstract = True

    def realizar(self, inicio, finalizacion, condicionPreviaMascota="", resultados=""):

        servicios = [
            RealizadaServicio(
                servicio=detalle.servicio,
                cantidad=detalle.cantidad,
                precio=detalle.precio,
            ) for detalle in self.practica.practica_servicios.all()
        ]

        productos = [
            RealizadaProducto(
                producto=detalle.producto,
                cantidad=detalle.cantidad,
                precio=detalle.precio,
            ) for detalle in self.practica.practica_productos.all()
        ]

        with transaction.atomic():
            realizada = Realizada.objects.create(
                practica=self.practica,
                inicio=inicio,
                finalizacion=finalizacion,
                condicionPreviaMascota=condicionPreviaMascota,
                resultados=resultados,
            )
            realizada.realizada_servicios.set(servicios, bulk=False)
            realizada.realizada_productos.set(productos, bulk=False)

        return realizada

    def programar(self, inicio, finalizacion, adelanto):



class EstadoProgramable(Estado):

    class Meta:
        abstract = True

    def programar(self, inicio, finalizacion, adelanto):

        if self.practica.adelanto is not None:
            raise Exception("La practica ya tiene adelanto registrado")

        with transaction.atomic():
            programada = Programada.objects.create(
                practica=self.practica,
                inicio=inicio,
                finalizacion=finalizacion,
            )
            adelanto = Adelanto.objects.create(
                turno=programada,
                importe=adelanto
            )
            self.practica.adelanto = adelanto
            self.practica.save(force_update=True)

        return programada



class Creada(EstadoRealizable, EstadoCancelable, EstadoProgramable):
    TIPO = 1

    @classmethod
    def acciones(cls):
        return set([
            Practica.Acciones.presupuestar,
            Practica.Acciones.programar,
            Practica.Acciones.realizar,
            Practica.Acciones.cancelar,
        ])

    def accionesPosibles(self):
        return set([Practica.Acciones.cancelar])

    def presupuestar(self, diasMantenimiento):
        return Presupuestada.objects.create(
            practica = self.practica,
            diasMantenimiento=diasMantenimiento,
        )



class ProgramadaManager(EstadoManager):
    def enHorario(self, inicio, finalizacion):

        total = models.Q(
            inicio__lte=inicio,
            finalizacion__gte=finalizacion
        )

        parcial = models.Q(
            inicio__gt=inicio,
            inicio__lt=finalizacion
        ) | models.Q(
            finalizacion__gt=inicio,
            finalizacion__lt=finalizacion
        )

        return self.annotate(
            max_id=models.Max('practica__estado__id')
        ).filter(
            total | parcial,
            id=models.F('max_id'),
        )

class Programada(EstadoCancelable, EstadoRealizable):
    TIPO = 2
    objects = ProgramadaManager()

    @classmethod
    def acciones(cls):
        return set([
            Practica.Acciones.reprogramar,
            Practica.Acciones.realizar,
            Practica.Acciones.cancelar,
        ])

    inicio = models.DateTimeField()

    finalizacion = models.DateTimeField()

    motivoReprogramacion = models.CharField(
        verbose_name="Motivo de reprogramacion",
        max_length=Practica.MAX_MOTIVO,
        blank=True,
    )

    def reprogramar(self, inicio, finalizacion, motivoReprogramacion):

        return Programada.objects.create(
            practica=self.practica,
            inicio=inicio,
            finalizacion=finalizacion,
            motivoReprogramacion=motivoReprogramacion
        )

    @property
    def duracion(self):
        return int((self.finalizacion-self.inicio).total_seconds() / 60)

    def esReprogramacion(self):
        return isinstance(self.anteriorEstado(), Programada)

    def fueRealizado(self):
        siguienteEstado = self.siguienteEstado()
        if siguienteEstado is None:
            return False
        if isinstance(siguienteEstado.related(), Realizada):
            return True
        return False

    def fueCancelado(self):
        siguiente = self.siguienteEstado()
        if siguiente is None:
            return False
        return isinstance(siguiente, Cancelada)

    def fueReprogramado(self):
        siguiente = self.siguienteEstado()
        if siguiente is None:
            return False
        return isinstance(siguiente, Programada)

    def tiempoRestante(self):
        return ((self.inicio - timezone.now()).total_seconds() / 60)

    def turnosMismoHorario(self):
        return Programada.objects.enHorario(
            self.inicio,
            self.finalizacion,
        ).exclude(id=self.id)


    def esReprogramacion(self):
        return isinstance(self.anteriorEstado(), Programada)

class Presupuestada(EstadoCancelable, EstadoRealizable, EstadoProgramable):
    TIPO = 3



class Presupuestada(EstadoCancelable, EstadoRealizable, EstadoProgramable):
    TIPO = 3


class Realizada(Estado):
    TIPO = 5


    inicio = models.DateTimeField()


    inicio = models.DateTimeField()

    finalizacion = models.DateTimeField()

    condicionPreviaMascota = models.TextField(
        blank=True
    )

    resultados = models.TextField(
        blank=True
    )

    inicio = models.DateTimeField()

    finalizacion = models.DateTimeField()

    condicionPreviaMascota = models.TextField(
        blank=True
    )

    resultados = models.TextField(
        blank=True
    )

    servicios = models.ManyToManyField(
        Servicio,
        through='RealizadaServicio',
        through_fields=('realizada','servicio'),
        related_name='realizadas',
        related_query_name='practica_realizada',
    )

    productos = models.ManyToManyField(
        Producto,
        through='RealizadaProducto',
        through_fields=('realizada','producto'),
        related_name='realizadas',
        related_query_name='practica_realizada',
    )
    precioTotal = models.DecimalField(
        null = True,
        max_digits=Practica.MAX_DIGITOS,
        decimal_places=Practica.MAX_DECIMALES,
        validators = [
            MinValueValidator(Practica.MIN_PRECIO, message=("El precio no puede ser menor a {:.%df}" % (Practica.MAX_DECIMALES)).format(Practica.MIN_PRECIO)),
            DecimalValidator(max_digits=Practica.MAX_DIGITOS, decimal_places=Practica.MAX_DECIMALES)
        ]
    )

    def pagar(self, monto):
        pass

    def facturar(self):
        return Facturada.objects.create(
            practica=self.practica
        )

    @property
    def duracion(self):
        return int((self.finalizacion-self.inicio).total_seconds() / 60)

    def totalServicios(self):

        servicios = [ detalle for detalle in self.realizada_servicios.all() ]
        return sum([ detalle.precioTotal() for detalle in servicios ])

    def totalProductos(self):

        productos = [ detalle for detalle in self.realizada_productos.all() ]
        return sum([ detalle.precioTotal() for detalle in productos ])

    def total(self):
        return self.totalProductos() + self.totalServicios()



class RealizadaServicio(models.Model):

    class Meta:
        unique_together = ("realizada", "servicio")
        index_together = ["realizada", "servicio"]

    realizada = models.ForeignKey(
        Realizada,
        on_delete=models.CASCADE,
        related_name='realizada_servicios'
    )

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name='servicio_realizadas'
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

    observaciones = models.TextField(
        blank=True
    )

    def save(self, *args, **kwargs):

        if (not "commit" in kwargs) or (kwargs["commit"]):
            if (self.precio is None) and (not self.servicio is None):
                self.precio = self.servicio.precioManoDeObra

        super().save(*args, **kwargs)

    def precioTotal(self):
        return self.cantidad * self.precio



class RealizadaProducto(models.Model):

    class Meta:
        unique_together = ("realizada", "producto")
        index_together = ["realizada", "producto"]

    realizada = models.ForeignKey(
        Realizada,
        on_delete=models.CASCADE,
        related_name='realizada_productos'
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='producto_realizadas'
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
        return self.cantidad * self.precio

    def save(self, *args, **kwargs):

        if (not "commit" in kwargs) or (kwargs["commit"]):
            if (self.precio is None) and (not self.producto is None):
                self.precio = self.producto.precioPorUnidad

        super().save(*args, **kwargs)



class Cancelada(Estado):
    TIPO = 4

    motivo = models.TextField(
        blank=True
    )



class Facturada(Estado):
    TIPO = 6



for Klass in (Creada, Presupuestada, Programada, Realizada, Facturada, Cancelada):
    Estado.register(Klass)
