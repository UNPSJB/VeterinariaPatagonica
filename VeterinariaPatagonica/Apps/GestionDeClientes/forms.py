from django import forms
from .models import Cliente
from localflavor.ar import forms as lforms

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [ 'dniCuit',
                   'nombres', 'apellidos', 'direccion', 'localidad', 'celular', 'telefono', 'email',
                   'tipoDeCliente',
                   'descuentoServicio', 'descuentoProducto', 'baja']

    def clean_dniCuit(self):
        dato = self.data["nombres"]
        lforms.ARDNIField().clean(dato)
        lforms.ARCUITField().clean(dato)
        return dato

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data