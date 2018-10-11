from django import forms
from .models import Cliente
#from localflavor.ar import forms as lforms #[BUG]Comento esta linea porque hace pinchar en mi compu. [Matias]

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente

        fields = [ 'dniCuit',
                   'nombres', 'apellidos', 'direccion', 'localidad', 'celular', 'telefono', 'email',
                   'tipoDeCliente',
                   'descuentoServicio', 'descuentoProducto', 'baja']

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
            #'localidad' : forms.ComboField(),
            'localidad': forms.TextInput(),
            'celular': forms.TextInput(),
            'telefono': forms.TextInput(),
            'email': forms.EmailInput(),
        }

    def clean_dniCuit(self):
        dato = self.data["nombres"]
        lforms.ARDNIField().clean(dato)
        lforms.ARCUITField().clean(dato)
        return dato

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
