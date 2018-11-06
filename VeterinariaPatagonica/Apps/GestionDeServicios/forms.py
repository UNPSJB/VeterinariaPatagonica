from django import forms
from .models import Servicio, ServicioProducto
from django.core.validators import RegexValidator
from Apps.GestionDeClientes import models as gcmodels

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = [ 'tipo',
                    'nombre',
                    'descripcion',
                    'tiempoEstimado',
                    'precioManoDeObra',
                    ]
        labels = {
            'tipo':'Tipo:',
            'nombre':'Nombre:',
            'descripcion':'Descripcion:',
            'tiempoEstimado':'Tiempo Estimado:',
            'precioManoDeObra':'Precio Mano de Obra:',
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

            'nombre' : forms.TextInput(),
            'descripcion': forms.Textarea(attrs={ 'cols':60, 'rows':6 }),
            'tiempoEstimado' : forms.NumberInput(),
            'precioManoDeObra': forms.NumberInput(),
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

class ServicioProductoForm(forms.ModelForm):
    class Meta:
        model = ServicioProducto
        fields = ["producto", "cantidad"]


class ServicioProductoBaseFormSet(forms.BaseModelFormSet):
    def clean(self):
        #import ipdb; ipdb.set_trace()
        
        producto_ids = [item["producto"].id for item in self.cleaned_data]

        if len(producto_ids) != len(set(producto_ids)):
            raise forms.ValidationError("Hay productos repetidos.")
        return super().clean()

    def save(self, commit=True):
        return super().save(commit=commit)
