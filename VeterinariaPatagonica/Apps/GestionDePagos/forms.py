from django import forms

from VeterinariaPatagonica.forms import BaseForm
from Apps.GestionDeFacturas.models import Factura


class PagoForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FiltradoPagoForm(BaseForm):

    tipo_factura = forms.ChoiceField(
        required=False,
        choices=[(None, "Cualquiera")] + list(Factura.TIPODEFACTURA),
        widget=forms.Select(
            attrs={"class":"form-control"},
        )
    )

    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder" : "Cliente"}
        )
    )

    fecha_desde = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder" : "Fecha desde"}
        ),
        error_messages={
            "invalid" : "Fecha desde debe tener el formato <dia>/<mes>/<año>",
        },
    )

    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder" : "Fecha hasta"}
        ),
        error_messages={
            "invalid" : "Fecha hasta debe tener el formato <dia>/<mes>/<año>",
        },
    )

    importe_desde = forms.DecimalField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder" : "Importe desde"}
        )
    )

    importe_hasta = forms.DecimalField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder" : "Importe hasta"}
        )
    )

    def filtros(self):
        return self.datosCumplen(bool)
