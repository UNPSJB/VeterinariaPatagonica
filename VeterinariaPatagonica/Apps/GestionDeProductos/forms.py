from django import forms
from .models import Producto
from dal import autocomplete

from django.core.validators import RegexValidator

'''
class creacionModelForm(forms.ModelForm):
    class meta:
        model = Producto
'''

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
    campos = [ 'nombre', 'marca', 'stock', 'formaDePresentacion', 'precioPorUnidad', 'precioDeCompra', 'rubro', 'descripcion', ]

    if producto is  None:
        campos.insert(0, 'nombre') #0

    class ProductoForm(forms.ModelForm):

        class Meta:
            model = Producto
            fields = campos
            labels = {
                'nombre':'Nombre',
                'marca': 'Marca',
                'stock': 'Stock',
                'formaDePresentacion':'FormaDePresentacion',
                'precioPorUnidad':'PrecioPorUnidad',
                'precioDeCompra' : 'PrecioDeCompra',
                'rubro':'Rubro',
                'descripcion':'Descripcion',
                'baja':'Baja'
            }

            error_messages = {
                'nombre' : {
                    'max_length': ("Nombre demasiado largo"),
                    'unique': ("Ese nombre ya existe"),
                }
            }

            widgets = {
                'nombre' : forms.TextInput(),
                'formaDePresentacion' : forms.Select(choices=Producto.UNIDADES),
                'precioPorUnidad': forms.TextInput(),
                'precioDeCompra': forms.TextInput(),
                'rubro' : autocomplete.ModelSelect2(url='/GestionDeProductos/rubroAutocomplete'),
                #'rubro' : forms.Select(attrs={'class': 'form-control'}),
            }

        '''def clean_nombre(self):
            dato = self.data["nombre"]
            try:
                return forms.CharField().clean(dato)
            except forms.ValidationError:
                pass

            return forms.CharField().clean(dato)'''

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

