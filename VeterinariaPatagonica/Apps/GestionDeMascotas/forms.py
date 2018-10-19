from django import forms
from .models import Mascota

from django.core.validators import RegexValidator

#from localflavor.ar import forms as lforms

from localflavor.ar import forms as lforms


#TIMEINPUT_FMTS = [ "%H:%M" ]


'''class creacionModelForm(forms.ModelForm):
    class meta:
        model = Mascota'''

cliente = forms.ChoiceField(
    required=True,
    label='cliente',
    widget=forms.Select,
    help_text='Cliente',
    error_messages={
        'invalid_choice': "La opcion no es valida",
        'required': "el cliente es obligatorio"
    },
    validators=[],
    #choices=apps.get_model('GestionDeClientes', 'cliente', require_ready=False).TIPO,
)
def MascotaFormFactory(mascota=None):
    campos = [ 'cliente',
               #'fechaNacimiento',
               'nombre',
               'raza',
               'especie',
               ]
    if mascota is  None:
        campos.insert(0, 'patente')


    class MascotaForm(forms.ModelForm):
        class Meta:
            model = Mascota
            fields = campos
            labels = {
                'patente':'Patente',
                'cliente': "Cliente",
                'fechaNacimiento': 'FechaNacimiento',
                'nombre':'Nombre',
                'especie':'Especie',
                'raza': 'Raza',
                'baja':'Baja'
            }
            error_messages = {
                'nombre' : {
                    'max_length': ("Nombre demasiados largos"),
                },
                'patente' : {
                    'max_length' : ("patente demasiado largo"),
                    'unique' : ("Esa patente ya existe"),
                }
            }
            widgets = {
                'nombre' : forms.TextInput(),
                'cliente': forms.Select(attrs={'class': 'form-control'}),
                'fechaNacimiento': forms.DateTimeField,
                'raza' : forms.TextInput(),
                'especie': forms.TextInput(),
            }

        def clean(self):
            cleaned_data = super().clean()
            return cleaned_data
    return MascotaForm