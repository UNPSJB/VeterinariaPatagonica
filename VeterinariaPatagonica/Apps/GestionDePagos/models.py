from django.db import models
from Apps.GestionDeFacturas import models as facModel
from VeterinariaPatagonica import tools
from django.db.models import Q

#Esta clase se comunica con la BD
class BasePagoManager(models.Manager):
    pass

PagoManager = BasePagoManager.from_queryset(tools.BajasLogicasQuerySet)

class Pago (models.Model):

    MAPPER = {
        "fecha": "fecha__icontains",
        "tipoFactura": lambda value: Q(factura__tipo__icontains=value),
        "cliente": lambda value: Q(factura__cliente__nombres__icontains=value) | Q(factura__cliente__apellidos__icontains=value),
        "importeTotal": "importeTotal__icontains",
    }

    fecha = models.DateField(
        help_text="Fecha de pago",
        null=False,
        blank=False,
        auto_now=True,
        editable= True,
        error_messages={
            'blank':"La fecha es obligatoria"
        }
    )

    importeTotal = models.IntegerField(
        null=False,
        blank=False,
        error_messages={
            'blank':"El importe es obligatorio"
        }
    )

    factura = models.OneToOneField(
        facModel.Factura,
        on_delete = models.CASCADE,
        null = True,
        blank = True
    )



    baja = models.BooleanField(default=False)

    objects = PagoManager()

    def __str__(self):
        #return "%s La factura%" % self.factura.tipo
        return "{0}".format(self.importeTotal)

'''
In [1]: from Apps.GestionDeFacturas.models import Factura

In [2]: from Apps.GestionDePagos.models import Pago

In [3]: from django.utils import timezone

In [4]: f1 = Factura.objects.get(pk=1)

In [5]: print(f1)
Tipo de Factura: C, Cliente: Juan Carlos, Trinidad Ferrer Total: 1200.

In [6]: p1 = Pago.objects.create(fecha= timezone.now(), importeTotal= 1200, factura=f1)
In [7]:  f1 = Factura.objects.get(pk=2)

In [8]: print(f1)
Tipo de Factura: C, Cliente: Jonathan, Bueno Total: 2400.

In [9]:  p1 = Pago.objects.create(fecha= timezone.now(), importeTotal= 1200, factura=f1)

In [10]: p1.factura
Out[10]: <Factura: Tipo de Factura: C, Cliente: Jonathan, Bueno Total: 2400.>

In [11]: f1.pago
Out[11]: <Pago: 1200>

In [12]: print(p1)'''