from django import forms
from .models import Rubro

def RubroFormFactory(rubro=None):
    campos = ['nombre',
              'descripcion',
    ]

    class RubroForm(forms.ModelForm):
        class Meta:
            model = Rubro
            fields = campos
            labels = {
                'nombres':'Nombres',
                'descripcion' : 'Descripcion'
            }

            error_messages = {
                'nombres' : {
                    'max_length': ("Nombres demasiados largo"),
                }
            }

            widgets = {
                'descripcion': forms.Textarea(attrs={ 'cols':60, 'rows':6 })
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

    return RubroForm
