from django import forms
from .models import Practica
from django.core.validators import RegexValidator
from Apps.GestionDeClientes import models as gcmodels

def PracticaFormFactory(practica=None):

    class PracticaForm(forms.ModelForm):
        class Meta:
            model = Practica
            fields = [ 'nombre',
                        'precio',
                        'cliente',
                        'servicios',
                        'insumosReales',
                        'tipoDeAtencion',
                        ]
            labels = {
                'nombre':'Nombre.',
                'precio':'Precio.',
                'cliente':'Cliente.',
                'servicios':'Servicios.',
                'insumosReales':'Insumos Reales.',
                'tipoDeAtencion':'Tipo De Atención.',
                }
            error_messages = {
                'nombres' : {
                    'max_length': ("Nombres demasiados largos"),
                },
                'precio' : {
                    'min_value' : 'Debe ingresar un valor no menor que el 0%'
                },
            }
            widgets = {
                'nombre' : forms.TextInput(),
                'precio' : forms.NumberInput(),
                'cliente': forms.Select(attrs={'class':'form-control'}),
                'servicios' : forms.Select(attrs={'class':'form-control'}),
                'insumosReales': forms.Select(attrs={'class':'form-control'}),
                'tipoDeAtencion': forms.Select(attrs={'class':'form-control'}),
            }

        def clean(self):
            cleaned_data = super().clean()
            return cleaned_data

    return PracticaForm
