from decimal import Decimal
from datetime import datetime

from django import forms
from django.urls import reverse_lazy
from django.core.validators import MinValueValidator

from VeterinariaPatagonica.forms import BaseFormSet, BaseForm
from VeterinariaPatagonica.widgets import SubmitButtons
from VeterinariaPatagonica.errores import VeterinariaPatagonicaError
from VeterinariaPatagonica.viewsAutocomplete import productoSelectLabelActiva, clienteSelectLabel, practicaRealizadaSelectLabel
from Apps.GestionDePracticas import permisos
from Apps.GestionDeClientes.models import Cliente
from Apps.GestionDeProductos.models import Producto
from Apps.GestionDePracticas.models.practica import Practica
from Apps.GestionDePracticas.models.estado import Realizada
from .models import Factura, DetalleFactura

from dal.autocomplete import ModelSelect2


DATE_INPUT_FMTS = ("%d/%m/%y", "%d/%m/%Y")


class ProductoModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return productoSelectLabelActiva(obj)


class RealizadaModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return practicaRealizadaSelectLabel(obj)


class ClienteModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return clienteSelectLabel(obj)


class FacturarPracticaForm(forms.Form):

    tipo = forms.CharField(
        help_text="Debe elegir el tipo de facturación a realizar: A, B o C.",
        initial=Factura.TIPODEFACTURA[1][0],
        widget=forms.Select(
            choices=Factura.TIPODEFACTURA,
            attrs={"class":"form-control"},
        ),
    )

    fecha = forms.DateField(
        help_text="Puede ingresar la fecha de emisión de la factura.",
        initial=datetime.now().date(),
        input_formats=DATE_INPUT_FMTS,
        widget=forms.DateInput(
            format=DATE_INPUT_FMTS[0],
            attrs={"class":"form-control"},
        ),
    )

    recargo = forms.DecimalField(
        required=False,
        initial=Decimal(0),
        help_text="Puede agregar un porcentaje de recargo que se aplicara sobre el importe total facturado.",
        max_digits = Practica.MAX_DIGITOS,
        decimal_places = Practica.MAX_DECIMALES,
        widget = forms.TextInput(
            attrs={ "class" : "form-control" }
        ),
        validators=[MinValueValidator(0, "El porcentaje de recargo debe ser mayor que cero")]
    )

    descuento = forms.DecimalField(
        required=False,
        initial=Decimal(0),
        help_text="Puede agregar un porcentaje de descuento que se aplicara sobre el importe total facturado.",
        max_digits = Practica.MAX_DIGITOS,
        decimal_places = Practica.MAX_DECIMALES,
        widget = forms.TextInput(
            attrs={ "class" : "form-control" }
        ),
        validators=[MinValueValidator(0, "El porcentaje de descuento debe ser mayor que cero")]
    )

    def __init__(self, *args, practica=None, formsetProductos=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.practica = practica
        self.formsetProductos = formsetProductos
        self.productos = None
        self.instancia = None

    def factura(self):
        if self.instancia is None:
            datos = {}
            if self.practica is not None:
                datos["total"] = self.practica.estados.realizacion().total()
                datos["cliente"] = self.practica.cliente
                datos["practica"] = self.practica
            if self.is_valid():
                datos.update(self.cleaned_data)
            self.instancia = Factura(**datos)
            self.instancia.total = self.instancia.calcularTotal(
                detalles=self.productosFactura(),
                practica=self.instancia.practica,
                descuento=self.instancia.descuento,
                recargo=self.instancia.recargo,
            )
        return self.instancia

    def productosFactura(self):
        if self.productos is None:
            self.productos = self.formsetProductos.productos()
        return self.productos

    def clean(self):
        retorno = super().clean()
        if self.is_valid() and self.formsetProductos.is_valid():
            practica = self.factura().practica
            productos = self.productosFactura()
            if (practica is None) and (not productos):
                self.add_error(
                    None,
                    forms.ValidationError("La facturacion no puede completarse sin practica ni productos.")
                )
        return retorno

    def crearFactura(self):
        if not (self.is_valid() and self.formsetProductos.is_valid()):
            raise VeterinariaPatagonicaError("No se pudieron guardar los datos de la facturación, los datos del formulario no eran validos.")
        factura = self.factura()
        factura.save(force_insert=True)
        productosFactura = self.productosFactura()
        if len(productosFactura)>0:
            factura.detalles_producto.set(productosFactura, bulk=False)
        return factura

class FacturarForm(FacturarPracticaForm):


    cliente = ClienteModelChoiceField(
        queryset=Cliente.objects.habilitados(),
        empty_label=None,
        to_field_name="id",
        help_text="Seleccione al cliente a nombre del cual se registrara la facturación.",
        widget=ModelSelect2(
            url=reverse_lazy("autocomplete:cliente"),
            attrs={"data-allow-clear": "false"}
        ),
    )

    practica = RealizadaModelChoiceField(
        required=False,
        queryset=Practica.objects.enEstado(Realizada),
        empty_label="Ninguna",
        to_field_name="id",
        help_text="Puede agregar una práctica realizada a nombre del cliente a la facturación.",
        widget=ModelSelect2(
            url=reverse_lazy("autocomplete:practicaRealizada"),
            attrs={"data-allow-clear": "true"},
            forward=["cliente"]
        ),
    )

    def __init__(self, *args, practica=None, field_order=["cliente", "practica"], **kwargs):
        super().__init__(*args, field_order=field_order, **kwargs)

    def clean(self):
        retorno = super().clean()
        if ("cliente" in retorno) and ("practica" in retorno):
            practica = retorno["practica"]
            if (practica is not None):
                cliente = retorno["cliente"]
                if practica.cliente.id != cliente.id:
                    self.add_error(
                        "practica",
                        forms.ValidationError("La práctica debe haber sido realizada a nombre del cliente.")
                    )
        return retorno

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

    producto = ProductoModelChoiceField(
        required=False,
        empty_label="Ninguno",
        to_field_name="id",
        queryset=Producto.objects.habilitados(),
        widget=ModelSelect2(
            url=reverse_lazy(
                "autocomplete:producto",
                args=("productos",)
            )
        )
    )

class ProductosFormSet(BaseFormSet):
    min_num = 0
    max_num = 1000
    absolute_max = 2000
    validate_min = False
    validate_max = False
    extra=1
    form=FacturaProductoForm
    id_fields=["producto"]
    ignorar_incompletos = True

    def productos(self):
        detalles = []
        if self.is_valid():
            for dato in self.completos():
                cantidad = dato["cantidad"]
                if cantidad:
                    producto = dato["producto"]
                    detalles.append(DetalleFactura(
                        producto = producto,
                        cantidad = cantidad,
                        subtotal = producto.precioPorUnidad * cantidad
                    ))
        return detalles

class FiltradoFacturaForm(BaseForm):


    tipo = forms.ChoiceField(
        required=False,
        choices=[(None, "Cualquiera")] + list(Factura.TIPODEFACTURA),
        widget=forms.Select(
            attrs={"class" : "form-control"}
        )
    )

    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder" : "Cliente"}
        )
    )

    fecha_desde = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder" : "Desde fecha"}
        ),
        error_messages={
            "invalid" : "Fecha desde debe tener el formato <dia>/<mes>/<año>",
        },
    )

    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder" : "Hasta fecha"}
        ),
        error_messages={
            "invalid" : "Fecha hasta debe tener el formato <dia>/<mes>/<año>",
        },
    )

    productos = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder" : "Productos"}
        )
    )

    rubros = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder" : "Rubros"}
        )
    )

    importe_desde = forms.DecimalField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder" : "Desde importe"}
        )
    )

    importe_hasta = forms.DecimalField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder" : "Hasta importe"}
        )
    )

    def filtros(self):

        retorno = self.datosCumplen(bool)

        if "productos" in retorno:
            retorno["productos"] = [
                valor for valor in retorno["productos"].split(" ") if len(valor)
            ]

        if "rubros" in retorno:
            retorno["rubros"] = [
                valor for valor in retorno["rubros"].split(" ") if len(valor)
            ]

        return retorno


