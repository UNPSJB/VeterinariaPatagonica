from django import forms
from django.apps import apps
from django.core.validators import RegexValidator
from .models import Mascota

TIMEINPUT_FMTS = [ "%H:%M" ]


'''class creacionModelForm(forms.ModelForm):
    class meta:
        model = Mascota'''

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota


        fields = [ 'patente',
                   'nombre',
                   #'fechaDeNacimiento',
                   'especie', 'raza',
                   'cliente'
                   ]

        labels = {
            'patente':'Patente',
            'nombre':'Nombre',
            #'fechaDeNacimiento' : 'FechaDeNacimiento',
            'raza':'Raza',
            'especie':'Especie',
            'baja':'Baja'
        }


        error_messages = {
            'nombre' : {
                'max_length': ("Nombres demasiados largos"),
            },



            'patente' : {
                #'max_length' : ("DNI/CUIT demasiado largo"),
                'unique' : ("Ese DNI/CUIT ya existe"),
            }
        }
        widgets = {
            'nombre' : forms.TextInput(),
            'raza' : forms.TextInput(),
            'especie': forms.TextInput(),

        }

    def clean_patente(self):
        dato = self.data["patente"]
        try:
            return lforms.ARDNIField().clean(dato)
        except forms.ValidationError:
            pass

        return lforms.ARCUITField().clean(dato)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
