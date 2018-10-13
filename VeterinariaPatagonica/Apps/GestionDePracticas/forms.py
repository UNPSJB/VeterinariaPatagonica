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
<<<<<<< HEAD
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
                'cliente': forms.Select(choices=gcmodels.Cliente.objects.all()),
                'servicios' : forms.TextInput(),
                'insumosReales': forms.TextInput(),
                'tipoDeAtencion': forms.TextInput(),
            }
||||||| merged common ancestors
                'max_digits' : "Cantidad de digitos inválida."
            })
    #cliente.
    #servicios.
    #insumosReales.
    #tipoDeAtención.


    def __init__(self, *args, **kwargs):

        self.field_order = [
            'nombre',
            'formaDePresentacion',
            'precioPorUnidad',
            'rubro'
        ]


        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class' : 'form-control'
                })


    def crear(self):
        insumo = Insumo.objects.create(

            nombre = self.cleaned_data['nombre'],
            formaDePresentacion = self.cleaned_data['formaDePresentacion'],
            precioPorUnidad = self.cleaned_data['precioPorUnidad'],
            rubro = self.cleaned_data['rubro']
        )

        return insumo


class ModificacionForm(CreacionForm):

    baja = forms.BooleanField(
        required = False,
        label = 'Deshabilitado',
        widget = forms.CheckboxInput,
        help_text='Habilitar o deshabilitar el insumo',
        error_messages = {},
        validators = [],
    )

    def cargar(self, instancia):
=======
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
>>>>>>> bccb48685e40e04944099e326985ffd31d016bc4

        def clean(self):
            cleaned_data = super().clean()
            return cleaned_data

    return PracticaForm
