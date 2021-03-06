from django import forms
from .models import FormaDePago

class FormaDePagoForm(forms.ModelForm):
    class Meta:
        model = FormaDePago
        fields = [
            'nombre',
            'descripcion',
        ]

        labels = {
            'nombre':'Nombre:',
            'descripcion' : 'Descripción:'
        }

        error_messages = {
            'nombre' : {
                'max_length': ("Nombre demasiado largo"),
            }
        }

        widgets = {
            'nombre' : forms.TextInput(),
            'descripcion': forms.Textarea(attrs={ 'cols':60, 'rows':4 })
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
