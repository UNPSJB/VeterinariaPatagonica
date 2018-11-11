from django import forms
from .models import Producto
from dal import autocomplete


rubro = forms.DateField(
    required=True,
    label='rubro',
    widget=forms.CharField,
    help_text='Rubro',
    error_messages={
        'invalid_choice': "La opcion no es valida",
        'required': "el rubro es obligatorio"
    },
    validators=[],

)

def ProductoFormFactory(producto=None):
    campos = [ 'marca', 'descripcion',
               'formaDePresentacion', 'stock',
               'precioDeCompra', 'precioPorUnidad',
               'rubro' ]

    if producto is  None:
        campos.insert(0, 'nombre')

    class ProductoForm(forms.ModelForm):

        class Meta:
            model = Producto
            fields = campos
            labels = {
                'nombre':'Nombre:',
                'marca': 'Marca:',
                'stock': 'Stock:',
                'formaDePresentacion':'Forma de Presentación:',
                'precioPorUnidad':'Precio por Unidad:',
                'precioDeCompra' : 'Precio de Compra:',
                'rubro':'Rubro:',
                'descripcion':'Descripción:',
                'baja':'Baja:'
            }

            error_messages = {
                'nombre' : {
                    'max_length': ("Nombre demasiado largo"),
                    'unique': ("Ese nombre ya existe"),
                }
            }

            widgets = {
                #'nombre' : forms.TextInput(),
                'descripcion': forms.Textarea(attrs={'cols': 60, 'rows': 4}),
                'formaDePresentacion' : forms.Select(),
                'precioPorUnidad': forms.NumberInput(),
                'precioDeCompra': forms.NumberInput(),
                'rubro' : autocomplete.ModelSelect2(url='/GestionDeProductos/rubroAutocomplete'),
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

    return ProductoForm
