from decimal import Decimal
from datetime import datetime, timedelta

from django.db import models
from django.core.validators import MinValueValidator, DecimalValidator
from django.db import transaction

from Apps.GestionDeServicios.models import Servicio
from Apps.GestionDeProductos.models import Producto
from Apps.GestionDeClientes.models import Cliente
from Apps.GestionDeTiposDeAtencion.models import TipoDeAtencion
from Apps.GestionDeMascotas.models import Mascota
from Apps.GestionDeClientes import models as gcmodels
from Apps.GestionDeServicios import models as gsmodels
from Apps.GestionDeTiposDeAtencion import models as gtdamodels
from Apps.GestionDeMascotas import models as gmmodels
from VeterinariaPatagonica.errores import VeterinariaPatagonicaError
from VeterinariaPatagonica.tools import VeterinariaPatagonicaQuerySet

#from Apps.GestionDeFacturas.models import Factura


__all__ = [ "Practica", "PracticaServicio", "PracticaProducto", "TIPO_PRACTICA" ]



#[TODO]: Seria mejor que estas definiciones no esten repetidas,
TIPO_PRACTICA = {
    "consulta" : "C",
    "cirugia" : "Q",
}




class PracticaBaseManager(models.Manager):
    def __init__(self, tipo = None):
        super().__init__()
        self.tipo = tipo

    def get_queryset(self):
        qs = super().get_queryset()
        if self.tipo:
            qs = qs.filter(tipoDeAtencion__tipoDeServicio=self.tipo)
        return qs

class PracticaQuerySet(VeterinariaPatagonicaQuerySet):

    def enEstado(self, estados):

        if type(estados) != list:
            estados = [estados]

        return self.annotate(max_id=models.Max('estados__id')).filter(
            estados__id=models.F('max_id'),
            estados__tipo__in=[ e.TIPO for e in estados])

    def deTipo(self, tipo):
        return self.filter(tipoDeAtencion__tipoDeServicio=TIPO_PRACTICA[tipo])

PracticaManager = PracticaBaseManager.from_queryset(PracticaQuerySet)

