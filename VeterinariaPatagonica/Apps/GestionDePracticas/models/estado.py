from enum import Enum, unique

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, DecimalValidator
from django.db import transaction

from Apps.GestionDeServicios.models import Servicio
from Apps.GestionDeProductos.models import Producto
from .practica import Practica



__all__ = [ "Estado", "Creada", "Presupuestada", "Programada", "Realizada", "RealizadaServicio", "RealizadaProducto", "Cancelada", "Facturada" ]


#[TODO]: Averiguar si hay alguna manera de personalizar el manager de objetos relacionados
# ("objeto.relacionado_set"), estos metodos estaban pensados para ese manager, creia que
# se podira con la opcion "Meta.base_manager_name" pero no funciono
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

    marca = models.DateTimeField(auto_now=True)

    practica = models.ForeignKey(
        Practica,
        related_name="estados",
        on_delete=models.CASCADE
    )

    tipo = models.PositiveSmallIntegerField(choices=TIPOS)

    #[TODO]: Cuando este decidida la clase de usuario reemplazar AUTH_USER_MODEL
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.tipo = self.__class__.TIPO
        super(Estado, self).save(*args, **kwargs)

    def related(self):
        return self.__class__ != Estado and self or getattr(self, self.get_tipo_display())

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

    def realizar(self, inicio, duracion, condicionPreviaMascota="", resultados=""):

        realizada = Realizada.objects.create(
            practica=self.practica,
            inicio=inicio,
            duracion=duracion,
            condicionPreviaMascota=condicionPreviaMascota,
            resultados=resultados,
        )

        with transaction.atomic():

            detallesServicios = self.practica.practica_servicios.all()

            for detalle in detallesServicios:
                realizada.realizada_servicios.create(
                    servicio=detalle.servicio,
                    cantidad=detalle.cantidad,
                    precio=detalle.precio,
                )

            detallesProductos = self.practica.practica_productos.all()

            for detalle in detallesProductos:
                realizada.realizada_productos.create(
                    producto=detalle.producto,
                    cantidad=detalle.cantidad,
                    precio=detalle.precio,
                )

        return realizada



class Creada(EstadoRealizable):
    TIPO = 1

    def programar(self, inicio, duracion):

        return Programada.objects.create(practica=self.practica, inicio=inicio, duracion=duracion)

    def presupuestar(self, diasMantenimiento):

        return Presupuestada.objects.create(
            practica = self.practica,
            diasMantenimiento=diasMantenimiento,
        )



class Programada(EstadoCancelable, EstadoRealizable):
    TIPO = 2

    inicio = models.DateTimeField(
        blank=False
    )

    duracion = models.PositiveSmallIntegerField(
        blank=False
    )

    motivoReprogramacion = models.CharField(
        verbose_name="Motivo de reprogramacion",
        max_length=Practica.MAX_MOTIVO,
        blank=True,
        null=False,
        default=""
    )

    def reprogramar(self, inicio, duracion, motivo):

        return Programada.objects.create(
            practica=self.practica,
            inicio=inicio,
            duracion=duracion,
            motivoReprogramacion=motivo
        )

    def pagar(self, monto):
        pass



class Presupuestada(EstadoRealizable, EstadoCancelable):
    TIPO = 3

    #porcentajeDescuento = models.PositiveSmallIntegerField()
    #[TODO]fechaMantenimientoOferta = fechaActual+diasMantenimiento:

    # Seria necesario agregar un numero identificatorio a turnos/presupuestos/practicas?
    # No decidimos entre dejar el id de django visible para los usuarios o agregar otro field

    diasMantenimiento = models.PositiveSmallIntegerField()

    def seniar(self, practica, turno, monto):
        return Programada.objects.create(practica=practica, turno=turno)

    def confirmar(self, practica, turno):
        #[TODO]if fechaActual < fechaMantenimientoOferta: return Programada(self, practica, turno)
        return Programada.objects.create(practica=practica, turno=turno)

    def programar(self, inicio, duracion):

        return Programada.objects.create(practica=self.practica, inicio=inicio, duracion=duracion)



