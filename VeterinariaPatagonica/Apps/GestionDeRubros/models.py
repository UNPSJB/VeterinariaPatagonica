from django.db import models
from django.core.validators import RegexValidator

# Create your models here.

class Rubro (models.Model):

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
