from django.db import models
from django.apps import apps
from datetime import date, timedelta, time, datetime
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

"""
Clase auxiliar para lidiar con los horarios (si si es una exageracion)
"""
class FranjaHoraria():

    def __init__(self, inicio, fin):
        self.inicio = inicio
        self.fin = fin

    def __eq__(self, otra):
        return (
            self.inicio == otra.inicio and
            self.fin == otra.fin
        )

    def __str__(self):
        return '{} hs. a {} hs.'.format(
            self.inicio.strftime("%H:%M"),
            self.fin.strftime("%H:%M")
        )

    def calcular_duracion(self):

        i = datetime.combine(date.today(), self.inicio)
        j = datetime.combine(date.today(), self.fin)
        d = j - i

        if j < i:
            d = timedelta(hours=24) + d

        return int(d.total_seconds() / 60)

    def abarca(self, t):

        return self.inicio <= t and self.fin >= t



class TipoDeAtencion(models.Model):

    MAX_NOMBRE = 100
    MIN_NOMBRE = 3
    REGEX_NOMBRE = '^[0-9a-zA-Z-_ .]{3,100}$'

    EN_VETERINARIA = 'VET'
    EN_DOMICILIO = 'DOM'

    LUGARES_DE_ATENCION_DICT = {
        EN_VETERINARIA : 'Veterinaria',
        EN_DOMICILIO : 'Domicilio'
    }

    LUGARES_DE_ATENCION = (
        (EN_VETERINARIA, 'Veterinaria'),
        (EN_DOMICILIO, 'Domicilio')
    )

    RECARGO_DEFAULT = 0

    LUGAR_DEFAULT = EN_VETERINARIA



    id = models.AutoField(
        primary_key=True,
        unique=True,
        editable=False
    )

    nombre = models.CharField(
        help_text="Nombre del tipo de atencion",
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
        help_text="Descripcion del tipo de atencion",
        blank=True
    )

    emergencia = models.BooleanField(
        help_text="Determina el grado de urgencia del tipo de atencion",
        default=False
    )

    lugar = models.CharField(
        verbose_name="Lugar de atencion",
        help_text="Lugar en donde se realiza el tipo de atencion",
        max_length=3,
        default=LUGAR_DEFAULT,
        choices=LUGARES_DE_ATENCION,
        error_messages = {
            'invalid_choice' : "Opcion invalida",
            'blank' : "El lugar de atencion es obligatorio"
        }
    )
        #choices=LUGARES_DE_ATENCION_DICT.items(),

    recargo = models.FloatField(
        verbose_name="Porcentaje de recargo",
        help_text="Porcentaje de recargo sobre el costo del servicio a aplicar",
        default=RECARGO_DEFAULT,
        validators = [
            MinValueValidator(0, message='ERROR'),
            MaxValueValidator(100, message='ERRORR')
        ],
        error_messages = {
            'blank' : "El porcentaje de recargo es obligatorio",
        }
    )



    tipo_de_servicio = models.CharField(
        verbose_name='Tipo de servicio',
        help_text='Tipo de servicio',
        max_length=25,
        choices=apps.get_model('GestionDeServicios', 'Servicio', require_ready=False).t_tipo,
        error_messages = {
            'invalid_choice' : "Opcion invalida",
            'blank' : "El tipo de servicio es obligatorio"
        }
    )

    inicio_franja_horaria = models.TimeField(
        verbose_name="Inicio de horario de atencion",
        help_text='Hora de inicio del tipo de atencion',
        error_messages = {
            'invalid' : 'El formato debe ser HH:MM, por ejemplo "01:23"',
            'blank' : 'El inicio de horario de atencion es obligatorio'
        }
    )

    fin_franja_horaria = models.TimeField(
        verbose_name="Fin de horario de atencion",
        help_text='Hora de finalizacion del tipo de atencion',
        error_messages = {
            'invalid' : 'El formato debe ser HH:MM, por ejemplo "01:23"',
            'blank' : 'El inicio de horario de atencion es obligatorio'
        }
    )

    baja = models.BooleanField(
        help_text='Deshabilitado',
        default=False
    )



    def __str__(self):

        return self.nombre



    def crear_franja_horaria(self):
        """ to_timerange (o algo por el estilo) """

        return FranjaHoraria(self.inicio_franja_horaria, self.fin_franja_horaria)



    def leer_franja_horaria(self, franja):
        """ from_timerange (o algo por el estilo) """

        self.inicio_franja_horaria = franja.inicio
        self.fin_franja_horaria = franja.fin



    def lugar_str(self):

        tuplas = TipoDeAtencion.LUGARES_DE_ATENCION
        i=0
        while tuplas[i][0] != self.lugar:
            i=i+1

        return tuplas[i][1]



    def tipo_de_servicio_str(self):

        tuplas = apps.get_model('GestionDeServicios', 'Servicio', require_ready=False).t_tipo
        i=0
        while tuplas[i][0] != self.tipo_de_servicio:
            i=i+1

        return tuplas[i][1]

