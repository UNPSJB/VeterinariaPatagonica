from django import forms
from .models import Rubro

def RubroFormFactory(rubro=None):
    campos = [ 'nombre', 'descripcion']

    if rubro is None:
        campos.insert(0, 'nombre')

    class RubroForm(forms.ModelForm):
        class Meta:
            model = Rubro
            fields = campos
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
    
    return RubroForm

class FiltradoForm(forms.Form):

    ordenes = (
        ("d", "Descendente"),
        ("a", "Ascendente"),
    )

    criterios = (
        ("nombre", "Nombre"),
        ("descripcion", "Descripcion")
    )

    nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder":"Nombre...",
            "class":"form-control"
        })
    )

    descripcion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder":"Descripcion...",
            "class":"form-control",
        })
    )

    segun = forms.ChoiceField(
        label="Ordenar segun",
        choices=criterios,
        required=False,
        widget=forms.Select(attrs={"class":"form-control"}),
    )

    orden = forms.ChoiceField(
        label="Orden",
        choices=ordenes,
        required=False,
        widget=forms.Select(attrs={"class":"form-control"}),
    )

    def filtros(self):
        retorno = {}
        if self.is_valid():
            fields = ("nombre", "descripcion")
            for field in fields:
                if field in self.cleaned_data and self.cleaned_data[field]:
                    retorno[field] = self.cleaned_data[field]
        return retorno

    def criterio(self):
        if self.cleaned_data and "segun" in self.cleaned_data:
            return self.cleaned_data["segun"]
        return None

    def ascendente(self):
        if self.cleaned_data and "orden" in self.cleaned_data:
            return (self.cleaned_data["orden"] == "a")
        return None

