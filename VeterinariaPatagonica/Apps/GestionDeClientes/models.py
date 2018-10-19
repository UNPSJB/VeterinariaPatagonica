from django.db import models
from django.core.validators import RegexValidator

# Create your models here.

class Cliente (models.Model):

    REGEX_NOMBRE = '^[0-9a-zA-Z-_ .]{3,100}$'
    REGEX_NUMERO = '^[0-9]{1,12}$'
    MAXDNICUIT = 14
    MAXNOMBRE = 50
    MAXAPELLIDO = 50
    MAXLOCALIDAD = 60
    MAXDIRECCION = 100
    MAXCELULAR = 12
    MAXTELEFONO = 7
    TIPODECLIENTE = (('C', 'Comun'), ('E', 'Especial'))
    LOCALIDADES = [
        ("Trelew", "Trelew"),
        ("Rawson", "Rawson"),
        ("Madryn", "Madryn"),
        ("Gaiman", "Gaiman"),
        ("Dovalon", "Dovalon")
    ]

    dniCuit = models.CharField(
        help_text= "Dni/Cuit del Cliente",
        max_length = MAXDNICUIT,
        unique= True,
        null= False,
        blank= False,
        error_messages= {
            'max_length': "El dni/cuit puede tener a lo sumo {} caracteres".format(MAXDNICUIT),
            'unique': "Otro cliente tiene ese dni/cuit",
            'blank': "El dni/cuit es obligatorio"
        }
    )

    nombres = models.CharField(
        help_text= "Nombre del Cliente",
        max_length = MAXNOMBRE,
        unique= False,
        null= False,
        blank= False,
        primary_key= False,
        validators= [RegexValidator(regex=REGEX_NOMBRE)],
        error_messages= {
            'max_length': "El nombre puede tener a lo sumo {} caracteres".format(MAXNOMBRE),
            'blank': "El nombre es obligatorio"
        }
    )

    apellidos = models.CharField(
        help_text= "Apellido del Cliente",
        max_length = MAXAPELLIDO,
        unique= False,
        null= True,
        blank= True,
        primary_key= False,
        validators= [RegexValidator(regex=REGEX_NOMBRE)],
        error_messages= {
            'max_length': "El apellido puede tener a lo sumo {} caracteres".format(MAXAPELLIDO),
        }
    )

    direccion = models.CharField(
        help_text="Direccion del Cliente",
        max_length=MAXDIRECCION,
        unique=False,
        null=False,
        blank=False,
        primary_key=False,
        error_messages={
            'max_length': "El direccion puede tener a lo sumo {} caracteres".format(MAXDIRECCION),
        }
    )

    localidad = models.CharField(
        help_text="Localidad del Cliente",
        max_length=MAXLOCALIDAD,
        unique=False,
        null=False,
        blank=False,
        primary_key=False,
        error_messages={
            'max_length': "La localidad puede tener a lo sumo {} caracteres".format(MAXLOCALIDAD),
        }
    )
    celular = models.CharField(
        help_text="Celular del Cliente sin el 0",
        max_length=MAXCELULAR,
        unique=True,
        null=True,
        blank=True,
        primary_key=False,
        validators=[RegexValidator(regex=REGEX_NUMERO)],
        error_messages={
            'max_length': "El celular puede tener a lo sumo {} caracteres".format(MAXCELULAR),
            'unique': "Otro cliente tiene ese celular",
        }
    )

    telefono = models.CharField(
        help_text="Telefono del Cliente",
        max_length=MAXTELEFONO,
        unique=False,
        null=True,
        blank=True,
        primary_key=False,
        validators=[RegexValidator(regex=REGEX_NUMERO)],
        error_messages={
            'max_length': "El telefono puede tener a lo sumo {} caracteres".format(MAXTELEFONO),
        }
    )

    email = models.EmailField(
        help_text="Email del Cliente",
        unique=True,
        null=True,
        blank=True,
        primary_key=False,
        error_messages={
            'unique': "Otro cliente tiene ese email",
        }
    )

    tipoDeCliente = models.CharField(
        max_length=1,
        choices=TIPODECLIENTE,
        default='C',
        unique=False,
        null=False,
        blank=False,
        error_messages={
            'blank': "El tipo de cliente es obligatorio"
        }
    )

    descuentoServicio = models.PositiveSmallIntegerField(blank=True, default=0)
    descuentoProducto = models.PositiveSmallIntegerField(blank=True, default=0)

    cuentaCorriente = models.DecimalField(
        max_digits = 6, #Son 6 digitos porque tiene un limite de adeudamiento de $3.000,00.
        decimal_places = 2,
        default=0.0,
        blank=True
    )

    baja = models.BooleanField(default=False)

    def __str__ (self):
        return "{0}, {1}".format(self.nombres,self.apellidos)


    
