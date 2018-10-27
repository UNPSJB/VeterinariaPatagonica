from django.db import models
#from django.apps import apps
#from datetime import date, timedelta, time, datetime
from django.core.validators import RegexValidator #MinValueValidator, #MaxValueValidator
from Apps.GestionDeRubros import models as grmodels
# Create your models here.

class Producto (models.Model):

    MAX_NOMBRE = 50
    REGEX_NOMBRE = '^[0-9a-zA-Z-_ .]{3,100}$'
    REGEX_NUMERO = '^[0-9]{1,12}$'
    MAX_DIGITOS = 7
    MAX_DECIMALES = 2
    MAXDESCRIPCION= 150



    NONE = 0
    GRAMO = 1
    CM3 = 2
    UNIDAD = 3
    KG = 4
    LITRO = 5
    DOCENA = 6
    TUPLAS = [(GRAMO,KG),
              (CM3,LITRO),
              (UNIDAD, DOCENA)]

    UNIDADES_BASICAS = (
        (GRAMO, "g"),
        (CM3, "cm3"),
        (UNIDAD, "unidad")
    )

    UNIDADES_DERIVADAS = (
        (KG, "kg"),
        (LITRO, "litro"),
        (DOCENA, "docena")
    )

    UNIDADES = UNIDADES_BASICAS + UNIDADES_DERIVADAS
    UNIDADES_DICT = dict(UNIDADES)

    CONVERT = {
        NONE: lambda cantidad: cantidad,
        GRAMO: lambda cantidad: cantidad,
        CM3: lambda cantidad: cantidad,
        UNIDAD: lambda cantidad: cantidad,
        KG: lambda cantidad: cantidad / 1000,
        LITRO: lambda cantidad: cantidad / 1000,
        DOCENA: lambda cantidad: cantidad / 12
    }

    FORMAT = {
        GRAMO: lambda cantidad: "%s.%s kg" % (cantidad // 1000, cantidad % 1000),
        CM3: lambda cantidad: "%s.%s litros" % (cantidad // 1000, cantidad % 1000),
        UNIDAD: lambda cantidad: "%s docenas y %s unidades" % (cantidad // 12, cantidad % 12)
    }

    id = models.AutoField(
        primary_key=True,
        unique=True,
        editable=False
    )

    nombre = models.CharField(
        help_text="Nombre del Producto",
        max_length = MAX_NOMBRE,
        unique = False,
        null = False,
        blank = False,
        validators = [RegexValidator(regex=REGEX_NOMBRE)],
        error_messages = {
            'max_length' : "El nombre puede tener a lo sumo {} caracteres".format(MAX_NOMBRE),
            'blank' : "El nombre es obligatorio"
            })

    marca = models.CharField(
        help_text="Marca del Producto",
        max_length = MAX_NOMBRE,
        unique = False,
        null = False,
        blank = False,
        validators = [RegexValidator(regex=REGEX_NOMBRE)],
        error_messages = {
            'max_length' : "La marca puede tener a lo sumo {} caracteres".format(MAX_NOMBRE),
            'blank' : "La marca es obligatoria"
            })

    stock = models.IntegerField(
        help_text="Stock del Producto",
        #max_digits = MAX_DIGITOS,
        #unique = False,
        #null = True,
        #blank = True,
        #validators = [RegexValidator(regex=REGEX_NUMERO)],
        #error_messages = {
            #'max_digits' : "El stock puede tener a lo sumo {} digitos".format(MAX_DIGITOS),
         #   }
    )

    formaDePresentacion = models.PositiveSmallIntegerField(
        help_text="Forma de Presentacion del Producto",
        choices=UNIDADES,
        unique=False,
        null=False,
        blank=False,
        error_messages = {
            'invalid_choice' : "Opcion invalida",
            'blank' : "La unidad de medida es obligatoria"
        })

    precioPorUnidad = models.DecimalField(
        help_text="Precio del Producto",
        max_digits = MAX_DIGITOS,
        decimal_places = MAX_DECIMALES)

    precioDeCompra = models.DecimalField(
        help_text="Precio de Compra del Producto",
        max_digits = MAX_DIGITOS,
        unique=False,
        null=False,
        blank=False,
        decimal_places = MAX_DECIMALES)


    rubro = models.ForeignKey(
        grmodels.Rubro,
        help_text="Nombre del rubro al que pertenece",
        unique=False,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        max_length = MAX_NOMBRE,
        error_messages={
            'blank': "El rubro es obligatorio"
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
            'max_length': "La descripcion puede tener a lo sumo {} caracteres".format(MAXDESCRIPCION),
        }
    )

    baja = models.BooleanField(
        #help_text='Deshabilitado',
        default=False
        )



    def __str__(self):
        fp = self.formaDePresentacion
        unidad = list(filter(lambda t: fp in t, Producto.TUPLAS)).pop()
        return "Producto: {0} Unidad: {1} Precio: {2}".format(self.nombre, Producto.UNIDADES_DICT[unidad[0]], self.precioPorUnidad)

    def precioEnUnidad(self, cantidad):
        return Producto.CONVERT[self.formaDePresentacion](self.precioPorUnidad) * cantidad
