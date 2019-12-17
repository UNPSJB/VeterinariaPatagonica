from decimal import Decimal
from datetime import datetime

from django.db import models
from django.db.models import Q, F, Value, TimeField, BooleanField, Case, When
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, DecimalValidator

from VeterinariaPatagonica.tools import BajasLogicasQuerySet, R
from VeterinariaPatagonica.areas import Areas



class TipoDeAtencionQueryset(BajasLogicasQuerySet):

    MAPEO_FILTRADO = {
        "nombre" : "nombre__icontains",
        "emergencia" : "emergencia",
        "lugar" : "lugar",
        "desde" : lambda value: R(
            finFranjaHoraria__gt=value,
            inicioFranjaHoraria__gt=F("finFranjaHoraria"),
        ),
        "hasta" : lambda value: R(
            inicioFranjaHoraria__lt=value,
            inicioFranjaHoraria__gt=F("finFranjaHoraria"),
        ),
        "desdehasta" : lambda desdehasta: R(
            inicioFranjaHoraria__gt=desdehasta[0],
            finFranjaHoraria__gt=desdehasta[0]
        ) | R(
            inicioFranjaHoraria__lt=desdehasta[1],
            finFranjaHoraria__lt=desdehasta[1],
        ) | (
            Q(
                inicioFranjaHoraria__lt=desdehasta[0],
                finFranjaHoraria__gt=desdehasta[1]
            ) & Q(
                inicioFranjaHoraria__gt=F("finFranjaHoraria")
            )
        ),
    }

    MAPEO_ORDEN = {
        "id" : ["id"],
        "nombre" : ["nombre"],
        "emergencia" : ["emergencia"],
        "lugar" : ["lugar"],
        "recargo" : ["recargo"],
        "iniciofranjahoraria" : ["inicioFranjaHoraria"],
    }

    def paraConsultas(self):
        return self.filter(tipoDeServicio=Areas.C.codigo())

    def paraCirugias(self):
        return self.filter(tipoDeServicio=Areas.Q.codigo())

    def validosPrimero(self, primeroValidos=True):
        seleccionados = Q(
            inicioFranjaHoraria__lt=F("finFranjaHoraria"),
            inicioFranjaHoraria__lte=F("ahora"),
            finFranjaHoraria__gte=F("ahora"),
        ) | Q(
            Q(inicioFranjaHoraria__gt=F("finFranjaHoraria")),
            R(
                inicioFranjaHoraria__lte=F("ahora"),
                finFranjaHoraria__gte=F("ahora")
            )
        )
        validez = "-valido" if primeroValidos else "valido"
        return self.annotate(
            ahora=Value(
                datetime.now().timetz(),
                output_field=TimeField()
            )
        ).annotate(
            valido=Case(
                When(seleccionados, then=True),
                default=Value(False),
                output_field=BooleanField()
            )
        ).order_by(validez)



TipoDeAtencionManager = models.Manager.from_queryset(TipoDeAtencionQueryset)



class TipoDeAtencion(models.Model):

    class Meta:
        permissions=(
            ("tipodeatencion_crear", "crear"),
            ("tipodeatencion_modificar", "modificar"),
            ("tipodeatencion_eliminar", "eliminar"),
            ("tipodeatencion_ver_habilitados", "ver_habilitados"),
            ("tipodeatencion_listar_habilitados", "listar_habilitados"),
            ("tipodeatencion_ver_no_habilitados", "ver_no_habilitados"),
            ("tipodeatencion_listar_no_habilitados", "listar_no_habilitados"),
            ("tipodeatencion_exportar_excel_habilitados", "exportar_habilitados_excel"),
            ("tipodeatencion_exportar_excel_deshabilitados", "exportar_deshabilitados_excel"),
        )
        default_permissions = ()

    objects = TipoDeAtencionManager()


    RECARGO_PARTE_ENTERA = 3
    RECARGO_PARTE_DECIMAL = 2
    RECARGO_MIN_VALUE = Decimal(0)
    RECARGO_MAX_VALUE = Decimal(900.00)

    MAX_NOMBRE = 100
    MIN_NOMBRE = 1
    REGEX_NOMBRE = "^[0-9áéíóúÁÉÍÓÚñÑa-zA-Z-_ .]{%d,%d}$" % (MIN_NOMBRE, MAX_NOMBRE)

    EN_VETERINARIA = "V"
    EN_DOMICILIO = "D"

    LUGARES_DE_ATENCION = (
        (EN_VETERINARIA, "Veterinaria"),
        (EN_DOMICILIO, "Domicilio")
    )

    RECARGO_DEFAULT = Decimal(0)
    LUGAR_DEFAULT = EN_VETERINARIA



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
            "unique" : "Otro tipo de atencion tiene ese nombre",
            "max_length" : "El nombre puede tener a lo sumo {} caracteres".format(MAX_NOMBRE),
            "blank" : "El nombre es obligatorio"
        }
    )

    descripcion = models.TextField(
        blank=True,
    )

    emergencia = models.BooleanField(
        default=False
    )

    lugar = models.CharField(
        max_length=1,
        default=LUGAR_DEFAULT,
        choices=LUGARES_DE_ATENCION,
        error_messages = {
            "invalid_choice" : "La opcion no es valida",
            "blank" : "El lugar de atencion es obligatorio"
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
        max_length=1,
        choices=Areas.paresOrdenados(),
        error_messages = {
            "invalid_choice" : "La opcion no es valida",
            "blank" : "El tipo de servicio es obligatorio"
        }
    )

    inicioFranjaHoraria = models.TimeField(
        error_messages = {
            "invalid" : "El formato debe ser <horas>:<minutos>, por ejemplo 01:23",
            "blank" : "El inicio de horario de atencion es obligatorio"
        }
    )

    finFranjaHoraria = models.TimeField(
        error_messages = {
            "invalid" : "El formato debe ser <horas>:<minutos>, por ejemplo 01:23",
            "blank" : "El inicio de horario de atencion es obligatorio"
        }
    )

    baja = models.BooleanField(
        default=False,
        editable=False
    )

    def esValido(self, cuando):

        inicio = self.inicioFranjaHoraria
        fin = self.finFranjaHoraria
        horario = cuando.time()

        return (
            inicio <= horario <= fin
        ) or (
            (inicio >= fin) and (inicio <= horario or fin >= horario)
        )

    def __str__(self):
        return self.nombre
