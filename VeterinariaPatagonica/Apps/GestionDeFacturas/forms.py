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


class FacturarBaseForm(forms.Form):

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

    def __init__(self, *args, formsetProductos=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.formsetProductos = formsetProductos
        self.productos = None
        self.instancia = None
        self.datos = {}

    def is_valid(self):
        retorno = super().is_valid()
        if self.formsetProductos is not None:
            retorno &= self.formsetProductos.is_valid()
        return retorno

    def productosFactura(self):
        if self.productos is None:
            if self.formsetProductos is not None:
                self.productos = self.formsetProductos.productos()
            else:
                self.productos = ()
        return self.productos

    def factura(self):
        if self.instancia is None:
            if self.is_valid():
                self.datos.update(self.cleaned_data)
            self.instancia = Factura(**self.datos)
            self.instancia.total = self.instancia.calcularTotal(
                detalles=self.productosFactura(),
                practica=self.instancia.practica,
                descuento=self.instancia.descuento,
                recargo=self.instancia.recargo,
            )
        return self.instancia


class FacturarForm(FacturarBaseForm):

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

    def __init__(self, *args, field_order=["cliente", "practica"], **kwargs):
        super().__init__(*args, field_order=field_order, **kwargs)

    def clean(self):
        retorno = super().clean()
        practica = retorno["practica"] if "practica" in retorno else None
        if "fecha" in retorno:
            maxima = datetime.now().date()
            if retorno["fecha"] > maxima:
                self.add_error(
                    "fecha",
                    forms.ValidationError(
                        "La fecha de facturación no puede ser mayor al dia %s" % (
                            maxima.strftime("%d/%m/%Y")
                        )
                    )
                )
            elif practica is not None:
                minima = practica.estados.realizacion().finalizacion.date()
                if retorno["fecha"] < minima:
                    self.add_error(
                        "fecha",
                        forms.ValidationError(
                            "La fecha de facturación no puede ser anterior al %s dia en que se realizo la %s" % (
                                minima.strftime("%d/%m/%Y"),
                                practica.nombreTipo()
                            )
                        )
                    )
        if "cliente" in retorno and practica is not None:
            cliente = retorno["cliente"]
            if practica.cliente.id != cliente.id:
                self.add_error(
                    "practica",
                    forms.ValidationError("La práctica debe haber sido realizada a nombre del cliente.")
                )
        if not self.errors:
            productos = self.productosFactura()
            if (practica is None) and (not productos):
                self.add_error(
                    None,
                    forms.ValidationError("La facturacion no puede completarse sin practica ni productos.")
                )
        return retorno


class FacturarPracticaForm(FacturarBaseForm):

    def __init__(self, practica, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.practica = practica
        if practica is not None:
            self.datos["practica"] = practica
            self.datos["cliente"] = practica.cliente

    def clean(self):
        retorno = super(FacturarBaseForm, self).clean()
        if "fecha" in retorno:
            maxima = datetime.now().date()
            if retorno["fecha"] > maxima:
                self.add_error(
                    "fecha",
                    forms.ValidationError(
                        "La fecha de facturación no puede ser mayor al dia %s" % (
                            maxima.strftime("%d/%m/%Y")
                        )
                    )
                )
            elif self.practica is not None:
                minima = self.practica.estados.realizacion().finalizacion.date()
                if retorno["fecha"] < minima:
                    self.add_error(
                        "fecha",
                        forms.ValidationError(
                            "La fecha de facturación no puede ser anterior al %s dia en que se realizo la %s" % (
                                minima.strftime("%d/%m/%Y"),
                                self.practica.nombreTipo()
                            )
                        )
                    )
        if not self.errors:
            productos = self.productosFactura()
            if (self.practica is None) and (not productos):
                self.add_error(
                    None,
                    forms.ValidationError("La facturacion no puede completarse sin practica ni productos.")
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
                "autocomplete:producto"
            )
        )
    )


class ProductosFormSet(BaseFormSet):
    min_num = 1
    max_num = 1000
    absolute_max = 2000
    validate_min = False
    validate_max = False
    extra=0
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
