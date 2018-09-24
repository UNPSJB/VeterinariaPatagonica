from django.db import models

# Create your models here.


#FALTAN LAS VALIDACIONES.

class Cliente (models.Model):
    DNI_CUIT = models.CharField(max_length = 14)
    nombres = models.CharField(max_length = 50)
    apellidos = models.CharField(max_length = 50)
    direccion = models.CharField(max_length = 50)
    localidad = models.CharField(max_length = 100)
    telefono = models.CharField(max_length = 30)
    email = models.EmailField(max_length=30)
    tipoDeCliente = models.CharField(max_length = 7)
    TIPODECLIENTE = (('E', 'Especial'), ('C', 'Comun'))
    tipoDeCliente = models.CharField(max_length=1, choices=TIPODECLIENTE, default='C')
    descuentoServicio = models.PositiveSmallIntegerField()
    descuentoProducto = models.PositiveSmallIntegerField()
    cuentaCorriente = models.DecimalField(max_digits = 6, decimal_places = 2)#Son 6 digitos porque tiene un limite de adeudamiento de $3.000,00.

    def __str__ (self):
        return "{0}, {1}".format(self.nombres,self.apellidos)


    
