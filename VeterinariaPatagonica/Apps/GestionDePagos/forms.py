from django import forms
from .models import Pago

#def PagoFormFactory(pago=None, factura=None):
#return PagoForm

class PagoForm(forms.ModelForm):

    class Meta:
        model = Pago
        fields = {
            #'fecha',
            'importeTotal',
        }

        '''widget_importe = forms.TextInput(),
        if factura:
            widget_importe = forms.TextInput(attrs={'value': str(factura), 'disabled': 'disabled'})'''

        labels = {
            'fecha':'Fecha',
            'importeTotal' : 'Importe Total'
        }

        widgets = {
            #'fecha' : forms.TextInput(),
            'importeTotal': forms.TextInput()
        }

        field_order = [
            #'fecha',
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