class AccionesFacturacionForm(forms.Form):

    acciones = forms.CharField(
        required=False,
        label="",
        widget=SubmitButtons(
            option_attrs={"class" : "btn btn-sm btn-default"},
            choices=(
                ("actualizar", "Actualizar"),
                ("guardar", "Guardar"),
            )
        ),
    )

    def accion(self):
        if self.is_valid():
            retorno = self.cleaned_data["acciones"]
        else:
            retorno = ""
        return retorno


# from .models import Factura, DetalleFactura, MAXDIGITO, MAXDECIMAL
# from django import forms
# from dal import autocomplete
# from Apps.GestionDePracticas.models.practica import Practica
# from Apps.GestionDePracticas.models.estado import Realizada

# from django.core.validators import MinValueValidator
# from Apps.GestionDeProductos.models import Producto
# from VeterinariaPatagonica.forms import BaseFormSet

# DATE_INPUT_FMTS = ("%d/%m/%y", "%d/%m/%Y")

# TIPO_CHOICES = (
#     ("A", "Factura tipo A"),
#     ("B", "Factura tipo B"),
#     ("C", "Factura tipo C"),
# )

# def FacturaFormFactory(practica):
#     class FacturaForm(forms.ModelForm):
#         class Meta:
#             model = Factura
#             fields = {'tipo', 'cliente', 'fecha','descuento','recargo', 'practica', 'total'}

