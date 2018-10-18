from decimal import Decimal
from django.db import models
from django.apps import apps
from datetime import date, timedelta, time, datetime
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, DecimalValidator



class FranjaHoraria():
    """

    Clase auxiliar para lidiar con los horarios (si si es una exageracion)

    """

    def __init__(self, inicio, fin):
        """ Crea una franja a partir de dos datetime.time """
        self._inicio = inicio
        self._fin = fin

    def __eq__(self, otra):
        """ Compara igualdad/desigualdad de franjas horarias """
        return (
            self._inicio == otra._inicio and
            self._fin == otra._fin
        )

    def __str__(self):
        """ Strings de franjas horarias """
        return '{} hs. a {} hs.'.format(
            self._inicio.strftime("%H:%M"),
            self._fin.strftime("%H:%M")
        )

    @property
    def duracion(self):
        """ Cantidad de minutos que abarca la franja """
        i = datetime.combine(date.today(), self._inicio)
        j = datetime.combine(date.today(), self._fin)
        d = j - i

        if j < i:
            d = timedelta(hours=24) + d

        return int(d.total_seconds() / 60)

    @property
    def inicio(self):
        """ datetime.time que representa el momento de inicio de la franja horaria """
        return self._inicio

    @property
    def fin(self):
        """ datetime.time que representa el momento de fin de la franja horaria """
        return self._fin

    def abarca(self, t):
        """ True si <t> pertenece al rango de la franja horaria """
        return self._inicio <= t and self._fin >= t



class TipoDeAtencionManager(models.Manager):
    """

    Por ahora no veo la necesidad de crear un Manager para
    los Tipos de Atencion aunque puede ser que lo dejemos

    """

    def habilitados(self):
        """ Tipos de Atencion habilitados """

        return self.filter(baja=False)

    def deshabilitados(self):
        """ Tipos de Atencion deshabilitados """

        return self.filter(baja=True)



class TipoDeAtencion(models.Model):
    """

    Model para los Tipos de Atencion

    """

    # Manager para Tipos de Atencion
    objects = TipoDeAtencionManager()

    RECARGO_PARTE_ENTERA = 3
    RECARGO_PARTE_DECIMAL = 2
    RECARGO_MIN_VALUE = Decimal(0)
    RECARGO_MAX_VALUE = Decimal(900.00)

    MAX_NOMBRE = 100
    MIN_NOMBRE = 3
    REGEX_NOMBRE = '^[0-9a-zA-Z-_ .]{3,100}$'

    EN_VETERINARIA = 'VET'
    EN_DOMICILIO = 'DOM'

    LUGAR = {
        'VET' : 'Veterinaria',
        'DOM' : 'Domicilio'
    }

    LUGARES_DE_ATENCION = tuple(LUGAR.items())

    RECARGO_DEFAULT = 0
    LUGAR_DEFAULT = EN_VETERINARIA



    #---------------------- Model Fields ----------------------

    id = models.AutoField(
        primary_key=True,
        unique=True,
        editable=False
    )

    nombre = models.CharField(
        max_length=MAX_NOMBRE,
        unique=True,
        validators = [
            RegexValidator(regex=REGEX_NOMBRE)
        ],
        error_messages = {
            'unique' : "Otro tipo de atencion tiene ese nombre",
            'max_length' : "El nombre puede tener a lo sumo {} caracteres".format(MAX_NOMBRE),
            'blank' : "El nombre es obligatorio"
        }
    )

    descripcion = models.TextField(
        blank=True
    )

    emergencia = models.BooleanField(
        default=False
    )

    lugar = models.CharField(
        max_length=3,
        default=LUGAR_DEFAULT,
        choices=LUGARES_DE_ATENCION,
        error_messages = {
            'invalid_choice' : "Opcion invalida",
            'blank' : "El lugar de atencion es obligatorio"
        }
    )

    recargo = models.DecimalField(
        max_digits=RECARGO_PARTE_ENTERA+RECARGO_PARTE_DECIMAL,
        decimal_places=RECARGO_PARTE_DECIMAL,
        default=RECARGO_DEFAULT,
        validators = [
            MinValueValidator(RECARGO_MIN_VALUE, message=("El recargo no puede ser menor a {:.%df}" % (RECARGO_PARTE_DECIMAL)).format(RECARGO_MIN_VALUE)),
            MaxValueValidator(RECARGO_MAX_VALUE, message=("El recargo no puede ser mayor a {:.%df}" % (RECARGO_PARTE_DECIMAL)).format(RECARGO_MAX_VALUE)),
            DecimalValidator(max_digits=RECARGO_PARTE_ENTERA+RECARGO_PARTE_DECIMAL, decimal_places=RECARGO_PARTE_DECIMAL)
        ]
    )


    tipoDeServicio = models.CharField(
        max_length=25,
        choices=apps.get_model('GestionDeServicios', 'Servicio', require_ready=False).TIPO,
        error_messages = {
            'invalid_choice' : "Opcion invalida",
            'blank' : "El tipo de servicio es obligatorio"
        }
    )

    inicioFranjaHoraria = models.TimeField(
        error_messages = {
            'invalid' : 'El formato debe ser HH:MM, por ejemplo "01:23"',
            'blank' : 'El inicio de horario de atencion es obligatorio'
        }
    )

    finFranjaHoraria = models.TimeField(
        error_messages = {
            'invalid' : 'El formato debe ser HH:MM, por ejemplo "01:23"',
            'blank' : 'El inicio de horario de atencion es obligatorio'
        }
    )

    baja = models.BooleanField(
        default=False,
        editable=False
    )



    #---------------------- Metodos ----------------------
    def __str__(self):
        """ String para Tipos de Atencion """
        return self.nombre



    @property
    def franjaHoraria(self):
        """ FranjaHoraria a partir de inicio y fin """

        return FranjaHoraria(self.inicioFranjaHoraria, self.finFranjaHoraria)



    @franjaHoraria.setter
    def franjaHoraria(self, franja):
        """ Inicio y fin desde FranjaHoraria """

        self.inicioFranjaHoraria = franja.inicio
        self.finFranjaHoraria = franja.fin



    #[TODO] Averiguar/Ponernos de acuerdo en alguna buena manera de obtener los
    # nombres de los CharFields con choices

    @property
    def lugarStr(self):
        """ String para el nombre del lugar de atencion """

        return TipoDeAtencion.LUGAR[self.lugar]



    @property
    def tipoDeServicioStr(self):
        """ String para el tipo de servicio """

        tuplas = apps.get_model('GestionDeServicios', 'Servicio', require_ready=False).TIPO
        i=0
        while tuplas[i][0] != self.tipoDeServicio:
            i=i+1

        return tuplas[i][1]

