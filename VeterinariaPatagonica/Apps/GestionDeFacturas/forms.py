from .models import Factura, DetalleFactura, MAXDIGITO, MAXDECIMAL
from django import forms
from dal import autocomplete
from Apps.GestionDePracticas.models.practica import Practica
from Apps.GestionDePracticas.models.estado import Realizada

from django.core.validators import MinValueValidator
from Apps.GestionDeProductos.models import Producto
from VeterinariaPatagonica.forms import BaseFormSet

DATE_INPUT_FMTS = ("%d/%m/%y", "%d/%m/%Y")

TIPO_CHOICES = (
    ("A", "Factura tipo A"),
    ("B", "Factura tipo B"),
    ("C", "Factura tipo C"),
)

def FacturaFormFactory(practica):
    class FacturaForm(forms.ModelForm):
        class Meta:
            model = Factura
            fields = {'tipo', 'cliente', 'fecha','descuento','recargo', 'practica', 'total'}

            labels = {
                'tipo': 'Tipo:',
                'cliente': 'Cliente:',
                'fecha': 'Fecha:',
                'descuento' : 'Descuento:',
                'recargo' : 'Recargo:',
                'practica': 'Práctica:',
                'total': 'Total:',
            }

            error_messages = {
                'tipo': {
                    'max_length': ("Nombre demasiado largo"),
                }
            }

            widgets = {

                'cliente': autocomplete.ModelSelect2(url='/GestionDeFacturas/clienteAutocomplete'),
                'total': Factura.precioTotal(Factura),
            }

            print(Factura.precioTotal(Factura)),

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


        field_order = [
            'tipo',
            'cliente',
            'fecha',
            'descuento',
            'recargo',
            'practica',
            'total',
        ]
    return FacturaForm

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = [
            'tipo',
            'cliente',
            'fecha',
            'descuento',
            'recargo',
            'practica',
            'total'
        ]

        labels = {
            'tipo':'Tipo:',
            'cliente' : 'Cliente:',
            'fecha' : 'Fecha:',
            'descuento' : 'Descuento:',
            'recargo' : 'Recargo:',
            'practica': 'Práctica:',
            'total': 'Total:'
        }

        error_messages = {
            'tipo' : {
                'max_length': ("Nombre demasiado largo"),
            }
        }

        widgets = {
            'cliente': autocomplete.ModelSelect2(url='/GestionDeFacturas/clienteAutocomplete'),
            #'total': Factura.calcular_subtotales(Factura, DetalleFactura)
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
        self.fields["practica"].queryset = Practica.objects.enEstado(Realizada)

    field_order=[
            'tipo',
            'cliente',
            'fecha',
    ]

class DetalleFacturaForm(forms.ModelForm):
    class Meta:
        model = DetalleFactura
        fields= [
            #'factura',
            'producto',
            'cantidad',
            #'subtotal',
        ]

        widgets = {
            'producto': autocomplete.ModelSelect2(url='/GestionDeFacturas/productoAutocomplete'),

        }
        #widgets = {
        #    'subtotal' : forms.NumberInput(attrs={'disabled': '', 'value': 0.0}),
        #}

class DetalleFacturaBaseFormSet(forms.BaseModelFormSet):
    def clean(self):
        ret = super().clean()
        productos = [form.cleaned_data for form in self if form.cleaned_data]#Obtengo los productos puestos en el formulario (No toma las tuplas vacias).
        producto_ids = [d["producto"].pk for d in productos if not d["DELETE"]]#Obtengo los Ids de los productos que no estén marcados como "eliminados"(El Checkbox "eliminar").
        if len(producto_ids) != len(set(producto_ids)):#Verifico si hay productos repetidos.
            raise forms.ValidationError("Hay productos repetidos.")
        return ret

    def save(self, commit=True):
        return super().save(commit=commit)


class FacturarPracticaForm(forms.ModelForm):

    class Meta:
        model = Factura

        fields = [
            "tipo",
            "fecha",
            "recargo",
            "descuento",
        ]

        error_messages = {
        }

        widgets = {
            "fecha" : forms.DateInput(format=DATE_INPUT_FMTS[0]),
            "tipo"  : forms.Select(choices=TIPO_CHOICES)
        }

    field_order=[
        "tipo",
        "fecha",
        "recargo",
        "descuento",
    ]

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tipo"].widget.attrs.update({ "class" : "form-control" })

        self.fields["fecha"].widget.attrs.update({ "class" : "form-control" })
        self.fields["fecha"].input_formats = DATE_INPUT_FMTS

        self.fields["recargo"].label = "Porcentaje de recargo"
        self.fields["recargo"].widget.attrs.update({ "class" : "form-control" })
        self.fields["recargo"].validators.clear()
        self.fields["recargo"].validators.append(
            MinValueValidator(0, "El porcentaje de recargo debe ser mayor que cero")
        )

        self.fields["descuento"].label = "Porcentaje de descuento"
        self.fields["descuento"].widget.attrs.update({ "class" : "form-control" })
        self.fields["descuento"].validators.clear()
        self.fields["descuento"].validators.append(
            MinValueValidator(0, "El porcentaje de descuento debe ser mayor que cero")
        )



class ProductoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.describir()



class FacturaProductoForm(forms.Form):

    cantidad =  forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        ),
        error_messages={
            "required" : "La cantidad es obligatoria",
            "invalid" : "La cantidad debe ser un numero entero",
            "min_value" : "La cantidad debe ser mayor o igual que cero",
        }
    )

    producto = ProductoChoiceField(
        required=False,
        queryset=Producto.objects.habilitados().filter(precioPorUnidad__gt=0).order_by("precioPorUnidad", "nombre"),
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )

    def clean(self):
        data = super().clean()

        if ("producto" in data and data["producto"]) and (not data["cantidad"]):
            data["cantidad"] = 0

        self.cleaned_data = data
        return self.cleaned_data



class FacturaProductoFormSet(BaseFormSet):
    min_num = 0
    max_num = 1000
    absolute_max = 2000
    validate_min = False
    validate_max = False
    extra=1
    form=FacturaProductoForm
    id_fields=["producto"]
    ignorar_incompletos = True