#             labels = {
#                 'tipo': 'Tipo:',
#                 'cliente': 'Cliente:',
#                 'fecha': 'Fecha:',
#                 'descuento' : 'Descuento:',
#                 'recargo' : 'Recargo:',
#                 'practica': 'Práctica:',
#                 'total': 'Total:',
#             }

#             error_messages = {
#                 'tipo': {
#                     'max_length': ("Nombre demasiado largo"),
#                 }
#             }

#             widgets = {

#                 'cliente': autocomplete.ModelSelect2(url='/GestionDeFacturas/clienteAutocomplete'),
#                 'total': Factura.precioTotal(Factura),
#             }



#         def clean(self):
#             cleaned_data = super().clean()
#             return cleaned_data

#         def __init__(self, *args, **kwargs):

#             super().__init__(*args, **kwargs)

#             # [TODO] Averiguar una mejor manera de hacer esto:
#             for field in self.fields.values():
#                 if not isinstance(field.widget, forms.CheckboxInput):
#                     field.widget.attrs.update({
#                         'class': 'form-control'
#                     })


#         field_order = [
#             'tipo',
#             'cliente',
#             'fecha',
#             'descuento',
#             'recargo',
#             'practica',
#             'total',
#         ]
#     return FacturaForm

# class FacturaForm(forms.ModelForm):
#     class Meta:
#         model = Factura
#         fields = [
#             'tipo',
#             'cliente',
#             'fecha',
#             'descuento',
#             'recargo',
#             'practica',
#             'total'
#         ]

#         labels = {
#             'tipo':'Tipo:',
#             'cliente' : 'Cliente:',
#             'fecha' : 'Fecha:',
#             'descuento' : 'Descuento:',
#             'recargo' : 'Recargo:',
#             'practica': 'Práctica:',
#             'total': 'Total:'
#         }

#         error_messages = {
#             'tipo' : {
#                 'max_length': ("Nombre demasiado largo"),
#             }
#         }

#         widgets = {
#             'cliente': autocomplete.ModelSelect2(url='/GestionDeFacturas/clienteAutocomplete'),
#             #'total': Factura.calcular_subtotales(Factura, DetalleFactura)
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         return cleaned_data

#     def __init__(self, *args, **kwargs):

#         super().__init__(*args, **kwargs)

#         # [TODO] Averiguar una mejor manera de hacer esto:
#         for field in self.fields.values():
#             if not isinstance(field.widget, forms.CheckboxInput):
#                 field.widget.attrs.update({
#                     'class': 'form-control'
#                 })
#         self.fields["practica"].queryset = Practica.objects.enEstado(Realizada)

#     field_order=[
#             'tipo',
#             'cliente',
#             'fecha',
#     ]

