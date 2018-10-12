from django import forms
from .models import Cliente
from django.core.validators import RegexValidator
<<<<<<< HEAD

#from localflavor.ar import forms as lforms

#from localflavor.ar import forms as lforms #Lo comento porque me pincha [Matias]
||||||| merged common ancestors
#from localflavor.ar import forms as lforms #Lo comento porque me pincha [Matias]
=======
from localflavor.ar import forms as lforms #Lo comento porque me pincha [Matias]
#Para que no pinche instalar -> pip install django-localflavor
>>>>>>> d90545785d9a73bf61911f6d81aaac5584a9eaa8


<<<<<<< HEAD

'''class creacionModelForm(forms.ModelForm):
    class meta:
        model = Cliente'''
||||||| merged common ancestors
'''class creacionModelForm(forms.ModelForm):
    class meta:
        model = Cliente'''
=======
>>>>>>> d90545785d9a73bf61911f6d81aaac5584a9eaa8

def ClienteFormFactory(cliente=None):
    campos = [ 'nombres', 'apellidos', 'direccion', 'localidad', 'celular', 'telefono', 'email',
        'tipoDeCliente',
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

    return ClienteForm