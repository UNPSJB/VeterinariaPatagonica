from django import forms
from .models import Servicio, ServicioProducto
from django.core.validators import RegexValidator
from Apps.GestionDeClientes import models as gcmodels

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = [  'tipo',
                    'nombre',
                    'descripcion',
                    'tiempoEstimado',
                    'precioManoDeObra',
                    ]
        labels = {
            'tipo':'Tipo:',
            'nombre':'Nombre:',
            'descripcion':'Descripción:',
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
            'precioManoDeObra': {
                'max_digits': "Debe ingresar a lo sumo %d digitos para la parte entera" % (Servicio.MAX_ENTERO),
                'max_whole_digits': "Debe ingresar a lo sumo %d digitos en total" % (Servicio.PRECIO),
            }
        }
        widgets = {
            'nombre' : forms.TextInput(),
            'descripcion': forms.Textarea(attrs={ 'cols':60, 'rows':4 }),
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
        labels = {
            'producto':'Insumo:',
            'cantidad':'Cantidad:',
            }

class ServicioProductoBaseFormSet(forms.BaseModelFormSet):
    def clean(self):

        ret = super().clean()
        #if not ret.lenght()>0:
        #    raise forms.ValidationError("Debe ingresar almenos un producto.")
        productos = [form.cleaned_data for form in self if form.cleaned_data]#Obtengo los productos puestos en el formulario (No toma las tuplas vacias).
        producto_ids = [d["producto"].pk for d in productos if not d["DELETE"]]#Obtengo los Ids de los productos que no estén marcados como "eliminados"(El Checkbox "eliminar").
        if len(producto_ids) != len(set(producto_ids)):#Verifico si hay productos repetidos.
            raise forms.ValidationError("Hay insumos repetidos.")


        return ret

    def save(self, commit=True):
        return super().save(commit=commit)
