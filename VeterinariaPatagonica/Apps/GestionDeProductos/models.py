from django.db import models

from django.apps import apps
from datetime import date, timedelta, time, datetime
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
# Create your models here.

class Producto (models.Model):

    MAX_NOMBRE = 50
    REGEX_NOMBRE = '^[0-9a-zA-Z-_ .]{3,100}$'
    MAX_DIGITOS = 7
    MAX_DECIMALES = 2



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
        unique = True,
        null = False,
        blank = False,
        validators = [RegexValidator(regex=REGEX_NOMBRE)],
        error_messages = {
            'unique' : "Otro Producto tiene ese nombre",
            'max_length' : "El nombre puede tener a lo sumo {} caracteres".format(MAX_NOMBRE),
            'blank' : "El nombre es obligatorio"
            })

    formaDePresentacion = models.PositiveSmallIntegerField(
        help_text="Forma de Presentacion del Producto",
        choices=UNIDADES,
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
        decimal_places = MAX_DECIMALES)

    #Cambiar cuando tengamos la clase Rubro.
    rubro = models.CharField(
        help_text="Nombre del rubro al que pertenece",
        max_length = MAX_NOMBRE,
        blank = False
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
