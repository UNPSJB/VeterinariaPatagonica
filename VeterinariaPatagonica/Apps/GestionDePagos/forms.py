from django import forms
from .models import Pagos

class PagosForm(forms.ModelForm):
    class Meta:
        model = Pagos
        fields = {
            'fecha',
            'importeTotal',
        }

        labels = {
            'fecha':'Fecha',
            'importeTotal' : 'Importe Total'
        }

        widgets = {
            'fecha' : forms.TextInput(),
            'importeTotal': forms.TextInput()
        }

        field_order = [
            'fecha',
            'importeTotal',
        ]


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