from django.db import models


class Pago (models.Model):

    fecha = models.DateField(
        help_text="Fecha de pago",
        null=False,
        blank=False,
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


    baja = models.BooleanField(default=False)

    def __str__(self):
        return "{0}".format(self.fecha)