# class DetalleFacturaForm(forms.ModelForm):
#     class Meta:
#         model = DetalleFactura
#         fields= [
#             #'factura',
#             'producto',
#             'cantidad',
#             #'subtotal',
#         ]

#         widgets = {
#             'producto': autocomplete.ModelSelect2(url='/GestionDeFacturas/productoAutocomplete'),

#         }
#         #widgets = {
#         #    'subtotal' : forms.NumberInput(attrs={'disabled': '', 'value': 0.0}),
#         #}

# class DetalleFacturaBaseFormSet(forms.BaseModelFormSet):
#     def clean(self):
#         ret = super().clean()
#         productos = [form.cleaned_data for form in self if form.cleaned_data]#Obtengo los productos puestos en el formulario (No toma las tuplas vacias).
#         producto_ids = [d["producto"].pk for d in productos if not d["DELETE"]]#Obtengo los Ids de los productos que no estén marcados como "eliminados"(El Checkbox "eliminar").
#         if len(producto_ids) != len(set(producto_ids)):#Verifico si hay productos repetidos.
#             raise forms.ValidationError("Hay productos repetidos.")
#         return ret

#     def save(self, commit=True):
#         return super().save(commit=commit)


# class FacturarPracticaForm(forms.ModelForm):

#     class Meta:
#         model = Factura

#         fields = [
#             "tipo",
#             "fecha",
#             "recargo",
#             "descuento",
#         ]

#         error_messages = {
#         }

#         widgets = {
#             "fecha" : forms.DateInput(format=DATE_INPUT_FMTS[0]),
#             "tipo"  : forms.Select(choices=TIPO_CHOICES)
#         }

#     field_order=[
#         "tipo",
#         "fecha",
#         "recargo",
#         "descuento",
#     ]

#     def clean(self):
#         cleaned_data = super().clean()
#         return cleaned_data

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields["tipo"].widget.attrs.update({ "class" : "form-control" })

#         self.fields["fecha"].widget.attrs.update({ "class" : "form-control" })
#         self.fields["fecha"].input_formats = DATE_INPUT_FMTS

#         self.fields["recargo"].label = "Porcentaje de recargo"
#         self.fields["recargo"].widget.attrs.update({ "class" : "form-control" })
#         self.fields["recargo"].validators.clear()
#         self.fields["recargo"].validators.append(
#             MinValueValidator(0, "El porcentaje de recargo debe ser mayor que cero")
#         )

#         self.fields["descuento"].label = "Porcentaje de descuento"
#         self.fields["descuento"].widget.attrs.update({ "class" : "form-control" })
#         self.fields["descuento"].validators.clear()
#         self.fields["descuento"].validators.append(
#             MinValueValidator(0, "El porcentaje de descuento debe ser mayor que cero")
#         )



# class ProductoChoiceField(forms.ModelChoiceField):
#     def label_from_instance(self, obj):
#         return obj.describir()



# class FacturaProductoForm(forms.Form):

#     cantidad =  forms.IntegerField(
#         required=False,
#         min_value=0,
#         widget=forms.TextInput(
#             attrs={'class': 'form-control'}
#         ),
#         error_messages={
#             "required" : "La cantidad es obligatoria",
#             "invalid" : "La cantidad debe ser un numero entero",
#             "min_value" : "La cantidad debe ser mayor o igual que cero",
#         }
#     )

#     producto = ProductoChoiceField(
#         required=False,
#         queryset=Producto.objects.habilitados().filter(precioPorUnidad__gt=0).order_by("precioPorUnidad", "nombre"),
#         widget=forms.Select(
#             attrs={'class': 'form-control'}
#         )
#     )

#     def clean(self):
#         data = super().clean()

#         if ("producto" in data and data["producto"]) and (not data["cantidad"]):
#             data["cantidad"] = 0

#         self.cleaned_data = data
#         return self.cleaned_data



# class FacturaProductoFormSet(BaseFormSet):
#     min_num = 0
#     max_num = 1000
#     absolute_max = 2000
#     validate_min = False
#     validate_max = False
#     extra=1
#     form=FacturaProductoForm
#     id_fields=["producto"]
#     ignorar_incompletos = True


