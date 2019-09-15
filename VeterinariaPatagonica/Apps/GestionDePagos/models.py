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
        "baja" : "baja__icontains",
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

    class Meta:
        ordering = ["fecha",]
