from django import forms
from django.core.validators import MinValueValidator

from VeterinariaPatagonica.forms import BaseForm
from Apps.GestionDePracticas.models.practica import Practica
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


# from django import forms
# from .models import Pago

# #def PagoFormFactory(pago=None, factura=None):
# #return PagoForm

# class PagoForm(forms.ModelForm):

#     class Meta:
#         model = Pago
#         fields = {
#             #'fecha',
#             'importeTotal',
#         }

#         '''widget_importe = forms.TextInput(),
#         if factura:
#             widget_importe = forms.TextInput(attrs={'value': str(factura), 'disabled': 'disabled'})'''

#         labels = {
#             'fecha':'Fecha',
#             'importeTotal' : 'Importe Total'
#         }

#         widgets = {
#             #'fecha' : forms.TextInput(),
#             'importeTotal': forms.TextInput()
#         }

#         field_order = [
#             #'fecha',
#             'importeTotal',
#         ]


#     def clean(self):
#         cleaned_data = super().clean()
#         return cleaned_data

#     def __init__(self, *args, **kwargs):

#         super().__init__(*args, **kwargs)

#         # [TODO] Averiguar una mejor manera de hacer esto:
#         for field in self.fields.values():
#             if not isinstance(field.widget, forms.CheckboxInput):
#                 field.widget.attrs.update({
#                     'class': 'form-control'
#                 })
