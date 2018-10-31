from django import forms
from .models import Mascota

from django.core.validators import RegexValidator

#TIMEINPUT_FMTS = [ "%H:%M" ]


'''class creacionModelForm(forms.ModelForm):
    class meta:
        model = Mascota'''

cliente = forms.DateField(
    required=True,
    label='cliente',
    widget=forms.CharField,
    help_text='Cliente',
    error_messages={
        'invalid_choice': "La opcion no es valida",
        'required': "el cliente es obligatorio"
    },
    validators=[],

)
def MascotaFormFactory(mascota=None):
    campos = [ 'cliente',
               'fechaNacimiento',
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
                'fechaNacimiento': 'Fecha De Nacimiento',
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
                'fechaNacimiento': forms.DateInput(),
                'raza' : forms.TextInput(),
                'especie': forms.TextInput(),
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

    return MascotaForm
