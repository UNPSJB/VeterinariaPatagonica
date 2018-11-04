from .models import Factura, DetalleFactura
from django import forms
from dal import autocomplete

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = {
            'tipo',
            'cliente',
            'fecha',
            'total'
        }

        labels = {
            'tipo':'Tipo',
            'cliente' : 'Cliente',
            'fecha' : 'Fecha',
            'total' : 'Total'
        }

        error_messages = {
            'tipo' : {
                'max_length': ("Nombre demasiados largo"),
            }
        }

        widgets = {
            'cliente': autocomplete.ModelSelect2(url='/GestionDeFacturas/clienteAutocomplete'),
        }

        field_order=[
            'tipo',
            'cliente',
            'fecha',
            'total',
        ]


    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # [TODO] Averiguar una mejor manera de hacer esto:
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'form-control'
                })

class DetalleFacturaForm(forms.ModelForm):
    class Meta:
        model = DetalleFactura
        fields= {
            'factura': 'Factura',
            'subtotal': 'Subtotal',
            'cantidad': 'Cantidad'
        }