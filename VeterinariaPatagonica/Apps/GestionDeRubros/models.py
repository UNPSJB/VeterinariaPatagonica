from django.db import models
from django.core.validators import RegexValidator
from VeterinariaPatagonica import tools
from django.db.models import Q
from VeterinariaPatagonica.tools import BajasLogicasQuerySet

# Create your models here.

class BaseRubroManager(models.Manager):
    def __init__(self, tipo=None):
        super().__init__()
        self.tipo = tipo

    def get_queryset(self):
        qs = super().get_queryset()
        if self.tipo is not None:
            qs = qs.filter(tipo=self.tipo)
        return qs

class RubroQueryset(BajasLogicasQuerySet):
        MAPEO_ORDEN = {
            "orden_nombre": ["nombre"],
            "orden_descripcion": ["descripcion"],
        }

RubroManager = BaseRubroManager.from_queryset(RubroQueryset)

class Rubro (models.Model):
    class Meta:
        permissions=(
            ("rubro_crear", "crear"),
            ("rubro_modificar", "modificar"),
            ("rubro_eliminar", "eliminar"),
            ("rubro_ver_habilitados", "ver_habilitados"),
            ("rubro_listar_habilitados", "listar_habilitados"),
            ("rubro_ver_no_habilitados", "ver_no_habilitados"),
            ("rubro_listar_no_habilitados", "listar_no_habilitados"),
            ('deshabilitar_rubro', 'deshabilitar_rubro')
            #("rubro_exportar_excel_habilitados", "exportar_habilitados_excel"),
            #("rubro_exportar_excel_deshabilitados", "exportar_deshabilitados_excel"),
        )
        default_permissions = ()
        ordering = ["nombre", "descripcion"]

    MAPPER = {
        "nombre": "nombre__icontains",
        "descripcion": "descripcion__icontains",
    }

    REGEX_NOMBRE = '^[0-9a-zA-Z-_ .]{3,100}$'
    MAXNOMBRE = 50
    MAXDESCRIPCION = 150

    nombre = models.CharField(
        help_text= "Nombre del Rubro",
        max_length = MAXNOMBRE,
        unique= True,
        null= False,
        blank= False,
        primary_key= False,
        validators= [RegexValidator(regex=REGEX_NOMBRE)],
        error_messages= {
            'max_length': "El nombre puede tener a lo sumo {} caracteres".format(MAXNOMBRE),
            'blank': "El nombre es obligatorio"
        }
    )

    descripcion = models.TextField(
        help_text="Descripcion del Rubro",
        max_length=MAXDESCRIPCION,
        unique=False,
        null=True,
        blank=True,
        primary_key=False,
        error_messages={
            'max_length': "La descripcion puede tener a lo sumo {} caracteres".format(MAXNOMBRE),
        }
    )

    baja = models.BooleanField(default=False)

    objects = RubroManager()


    def __str__ (self):
        return "{0}, {1}".format(self.nombre,self.descripcion)