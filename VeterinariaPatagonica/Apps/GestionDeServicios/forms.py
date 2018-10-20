from django import forms
from .models import Servicio
from django.core.validators import RegexValidator

from Apps.GestionDeClientes import models as gcmodels



def ServicioFormFactory(servicio=None):

    class ServicioForm(forms.ModelForm):
        model = Servicio
        fields = [ 'tipo',
                    'nombre',
                    'descripcion',
                    'tiempoEstimado',
                    'precioManoDeObra',
                    'insumos',
                    ]
        labels = {
            'tipo':'Tipo.',
            'nombre':'Nombre.',
            'descripcion':'Descripcion.',
            'tiempoEstimado':'Tiempo Estimado.',
            'precioManoDeObra':'Precio Mano de Obra.',
            'insumos':'Insumos.',
            }
        error_messages = {
            'nombre' : {
                'max_length': ("Nombre demasiado largo"),
            },
            'precio' : {
                'min_value' : 'Debe ingresar un valor no menor que el 0%'
            },
        }
        widgets = {
            'tipo' : forms.TextInput(),
            'nombre' : forms.TextInput(),
            'descripcion': forms.Textarea(attrs={ 'cols':60, 'rows':6 }),
            'tiempoEstimado' : forms.NumberInput(),
            'precioManoDeObra': forms.NumberInput(),
            'insumos': forms.Select(attrs={'class':'form-control'}),
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

    return ServicioForm
