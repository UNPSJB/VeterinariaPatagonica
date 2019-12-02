from django import forms
from .models import Producto
from dal import autocomplete


rubro = forms.DateField(
    required=True,
    label='rubro',
    widget=forms.CharField,
    help_text='Rubro',
    error_messages={
        'invalid_choice': "La opcion no es valida",
        'required': "el rubro es obligatorio"
    },
    validators=[],

)

def ProductoFormFactory(producto=None):
    campos = [ 'marca', 'descripcion',
               'formaDePresentacion', 'stock',
               'precioDeCompra', 'precioPorUnidad',
               'rubro' ]

    if producto is None:
        campos.insert(0, 'nombre')

    class ProductoForm(forms.ModelForm):

        class Meta:
            model = Producto
            fields = campos
            labels = {
                'nombre':'Nombre:',
                'marca':'Marca:',
                'stock':'Stock:',
                'formaDePresentacion':'Forma de Presentación:',
                'precioPorUnidad':'Precio por Unidad:',
                'precioDeCompra':'Precio de Compra:',
                'rubro':'Rubro:',
                'descripcion':'Descripción:',
                'baja':'Baja:'
            }

            error_messages = {
                'nombre' : {
                    'max_length': ("Nombre demasiado largo"),
                    'unique': ("Ese nombre ya existe"),
                },

                'precioPorUnidad': {
                    'max_digits': "Debe ingresar a lo sumo %d digitos para la parte entera" % (Producto.MAX_ENTERO),
                    'max_whole_digits': "Debe ingresar a lo sumo %d digitos en total" % (Producto.PRECIO),
                },
                'precioDeCompra': {
                    'max_digits': "Debe ingresar a lo sumo %d digitos para la parte entera" % (Producto.MAX_ENTERO),
                    'max_whole_digits': "Debe ingresar a lo sumo %d digitos en total" % (Producto.PRECIO),
                }
            }

            widgets = {
                'descripcion': forms.Textarea(attrs={'cols': 60, 'rows': 4}),
                'formaDePresentacion' : forms.Select(),
                'precioPorUnidad': forms.NumberInput(),
                'precioDeCompra': forms.NumberInput(),
                'rubro' : autocomplete.ModelSelect2(url='/GestionDeProductos/rubroAutocomplete'),
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

    return ProductoForm

class FiltradoForm(forms.Form):

    ordenes = (
        ("d", "Descendente"),
        ("a", "Ascendente"),
    )

    criterios = (
        ("nombre", "Nombre"),
        ("marca", "Marca"),
    )

    nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder":"Nombre...",
            "class":"form-control"
        })
    )

    marca = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder":"Marcas...",
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

        fields = ("nombre", "marca")
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