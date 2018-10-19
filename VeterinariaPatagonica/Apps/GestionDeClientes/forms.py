from django import forms
from .models import Cliente

from django.core.validators import RegexValidator


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
        campos.insert(0, 'dniCuit')

    class ClienteForm(forms.ModelForm):
        class Meta:
            model = Cliente
            fields = campos
            labels = {
                'dniCuit':'DniCuit',
                'nombres':'Nombres', 'apellidos':'Apellidos', 'direccion':'Direccion', 'localidad':'Localidad', 'celular':'Celular', 'telefono':'Telefono', 'email':'Email',
                'tipoDeCliente':'TipoDeCliente',
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
                'nombres' : forms.TextInput(),
                'apellidos' : forms.TextInput(),
                'direccion': forms.TextInput(),
                'localidad' : forms.Select(choices=Cliente.LOCALIDADES),
                #'localidad': forms.TextInput(),
                'celular': forms.TextInput(),
                'telefono': forms.TextInput(),
                'email': forms.EmailInput(),
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
