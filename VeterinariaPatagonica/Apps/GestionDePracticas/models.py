from django.db import models
from Apps.GestionDeClientes import models as gcmodels
from Apps.GestionDeServicios import models as gsmodels
from Apps.GestionDeTiposDeAtencion import models as gtdamodels
from Apps.GestionDeMascotas import models as gmmodels



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
    MAX_DIGITOS = 8
    MAX_DECIMALES = 2

#-----------Atributos.--------------
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
            decimal_places = MAX_DECIMALES
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
    servicio = models.ForeignKey(
            gsmodels.Servicio,
            null = False,
            blank = False,
            on_delete = models.CASCADE,
            error_messages = {
            })
    tipoDeAtencion = models.ForeignKey(
            gtdamodels.TipoDeAtencion,
            null = False,
            blank = False,
            on_delete = models.CASCADE,
            error_messages = {
            })


#-----------Metodos.--------------------
    def estado(self):
        if self.estados.exists():
            return self.estados.latest().related()

    @classmethod
    def new(cls, tipo):
        t = cls(tipo=tipo)
        t.save()
        t.hacer(None, observacion="Arranca el permiso")
        return t

    def estados_related(self):
        return [estado.related() for estado in self.estados.all()]

    def hacer(self, accion, *args, **kwargs):
        estado_actual = self.estado()
        if estado_actual is not None and hasattr(estado_actual, accion):
            metodo = getattr(estado_actual, accion)
            estado_nuevo = metodo(self, *args, **kwargs)
            if estado_actual is not None:
                estado_nuevo.save()
        elif estado_actual is None:
            Creada(permiso=self, *args, **kwargs).save()
        else:
            raise Exception("La accion solicitada no se pudo realizar")



class Estado(models.Model):
    TIPO = 0
    TIPOS = [
        (0, 'estado')
    ]
    practica = models.ForeignKey(Practica, related_name="estados")
    tipo = models.PositiveSmallIntegerField(choices=TIPOS)
    usuario = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        get_latest_by = 'tipo'

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
        return Cancelada(self)



class Creada(Estado):
    TIPO = 1

    def programar(self, practica):#¿Poner turno como parametro? en ese caso, ¿inicializar?- supongo que si.
        #[TODO]Alguna validacion si se requiere.
        return Programada(practica = practica)

    def presupuestar(self, practica, porcentajeDescuento, diasMantenimiento):
        if porcentajeDescuento >= 0 :

            porcentajeDescuento = porcentajeDescuento
            diasMantenimiento = diasMantenimiento
            practica.save()

            return Presupuestada(practica = practica)
        return self

class Programada(Estados):
    TIPO = 2
    turno = models.DateTimeField(auto_now = True)
    motivoReprogramacion = models.CharField(max_length = MAX_NOMBRE)

    def reprogramar(self, practica, motivoReprogramacion):
        pass

    def pagar(self, practica, monto):
        pass

    def realizar(self, practica):
        pass

class Presupuestada(Estados):
    TIPO = 3
    porcentajeDescuento = models.PositiveSmallIntegerField()
    diasMantenimiento = models.PositiveSmallIntegerField()
    #[TODO]fechaMantenimientoOferta = fechaActual+diasMantenimiento.

def confirmar(self, practica, turno):
    #[TODO]if fechaActual < fechaMantenimientoOferta: return Programada(self, practica, turno)
    pass

class Cancelada(Estados):
    TIPO = 4

class Realizada(Estados):
    TIPO = 5

    def pagar(self, practica, monto):
        pass

class Facturada(Estados):
    TIPO = 6


for Klass in [Creada, Programada, Presupuestada, Cancelada, Realizada, Facturada]:
    Estado.register(Klass)
