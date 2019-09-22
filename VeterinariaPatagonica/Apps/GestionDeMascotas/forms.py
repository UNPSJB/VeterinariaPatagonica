from django import forms
from .models import Mascota
from dal import autocomplete


cliente = forms.DateField(
    required=True,
    label='cliente',
    widget=forms.CharField,
    help_text='Cliente',
    error_messages={
        'invalid_choice': "La opcion no es valida",
        'required': "el cliente es obligatorio"
    },
    validators=[],

)
def MascotaFormFactory(mascota=None, cliente=None):
    campos = [ 'nombre', 'cliente',
               'fechaNacimiento',
               'especie', 'raza' ]

    if mascota is None:
        campos.insert(0, 'patente')



    class MascotaForm(forms.ModelForm):

        class Meta:
            model = Mascota
            fields = campos
            widget_cliente = autocomplete.ModelSelect2(url='/GestionDeMascotas/clienteAutocomplete')
            if cliente:
                #widget_cliente = forms.TextInput(attrs={'value': cliente})
                widget_cliente = autocomplete.ModelSelect2(url='/GestionDeMascotas/clienteAutocomplete/?q={}'.format(cliente.dniCuit))

            labels = {
                'patente':'Patente:',
                'cliente': "Cliente:",
                'fechaNacimiento': 'Fecha de Nacimiento:',
                'nombre':'Nombre:',
                'especie':'Especie:',
                'raza': 'Raza:',
                'baja':'Baja:'
            }
            error_messages = {
                'nombre' : {
                    'max_length': ("Nombre demasiados largos"),
                },
                'patente' : {
                    'max_length' : ("patente demasiado largo"),
                    'unique' : ("Esa patente ya existe"),
                }
            }
            widgets = {
                'nombre' : forms.TextInput(),
                'cliente': widget_cliente,
                #'cliente': forms.Select(attrs={'class': 'form-control'}),
                'fechaNacimiento': forms.DateInput(),
                'raza' : forms.TextInput(),
                'especie': forms.TextInput(),
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

    return MascotaForm

class FiltradoForm(forms.Form):

    ordenes = (
        ("d", "Descendente"),
        ("a", "Ascendente"),
    )

    criterios = (
        ("patente", "Patente"),
        ("nombre", "Nombre"),
        ("cliente", "Dueño"),
        ("especie", "Especie"),
    )

    patente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder":"Patente...",
            "class":"form-control"
        })
    )

    nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder":"Nombre...",
            "class":"form-control"
        })
    )

    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder":"Dueño...",
            "class":"form-control"
        })
    )

    especie = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder":"Especie...",
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

        fields = ("patente", "nombre", "cliente", "especie")
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