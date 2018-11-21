from .models import Factura, DetalleFactura
from django import forms
from dal import autocomplete

def FacturaFormFactory(practica):
    class FacturaForm(forms.ModelForm):
        class Meta:
            model = Factura
            fields = {'tipo', 'cliente', 'fecha', 'practica', 'total'}

            labels = {
                'tipo': 'Tipo:',
                'cliente': 'Cliente:',
                'fecha': 'Fecha:',
                'practica': 'Práctica:',
                'total': 'Total:',
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
            'practica',
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
            'practica',
            'total'
        ]

        labels = {
            'tipo':'Tipo:',
            'cliente' : 'Cliente:',
            'fecha' : 'Fecha:',
            'practica': 'Práctica:',
            'total': 'Total:'
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
        ret = super().clean()
        productos = [form.cleaned_data for form in self if form.cleaned_data]#Obtengo los productos puestos en el formulario (No toma las tuplas vacias).
        producto_ids = [d["producto"].pk for d in productos if not d["DELETE"]]#Obtengo los Ids de los productos que no estén marcados como "eliminados"(El Checkbox "eliminar").
        if len(producto_ids) != len(set(producto_ids)):#Verifico si hay productos repetidos.
            raise forms.ValidationError("Hay productos repetidos.")
        return ret

    def save(self, commit=True):
        return super().save(commit=commit)
