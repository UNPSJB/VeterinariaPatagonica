from django.db import models
from django.core.validators import RegexValidator
from VeterinariaPatagonica import tools
from django.db.models import Q
from VeterinariaPatagonica.tools import BajasLogicasQuerySet
from VeterinariaPatagonica.tools import VeterinariaPatagonicaQuerySet
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

RubroManager = models.Manager.from_queryset(RubroQueryset)

class Rubro (models.Model):
    """MAPPER = {
        "nombre": "nombre__icontains",
    }"""

    objects = RubroManager()

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
            'blank': "El nombre es obligatorio",
            'unique': "El Rubro ya existe"
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

    def __str__ (self):
        return "{0}, {1}".format(self.nombre,self.descripcion)

    class Meta:
        ordering = ["nombre"]