from django.db import models
from Apps.GestionDeProductos import models as proModel
from Apps.GestionDeClientes import  models as cliModel

# Create your models here.

class Factura(models.Model):
    tipo = models.CharField(max_length=40, blank=True)
    cliente = models.ForeignKey(cliModel.Cliente, on_delete=models.CASCADE)
    fecha = models.DateField(null=True)
    total = models.IntegerField(null=True, blank=True)

    baja = models.BooleanField(default=False)

    def  __unicode__(self):
        return self.total

class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    producto = models.ForeignKey(proModel.Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.IntegerField()

    def  __unicode__(self):
        return self.subtotal

