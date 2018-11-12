from .models import Factura, DetalleFactura
from django import forms
from dal import autocomplete

def FacturaFormFactory(practica):
    class FacturaForm(forms.ModelForm):
        class Meta:
            model = Factura
            fields = {'tipo', 'cliente', 'fecha', 'total'}

            labels = {
                'tipo': 'Tipo',
                'cliente': 'Cliente',
                'fecha': 'Fecha',
                'total': 'Total'
            }

            error_messages = {
                'tipo': {
                    'max_length': ("Nombre demasiado largo"),
                }
            }

            widgets = {

                'cliente': autocomplete.ModelSelect2(url='/GestionDeFacturas/clienteAutocomplete'),
                'total': Factura.precioTotal(Factura),

            }

            print(Factura.precioTotal(Factura)),

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

        field_order = [
            'tipo',
            'cliente',
            'fecha',
            'total',
        ]
    return FacturaForm

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = [
            'tipo',
            'cliente',
            'fecha',
            'total'
        ]

        labels = {
            'tipo':'Tipo',
            'cliente' : 'Cliente',
            'fecha' : 'Fecha',
            'total': "Total"
        }

        error_messages = {
            'tipo' : {
                'max_length': ("Nombre demasiado largo"),
            }
        }

        widgets = {
            'cliente': autocomplete.ModelSelect2(url='/GestionDeFacturas/clienteAutocomplete'),
            #'total': Factura.calcular_subtotales(Factura, DetalleFactura)
        }

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

    field_order=[
            'tipo',
            'cliente',
            'fecha',
    ]

class DetalleFacturaForm(forms.ModelForm):
    class Meta:
        model = DetalleFactura
        fields= [
            #'factura',
            'producto',
            'cantidad',
            #'subtotal',
        ]

        widgets = {
            'producto': autocomplete.ModelSelect2(url='/GestionDeFacturas/productoAutocomplete'),

        }
        #widgets = {
        #    'subtotal' : forms.NumberInput(attrs={'disabled': '', 'value': 0.0}),
        #}

class DetalleFacturaBaseFormSet(forms.BaseModelFormSet):

    def clean(self):
        #import ipdb; ipdb.set_trace()
        producto= [item["producto"].id for item in self.cleaned_data]
        if len(producto) != len(set(producto)):
            raise forms.ValidationError("Hay productos repetidos.")
        return super().clean()

    def save(self, commit=True):
        return super().save(commit=commit)