class Realizada(EstadoCancelable):
    TIPO = 5

    inicio = models.DateTimeField()
    duracion = models.PositiveSmallIntegerField()
    condicionPreviaMascota = models.TextField(blank=True, null=False, default="")
    resultados = models.TextField(blank=True, null=False, default="")
    servicios = models.ManyToManyField(
        Servicio,
        through='RealizadaServicio',
        through_fields=('realizada','servicio'),
        related_name='realizadas'
    )
    productos = models.ManyToManyField(
        Producto,
        through='RealizadaProducto',
        through_fields=('realizada','producto'),
        related_name='realizadas'
    )

    def agregarServicio(self, servicio=None, cantidad=None, precio=None):

        return RealizadaServicio.objects.create(
            realizada=self,
            servicio=servicio,
            cantidad=cantidad,
            precio=precio,
        )

    def agregarProducto(self, producto=None, cantidad=None, precio=None):

        return RealizadaProducto.objects.create(
            realizada=self,
            producto=producto,
            cantidad=cantidad,
            precio=precio,
        )

    def pagar(self, monto):
        pass



class RealizadaServicio(models.Model):

    class Meta:
        unique_together = ("realizada", "servicio")
        index_together = ["realizada", "servicio"]

    realizada = models.ForeignKey(
        Realizada,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='realizada_servicios'
    )

    servicio = models.ForeignKey(
        Servicio,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='servicio_realizadas'
    )

    cantidad = models.PositiveSmallIntegerField()

    precio = models.DecimalField(
        max_digits=Practica.MAX_DIGITOS,
        decimal_places=Practica.MAX_DECIMALES,
        validators = [
            MinValueValidator(Practica.MIN_PRECIO, message=("El precio no puede ser menor a {:.%df}" % (Practica.MAX_DECIMALES)).format(Practica.MIN_PRECIO)),
            DecimalValidator(max_digits=Practica.MAX_DIGITOS, decimal_places=Practica.MAX_DECIMALES)
        ]
    )

    observaciones = models.TextField(blank=True)

    def save(self, *args, **kwargs):

        if (not "commit" in kwargs) or (kwargs["commit"]):
            if (self.precio is None) and (not self.servicio is None):
                self.precio = self.servicio.precioManoDeObra

        super().save(*args, **kwargs)



class RealizadaProducto(models.Model):

    class Meta:
        unique_together = ("realizada", "producto")
        index_together = ["realizada", "producto"]

    realizada = models.ForeignKey(
        Realizada,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='realizada_productos'
    )

    producto = models.ForeignKey(
        Producto,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='producto_realizadas'
    )

    cantidad = models.PositiveSmallIntegerField()

    precio = models.DecimalField(
        max_digits=Practica.MAX_DIGITOS,
        decimal_places=Practica.MAX_DECIMALES,
        validators = [
            MinValueValidator(Practica.MIN_PRECIO, message=("El precio no puede ser menor a {:.%df}" % (Practica.MAX_DECIMALES)).format(Practica.MIN_PRECIO)),
            DecimalValidator(max_digits=Practica.MAX_DIGITOS, decimal_places=Practica.MAX_DECIMALES)
        ]
    )

    observaciones = models.TextField(blank=True)

    def save(self, *args, **kwargs):

        if (not "commit" in kwargs) or (kwargs["commit"]):
            if (self.precio is None) and (not self.producto is None):
                self.precio = self.producto.precioPorUnidad

        super().save(*args, **kwargs)



class Cancelada(Estado):
    TIPO = 4

    motivo = models.TextField(blank=True)



class Facturada(Estado):
    TIPO = 6



for Klass in (Creada, Presupuestada, Programada, Realizada, Facturada, Cancelada):
    Estado.register(Klass)
