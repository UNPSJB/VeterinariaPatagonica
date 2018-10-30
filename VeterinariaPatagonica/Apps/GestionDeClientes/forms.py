from django import forms
from .models import Cliente
#from localflavor.ar import forms as lforms

from django.core.validators import RegexValidator
#Para que no pinche instalar -> pip install django-localflavor

class creacionModelForm(forms.ModelForm):
    class meta:
        model = Cliente


def ClienteFormFactory(cliente=None):
    campos = [
                'tipoDeCliente',
                'nombres',
               'apellidos',
               'direccion',
               'localidad',
               'celular',
               'telefono',
               'email',

                'descuentoServicio', 'descuentoProducto', 'cuentaCorriente']

    if cliente is  None:
        campos.insert(1, 'dniCuit')

    class ClienteForm(forms.ModelForm):
        class Meta:
            model = Cliente
            fields = campos
            labels = {
                'dniCuit':'Dni/Cuit',
                'nombres':'Nombres', 'apellidos':'Apellidos', 'direccion':'Direccion', 'localidad':'Localidad', 'celular':'Celular', 'telefono':'Telefono', 'email':'Email',
                'tipoDeCliente':'Tipo De Cliente',
                'descuentoServicio':'DescuentoServicio', 'descuentoProducto':'DescuentoProducto', 'baja':'Baja'
            }

            error_messages = {
                'nombres' : {
                    'max_length': ("Nombres demasiados largos"),
                },

                'apellidos' : {
                    'max_length' : ("Apellidos demasiados largos"),
                },

                'dniCuit' : {
                    'max_length' : ("DNI/CUIT demasiado largo"),
                    'unique' : ("Ese DNI/CUIT ya existe"),
                }
            }

            widgets = {
                'localidad' : forms.Select(choices=Cliente.LOCALIDADES),
                'descuentoServicio': forms.NumberInput(attrs={'data-tipo': 'especial', 'default': '0'}),
                'descuentoProducto': forms.NumberInput(attrs={'data-tipo': 'especial', 'default': '0'}),
                'cuentaCorriente': forms.NumberInput(attrs={'data-tipo': 'especial', 'default': '0.0'})
            }

        def clean_dniCuit(self):
            dato = self.data["dniCuit"]
            try:
                return lforms.ARDNIField().clean(dato)
            except forms.ValidationError:
                pass

            return lforms.ARCUITField().clean(dato)

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

    return ClienteForm
