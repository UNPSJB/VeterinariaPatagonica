from django.db import models

# Create your models here.
class Practica(models.Model):
    MAX_NOMBRE = 100
    MAX_DIGITOS = 8
    MAX_DECIMALES = 2
    nombre = models.CharField(
            max_length = MAX_NOMBRE,
            unique = True,
            null = False,
            blank = False,
            error_messages = {
                'unique' : "Otra práctica tiene ese nombre.",
                'max_length' : "El nombre puede tener a lo sumo {} caracteres.".format(MAX_NOMBRE),
                'blank' : "El nombre es obligatorio."
                })

    precio = models.DecimalField(
            max_digits = MAX_DIGITOS,
            decimal_places = MAX_DECIMALES
            error_messages = {
                'max_digits': "Cantidad de digitos ingresados supera el máximo."
            }
            )


#    estado = Estado




class Estado(models.Model):
    TIPO = 0
    TIPOS = [
            (0, 'estado')
            ]
    
