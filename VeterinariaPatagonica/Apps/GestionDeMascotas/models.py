from datetime import datetime, date
from django.db import models
from django.core.validators import RegexValidator
from django.db.models import Q
from Apps.GestionDeClientes import models as gcmodels
from VeterinariaPatagonica.tools import BajasLogicasQuerySet

# Create your models here.
class BaseMascotaManager(models.Manager):
    def __init__(self, tipo=None):
        super().__init__()
        self.tipo = tipo

    def get_queryset(self):
        qs = super().get_queryset()
        if self.tipo is not None:
            qs = qs.filter(tipo=self.tipo)
        return qs

class MascotaQueryset(BajasLogicasQuerySet):
        MAPEO_ORDEN = {
        "orden_patente" : ["patente"],
        "orden_nombre" : ["nombre"],
        "orden_cliente" : ["cliente"],
        "orden_especie" : ["especie"],
    }

MascotaManager = BaseMascotaManager.from_queryset(MascotaQueryset)

class Mascota(models.Model):

    class Meta:
        permissions=(
            ("mascota_crear", "crear"),
            ("mascota_modificar", "modificar"),
            ("mascota_eliminar", "eliminar"),
            ("mascota_ver_habilitados", "ver_habilitados"),
            ("mascota_listar_habilitados", "listar_habilitados"),
            ("mascota_ver_no_habilitados", "ver_no_habilitados"),
            ("mascota_listar_no_habilitados", "listar_no_habilitados"),
            ('deshabilitar_mascota', 'deshabilitar_mascota')
        )
        default_permissions = ()
        ordering = ["patente"]

    MAPPER = {
        "especie": "especie__icontains",
        "cliente": "cliente",
        "patente": "patente__icontains",
        "nombre": "nombre__icontains",
        "duenio": lambda value: Q(cliente__nombres__icontains=value) | Q(cliente__apellidos__icontains=value),
        "desde": "fecha__gte"
    }

    MAXPATENTE= 6
    REGEX_NOMBRE = '^[0-9a-zA-Z-_ .]{3,100}$'
    REGEX_ESPECIE = '^[0-9a-zA-Z-_ .]{3,100}$'
    REGEX_RAZA= '^[0-9a-zA-Z-_ .]{3,100}$'
    MAX_NOMBRE = 50
    MIN_NOMBRE= 3
    MAXRAZA = 50
    MAXESPECIE =50

    patente = models.CharField( help_text= "patente la mascota",
        max_length= MAXPATENTE,
        unique= True,
        null= False,
        blank= True,
        error_messages= {
            'max_length': "la patente puede tener a lo sumo {} caracteres".format(MAXPATENTE),
            'unique': "Otra mascota tiene esa patente",
            'blank': "la patente es obligatoria"
        }
    )

    nombre = models.CharField(
        help_text= "Nombre de la mascota",
        max_length = MAX_NOMBRE,
        unique= False,
        null= False,
        blank= False,
        primary_key= False,
        validators= [RegexValidator(regex=REGEX_NOMBRE)],
        error_messages= {
            'max_length': "El nombre puede tener a lo sumo {} caracteres".format(MAX_NOMBRE),
            'blank': "El nombre es obligatorio"
        }
    )

    cliente = models.ForeignKey(
        gcmodels.Cliente,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        help_text="Ingrese cliente",
        error_messages={
        }
    )

    fechaNacimiento = models.DateField(
        help_text="Fecha de nacimiento de la mascota",
        unique=False,
        null=False,
        blank=False,
        default=datetime.now,
        error_messages={'required': "la fecha es obligatorio"})

    especie = models.CharField(
        help_text= "Especie de la Mascota",
        max_length = MAXESPECIE,
        unique= False,
        null= False,
        blank= False,
        primary_key= False,
        validators= [RegexValidator(regex=REGEX_ESPECIE)],
        error_messages= {
            'max_length': "La especie puede tener a lo sumo {} caracteres".format(MAXESPECIE),
            'blank': "La especie es obligatorio"
        }
    )

    raza = models.CharField(
        help_text="Especie de la Mascota",
        max_length=MAXRAZA,
        unique=False,
        null=False,
        blank=False,
        primary_key=False,
        validators=[RegexValidator(regex=REGEX_RAZA)],
        error_messages={
            'max_length': "La especie puede tener a lo sumo {} caracteres".format(MAXESPECIE),
            'blank': "La especie es obligatorio"}
    )


    baja = models.BooleanField(default=False)

    objects = MascotaManager()

    def __str__(self):
        return "{0}, {1}".format(self.nombre, self.especie)


    def generadorDePatente(self, id):

         if self.patente is '':
             self.patente= "Vet-" + str(id)
         return self.patente