class Practica(models.Model):

    objects = PracticaManager()
    consultas = PracticaManager(Servicio.CONSULTA)
    quirurgicas = PracticaManager(Servicio.QUIRURGICA)
    internaciones = PracticaManager(Servicio.INTERNACION)

    MAX_NOMBRE = 100
    MAX_MOTIVO = 300
    MAX_DIGITOS = 8
    MAX_DECIMALES = 2
    MAX_DIGITOS_AJUSTES = 5
    MAX_DECIMALES_AJUSTES = 2
    MIN_PRECIO = Decimal(0)

    MAPPER = {
        "cliente" : lambda value: models.Q(cliente__nombres__icontains=value) | models.Q(cliente__apellidos__icontains=value),
        "tipoDeAtencion" : "tipoDeAtencion__nombre__icontains",
        "estado" : lambda value: models.Q(estados__id=models.F('max_id')) & models.Q(estados__tipo=value),
        "desde" : lambda value: models.Q(estados__id=models.F('max_id')) & models.Q(estados__marca__gte=value),
        "hasta" : lambda value: models.Q(estados__id=models.F('max_id')) & models.Q(estados__marca__lte=value),
        "servicios" : "servicios__nombre__icontains",
    }


    id = models.AutoField(
        primary_key=True,
        unique=True,
        editable=False
    )

    # Es mejor guardar el precio que sacar la cuenta en funcion de los subtotales?
    precio = models.DecimalField(
            blank=True,
            null = True,
            max_digits = MAX_DIGITOS,
            decimal_places = MAX_DECIMALES,
            error_messages = {
                'max_digits': "Cantidad de digitos ingresados supera el máximo."
            },
            validators = [],
    )
    cliente = models.ForeignKey(
        Cliente,
        related_name='practicas',
        null=False,
        blank=False,
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
        null=False,
        blank=False,
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
        related_name='practicas'
    )

    productos = models.ManyToManyField(
        Producto,
        through='PracticaProducto',
        through_fields=('practica','producto'),
        related_name='practicas'
    )

    turno = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        null=True,
    )

    senia = models.PositiveSmallIntegerField(
        null = True
    )

    def __str__(self):
        return "{} {}".format(self.tipoDeAtencion.get_tipoDeServicio_display(), self.id)

    def duracion(self):
        return sum([servicio.servicio.tiempoEstimado * servicio.cantidad for servicio in self.practica_servicios.all()])

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

        """
        La idea seria que el estado 'Creada' se instancie justo antes del primer 'hacer'?
        Me parece que seria mejor que se instancie la primera vez que se guarde la practica
        Otra alternativa seria instanciarlo la primera vez que se consulte el estado, algo asi:
        """
        """
        if estado_actual is None:
            Creada.objects.create(practica=self)

        if hasattr(estado_actual, accion):
        """

        if hasattr(estado_actual, accion):
            metodo = getattr(estado_actual, accion)
            estado_nuevo = metodo(*args, **kwargs)
            return estado_nuevo

        else:
            raise Exception("La accion: %s solicitada no se pudo realizar sobre el estado %s" % (accion, estado_actual))


    def agregarProducto(self, producto, cantidad):
        """ Agrega <cantidad> unidades de <producto> a la practica, creandolo de ser necesario """

        if not isinstance(producto, Producto):
            producto = Producto.objects.get(pk=producto)

        practicaProducto, creada = self.practica_productos.get_or_create(
            practica=self,
            producto=producto,
            defaults={
                'cantidad' : cantidad,
                'precio' : producto.precioPorUnidad
            }
        )

        if not creada:
            practicaProducto.cantidad += cantidad
            practicaProducto.precio = producto.precioPorUnidad

        practicaProducto.save()



    def agregarServicio(self, servicio, cantidad):
        """ Agrega <cantidad> unidades de <servicio> a la practica, creandolo de ser necesario """

        if not isinstance(servicio, Servicio):
            servicio = Servicio.objects.get(pk=servicio)

        practicaServicio, creada = self.practica_servicios.get_or_create(
            practica=self,
            servicio=servicio,
            defaults={
                'cantidad' : cantidad,
                'precio' : servicio.precioManoDeObra
            }
        )

        if not creada:
            practicaServicio.cantidad += cantidad
            practicaServicio.precio = servicio.precioManoDeObra

        practicaServicio.save()



    def eliminarProducto(self, producto):
        """ Elimina detalle de PracticaProducto de <producto> si es que existe """

        detalle = self.practica_productos.get(producto=producto)
        if detalle:
            detalle.delete()



    def eliminarServicio(self, servicio):
        """ Elimina detalle de PracticaServicio de <servicio> si es que existe """

        detalle = self.practica_servicios.get(servicio=servicio)
        if detalle:
            detalle.delete()



    def agregarProductosServicio(self, servicio, cantidad):
        """ Agrega a la practica los productos necesarios para <cantidad> realizaciones de <servicio> """

        for detalleProducto in servicio.servicio_productos.all():

            cantidadProducto = detalleProducto.cantidad * cantidad
            self.agregarProducto(detalleProducto.producto, cantidadProducto)



    def validarEstado(self, estado):

        actual = self.estado()

        if not isinstance(actual, estado):
            raise VeterinariaPatagonicaError(
                titulo="Solicitud erronea",
                descripcion="La practica debe encontrarse en estado %s, actualmente se encuentra en estado %s" % (estado.__name__, actual.__class__.__name__),
            )

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

class PracticaServicio(models.Model):

    class Meta:
        unique_together = ("practica", "servicio")
        index_together = ["practica", "servicio"]

    practica = models.ForeignKey(
        Practica,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='practica_servicios'
    )

    servicio = models.ForeignKey(
        Servicio,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='servicio_practicas'
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



    def save(self, *args, **kwargs):

        if (not "commit" in kwargs) or (kwargs["commit"]):
            if (self.precio is None) and (not self.servicio is None):
                self.precio = self.servicio.precioManoDeObra

        super().save(*args, **kwargs)


    def __str__(self):
        return "{}: {}".format(self.servicio.nombre, self.cantidad)

    def precioTotal(self):
        return self.precio * self.cantidad


class PracticaProducto(models.Model):

    class Meta:
        unique_together = ("practica", "producto")
        index_together = ["practica", "producto"]

    practica = models.ForeignKey(
        Practica,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='practica_productos'
    )

    producto = models.ForeignKey(
        Producto,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='producto_practicas'
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

    def precioTotal(self):
        return self.precio * self.cantidad

    def save(self, *args, **kwargs):

        if (not "commit" in kwargs) or (kwargs["commit"]):
            if (self.precio is None) and (not self.producto is None):
                self.precio = self.producto.precioPorUnidad

        super().save(*args, **kwargs)



    def __str__(self):
        return "{}: {}".format(self.producto.nombre, self.cantidad)
