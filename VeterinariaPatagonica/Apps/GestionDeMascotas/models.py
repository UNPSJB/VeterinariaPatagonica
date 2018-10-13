from django.db import models
from django.core.validators import RegexValidator


from Apps.GestionDeClientes import models as gcmodels

# Create your models here.

class Mascota(models.Model):
    REGEX_NOMBRE = '^[0-9a-zA-Z-_ .]{3,100}$'
    REGEX_ESPECIE = '^[0-9a-zA-Z-_ .]{3,100}$'
    REGEX_RAZA= '^[0-9a-zA-Z-_ .]{3,100}$'
    MAX_NOMBRE = 50
    MIN_NOMBRE= 3;
    MAXRAZA = 50
    MAXESPECIE =50

    patente = models.CharField(max_length=20, unique=True)



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

    cliente = models.ForeignKey(gcmodels.Cliente, null=False, blank=False, on_delete=models.CASCADE)

    fechaNacimiento = models.DateTimeField(),

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
            'blank': "La especie es obligatorio"})

