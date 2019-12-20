from django.db import models


class Pago (models.Model):

    class Meta:
        ordering = ["fecha",]
        permissions = (
            ("pago_crear", "pago_crear"),
            ("pago_ver", "pago_ver"),
            ("pago_listar", "pago_listar"),
        )
        default_permissions = ()
        unique_together = (
            ("id", "factura"),
        )

    fecha = models.DateField(
        help_text="Fecha de pago",
        null=False,
        blank=False,
        auto_now_add=True,
        editable= False,
        error_messages={
            'blank':"La fecha es obligatoria"
        }
    )

    factura = models.OneToOneField(
        "GestionDeFacturas.Factura",
        on_delete = models.CASCADE,
        null = False,
        blank = False
    )
