from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, DecimalValidator
from VeterinariaPatagonica import tools
from decimal import Decimal
from django.db.models import Q
from VeterinariaPatagonica.tools import VeterinariaPatagonicaQuerySet

# Create your models here.

#Esta clase se comunica con la BD
class ClienteBaseManager(models.Manager):
    def __init__(self, tipo=None):
        super().__init__()
        self.tipo = tipo

    def get_queryset(self):
        qs = super().get_queryset()
        if self.tipo is not None:
            qs = qs.filter(tipo=self.tipo)
        return qs

class ClienteQueryset(VeterinariaPatagonicaQuerySet):

    MAPEO_ORDEN = {
        "orden_dniCuit" : ["dniCuit"],
        "orden_apellidos" : ["apellidos"],
        "orden_nombres" : ["nombres"],
        "orden_direccion" : ["direccion"],
        "orden_localidad" : ["localidad"],
        "orden_tipoDeCliente" : ["tipoDeCliente"],
    }

ClienteManager = ClienteBaseManager.from_queryset(ClienteQueryset)



class Cliente (models.Model):

    MAPPER = {
        "dniCuit": "dniCuit__icontains",
        "nombres": "nombres__icontains",
        "apellidos": "apellidos__icontains",
        "mascotas": lambda value: Q(mascota__nombre__icontains=value),
    }

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


    PARTE_ENTERA = 3
    PARTE_DECIMAL = 2
    DESC_MIN = Decimal(0)
    DESC_MAX = Decimal(100.00)
    DEFAULT = Decimal(0)
    DESCUENTO = PARTE_ENTERA + PARTE_DECIMAL


    CC_MIN_PRECIO = Decimal(0)
    CC_MAX_PRECIO = Decimal(3000.00)
    PRECIO = PARTE_ENTERA + PARTE_DECIMAL

    
    CC_PARTE_ENTERA = 4
    CC_MIN_PRECIO = Decimal(0)
    CC_MAX_PRECIO = Decimal(3000.00)
    PRECIO = CC_PARTE_ENTERA + PARTE_DECIMAL

    
    DESC_PARTE_ENTERA = 3
    PARTE_DECIMAL = 2
    DESC_MIN = Decimal(0)
    DESC_MAX = Decimal(100.00)
    DEFAULT = Decimal(0)
    DESCUENTO = DESC_PARTE_ENTERA + PARTE_DECIMAL

    dniCuit = models.CharField(
        help_text= "Dni/Cuit del Cliente",
        max_length = MAXDNICUIT,
        unique= True,
        null= False,
        blank= False,
        error_messages= {
            'max_length': "El dni/cuit puede tener a lo sumo {} caracteres".format(MAXDNICUIT),
            'unique': "El dni/cuit ingresado ya existe",
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

    descuentoServicio = models.DecimalField(
        max_digits= DESCUENTO,
        decimal_places= PARTE_DECIMAL,
        default= DEFAULT,
        blank=True,
        validators= [
            MinValueValidator(DESC_MIN, message=("El descuento no puede ser menor a {:.%df}" % (PARTE_DECIMAL)).format(DESC_MIN)),
            MaxValueValidator(DESC_MAX, message=("El descuento no puede ser mayor a {:.%df}" % (PARTE_DECIMAL)).format(DESC_MAX)),
        ]
    )

    descuentoProducto = models.DecimalField(
        max_digits=DESCUENTO,
        decimal_places=PARTE_DECIMAL,
        default=DEFAULT,
        blank=True,
        validators=[
            MinValueValidator(DESC_MIN, message=("El descuento no puede ser menor a {:.%df}" % (PARTE_DECIMAL)).format(DESC_MIN)),
            MaxValueValidator(DESC_MAX, message=("El descuento no puede ser mayor a {:.%df}" % (PARTE_DECIMAL)).format(DESC_MAX)),
        ]
    )

    cuentaCorriente = models.DecimalField(
        max_digits = PRECIO,
        decimal_places = PARTE_DECIMAL,
        default=DEFAULT,
        blank=True,
        validators = [
            MinValueValidator(CC_MIN_PRECIO, message=("El precio no debe ser menor a ${:.%df}" % (PARTE_DECIMAL)).format(CC_MIN_PRECIO)),
            MaxValueValidator(CC_MAX_PRECIO, message=("El precio no puede ser mayor a ${:.%df}" % (PARTE_DECIMAL)).format(CC_MAX_PRECIO)),
        ]
    )

    baja = models.BooleanField(default=False)

    objects = ClienteManager()

    def __str__ (self):
        return "{0}, {1}".format(self.nombres,self.apellidos)

    class Meta:
        ordering = ["apellidos", "nombres"]
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
