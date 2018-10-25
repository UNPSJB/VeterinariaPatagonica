
from django.db import models
from django.contrib.auth.models import User
from Apps.GestionDeClientes import models as gcmodels
from Apps.GestionDeServicios import models as gsmodels
from Apps.GestionDeTiposDeAtencion import models as gtdamodels
from Apps.GestionDeMascotas import models as gmmodels
from Apps.GestionDeProductos import models as gpmodels



class PracticaBaseManager(models.Manager):
    pass

class PracticaQuerySet(models.QuerySet):
    def en_estado(self, estados):
        if type(estados) != list:
            estados = [estados]
        return self.annotate(max_id=models.Max('estados__id')).filter(
            estados__id=models.F('max_id'),
            estados__tipo__in=[ e.TIPO for e in estados])

PracticaManager = PracticaBaseManager.from_queryset(PracticaQuerySet)

class Practica(models.Model):
#------------Constantes.------------------
    MAX_NOMBRE = 100
    REGEX_NOMBRE = '^[0-9a-zA-Z-_ .]{3,100}$'
    MAX_DIGITOS = 8
    MAX_DECIMALES = 2

#-----------Atributos.--------------
    id = models.AutoField(
        primary_key=True,
        unique=True,
        editable=False
    )
    nombre = models.CharField(
            max_length = MAX_NOMBRE,
            unique = True,
            null = False,
            blank = False,
            error_messages = {
                'unique' : "Otra práctica tiene ese nombre.",
                'max_length' : "El nombre puede tener a lo sumo {} caracteres.".format(MAX_NOMBRE),
                'blank' : "El nombre es obligatorio."
                })
    precio = models.DecimalField(
            max_digits = MAX_DIGITOS,
            decimal_places = MAX_DECIMALES,
            error_messages = {
                'max_digits': "Cantidad de digitos ingresados supera el máximo."
            })
    cliente = models.ForeignKey(
            gcmodels.Cliente,
            null=False,
            blank = False,
            on_delete=models.CASCADE,
            error_messages = {
            })
    servicios = models.ManyToManyField(gsmodels.Servicio,
        through='PracticaServicio',
        through_fields=('practica', 'servicio'),
    )
    productosReales = models.ManyToManyField(gpmodels.Producto,
        #verbose = 'Insumos Reales',
        through='PracticaProducto',
        through_fields=('practica', 'producto'),
    )

    tipoDeAtencion = models.ForeignKey(
            gtdamodels.TipoDeAtencion,
        #    verbose = 'Tipo de Atención',
            null = False,
            blank = False,
            on_delete = models.CASCADE,
            error_messages = {
            })

#--------------Metodos.--------------------
    def precioReal(self):
        total = Decimal("0")
        for sproducto in self.productos.all():
            total += sproducto.producto.precioEnUnidad(sproducto.cantidad)
        for servicio in self.servicios.all():
            total += servicio.precioManoDeObra
        return total

    def precioEstimado(self):
        total = Decimal("0")
        for servicio in self.servicios.all():
            total += servicio.precio()
        return total

    def estado(self):
        if self.estados.exists():
            return self.estados.latest().related()

    @classmethod
    def new(cls, *args, **kwargs):
        t = cls(*args, **kwargs)
        t.save()
        t.hacer("crear")
        return t

    def estados_related(self):
        return [estado.related() for estado in self.estados.all()]

    def hacer(self, accion, *args, **kwargs):
        estado_actual = self.estado()
        if estado_actual is not None and hasattr(estado_actual, accion):
            metodo = getattr(estado_actual, accion)
            estado_nuevo = metodo(self, *args, **kwargs)
        elif estado_actual is None:
            Creada(practica=self, *args, **kwargs).save()
        else:
            raise Exception("La accion: %s solicitada no se pudo realizar sobre el estado %s" % (accion, estado_actual))

#---------Definicion de la clase necesaria para manejar Servicios ----------
class PracticaServicio(models.Model):
    practica = models.ForeignKey(Practica, on_delete=models.CASCADE)
    servicio = models.ForeignKey(gsmodels.Servicio, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

#---------Definicion de la clase necesaria para manejar Insumos ----------
class PracticaProducto(models.Model):
    practica = models.ForeignKey(Practica, on_delete=models.CASCADE)
    producto = models.ForeignKey(gpmodels.Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

#---------Definicion de la superclase de los Estados---------
class Estado(models.Model):
    TIPO = 0
    TIPOS = [
        (0, 'estado')
    ]
    marca = models.DateTimeField(auto_now=True)
    practica = models.ForeignKey(Practica, related_name="estados", on_delete=models.CASCADE)
    tipo = models.PositiveSmallIntegerField(choices=TIPOS)
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        get_latest_by = 'marca'

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.tipo = self.__class__.TIPO
        super(Estado, self).save(*args, **kwargs)

    def related(self):
        return self.__class__ != Estado and self or getattr(self, self.get_tipo_display())

    @classmethod
    def register(cls, klass):
        cls.TIPOS.append((klass.TIPO, klass.__name__.lower()))

    def cancelar(self):
        return Cancelada.objects.create(practica=self.practica)

    def __str__(self):
        return self.__class__.__name__

#---------Sección donde definimos cada estado con sus respectivos métodos.----------
class Creada(Estado):
    TIPO = 1

    def programar(self, practica, turno):#¿Poner turno como parametro? en ese caso, ¿inicializar?- supongo que si.
        if (turno >= datetime.now()):
            return Programada.objects.create(practica = self.practica, turno=turno)
        else:
            raise Exception("error: %s es una fecha inválida" % (turno.__str__()));
            return None

    def presupuestar(self, practica, porcentajeDescuento, diasMantenimiento):
        if not (0 <= porcentajeDescuento <= 100):
            raise Exception("El porcentaje debe ser entre 0 y 100")
        return Presupuestada.objects.create(practica = practica, porcentajeDescuento=porcentajeDescuento, diasMantenimiento = diasMantenimiento)

class Programada(Estado):
    TIPO = 2
    turno = models.DateTimeField(auto_now = True)
    motivoReprogramacion = models.CharField(max_length = Practica.MAX_NOMBRE)

    def reprogramar(self, practica, turno, motivoReprogramacion):
        return Programada.objects.create(practica=practica, turno=turno, motivoReprogramacion=motivoReprogramacion)

    def pagar(self, monto):

        pass

    def realizar(self):
        pass

class Presupuestada(Estado):
    TIPO = 3
    porcentajeDescuento = models.PositiveSmallIntegerField()
    diasMantenimiento = models.PositiveSmallIntegerField()
    #[TODO]fechaMantenimientoOferta = fechaActual+diasMantenimiento.

    def seniar(self, practica, turno, monto):
        return Programada.objects.create(practica=practica, turno=turno)

    def confirmar(self, practica, turno):
        #[TODO]if fechaActual < fechaMantenimientoOferta: return Programada(self, practica, turno)
        return Programada.objects.create(practica=practica, turno=turno)

class Cancelada(Estado):
    TIPO = 4

class Realizada(Estado):
    TIPO = 5

    def pagar(self, monto):
        pass

class Facturada(Estado):
    TIPO = 6


for Klass in [Creada, Programada, Presupuestada, Cancelada, Realizada, Facturada]:
    Estado.register(Klass)
