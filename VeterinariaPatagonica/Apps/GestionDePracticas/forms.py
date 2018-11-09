from decimal import Decimal

from django import forms

from VeterinariaPatagonica.widgets import SubmitSelect, BooleanHiddenInput
from Apps.GestionDeClientes.models import Cliente
from Apps.GestionDeMascotas.models import Mascota
from Apps.GestionDeServicios.models import Servicio
from Apps.GestionDeProductos.models import Producto
from Apps.GestionDeTiposDeAtencion.models import TipoDeAtencion
from .models import *



# Clases ######################################################################

class PresupuestadaForm(forms.Form):

    diasMantenimiento = forms.IntegerField(min_value=1, required=True)

    def datos(self):
        datos = {
            "diasMantenimiento" : self.cleaned_data["diasMantenimiento"],
        }

        return datos

    def accion(self):
        return "presupuestar"




class ProgramadaForm(forms.Form):

    inicio = forms.DateTimeField(required=True)
    duracion = forms.IntegerField(min_value=0, required=True)

    def datos(self):
        datos = {
            "inicio" : self.cleaned_data["inicio"],
            "duracion" : self.cleaned_data["duracion"],
        }

        return datos

    def accion(self):
        return "programar"



class RealizadaForm(forms.Form):

    inicio = forms.DateTimeField(required=True)

    duracion = forms.IntegerField(min_value=0, required=True)

    condicionPreviaMascota = forms.CharField(
        label="Condicion previa de la mascota",
        required = False,
        widget = forms.Textarea(attrs={ 'cols':60, 'rows':3 })
    )

    resultados = forms.CharField(
        label="Resultados de la practica",
        required = False,
        widget = forms.Textarea(attrs={ 'cols':60, 'rows':3 })
    )

    def datos(self):

        datos = {
            "inicio" : self.cleaned_data["inicio"],
            "duracion" : self.cleaned_data["duracion"],
            "condicionPreviaMascota" : self.cleaned_data["condicionPreviaMascota"],
            "resultados" : self.cleaned_data["resultados"],
        }

        return datos

    def accion(self):
        return "realizar"



class CanceladaForm(forms.Form):

    motivo = forms.CharField(
        required = False,
        widget = forms.Textarea(attrs={ 'cols':60, 'rows':6 })
    )

    def datos(self):

        datos = {
            "motivo" : self.cleaned_data["motivo"],
        }

        return datos

    def accion(self):
        return "cancelar"



class PracticaProductoForm(forms.ModelForm):

    cantidad =  forms.IntegerField(
        label="",
        min_value=1,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )

    producto = forms.ModelChoiceField(
        empty_label=None,
        label="",
        queryset=Producto.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )

    class Meta:
        model = PracticaProducto
        fields = ["cantidad", "producto"]



class RealizadaProductoForm(forms.ModelForm):

    cantidad =  forms.IntegerField(
        label="",
        min_value=1,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )

    producto = forms.ModelChoiceField(
        empty_label=None,
        label="",
        queryset=Producto.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )

    class Meta:
        model = RealizadaProducto
        fields = ["cantidad", "producto"]



class BaseInitialFormSet(forms.BaseInlineFormSet):

    def get_forms(self):
        if self.can_order and self.is_valid():
            return self.ordered_forms
        else:
            return self.forms

    def add_fields(self, form, index):
        super().add_fields(form, index)
        if "ORDER" in form.fields:
            form.fields["ORDER"].widget = forms.HiddenInput()
        if "DELETE" in form.fields:
            form.fields["DELETE"].widget = BooleanHiddenInput()

    def __init__(self, *args, **kwargs):
        if "initial" in kwargs:
            self.extra = len( kwargs["initial"] ) - self.min_num
        super().__init__(*args, **kwargs)



PracticaProductoFormSet =  forms.inlineformset_factory(
    Practica,
    PracticaProducto,
    form=PracticaProductoForm,
    formset=BaseInitialFormSet,
    validate_min=True,
    min_num=1,
    can_delete=True,
    can_order=True,
    extra=0,
)



RealizadaProductoFormSet = forms.inlineformset_factory(
    Realizada,
    RealizadaProducto,
    form=RealizadaProductoForm,
    formset=BaseInitialFormSet,
    validate_min=True,
    min_num=1,
    can_delete=True,
    can_order=True,
    extra=0,
)



class FiltradoForm(forms.Form):

    #[TODO]: Organizar estas opciones:
    estados = [(None, "todos")] + Estado.TIPOS[2:]

    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control"})
    )
    tipoDeAtencion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control"})
    )
    desde = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control"})
    )
    hasta = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control"})
    )
    estado = forms.TypedChoiceField(
        choices=estados,
        coerce=int,
        empty_value=None,
        required=False,
        widget=forms.Select(attrs={"class":"form-control"})
    )
    servicios = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control"})
    )



# Funciones ###################################################################



def seleccionPracticaFormFactory(tipo, queryset):

    class SeleccionBaseForm(forms.Form):

        @property
        def practica(self):
            return self.cleaned_data[tipo]

    attrs = {
            tipo : forms.ModelChoiceField(
                empty_label=None,
                queryset=queryset,
            ),
    }

    return type( "SeleccionForm", (SeleccionBaseForm,), attrs )



def practicaFormFactory(tipo):

    class PracticaBaseForm(forms.ModelForm):

        cliente = forms.ModelChoiceField(
            empty_label=None,
            queryset=Cliente.objects.habilitados(),
        )

        mascota = forms.ModelChoiceField(
            queryset=Mascota.objects.habilitados(),
            required=False,
        )

        tipoDeAtencion = forms.ModelChoiceField(
            empty_label=None,
            label="Tipo de atencion",
            queryset=TipoDeAtencion.objects.habilitados().filter(tipoDeServicio=TIPO_PRACTICA[tipo]),
        )

        recargo = forms.DecimalField(
            required=False,
            label="Porcentaje de descuento",
            initial=Decimal(0),
        )

        descuento = forms.DecimalField(
            required=False,
            label="Porcentaje de recargo",
            initial=Decimal(0),
        )

        def clean(self):

            if self.submitForm is None:
                return

            if not self.submitForm.is_valid():
                raise forms.ValidationError(
                    "El formulario de acciones no es valido" + str(self.submitForm.errors),
                    code="accionesNoValido",
                )

            accion = self.submitForm.estadoInicial()
            mascota = self.cleaned_data["mascota"]

            if (mascota is None) and (accion != "presupuestada"):
                raise forms.ValidationError(
                    "El campo '%(campo)s' es obligatorio",
                    code="faltaCampo",
                    params={"campo" : "mascota"}
                )

        def __init__(self, *args, submitForm=None, **kwargs):
            self.submitForm = submitForm
            super().__init__(*args, **kwargs)

        class Meta:
            model = Practica
            fields = [ "cliente", "mascota", "tipoDeAtencion", "recargo", "descuento" ]

    return type( tipo.capitalize()+"Form", (PracticaBaseForm,), {} )



def practicaServicioFormFactory(tipo):

    class PracticaServicioBaseForm(forms.ModelForm):

        cantidad =  forms.IntegerField(
            label="",
            min_value=1,
            widget=forms.TextInput(
                attrs={'class': 'form-control'}
            )
        )

        servicio = forms.ModelChoiceField(
            empty_label=None,
            label="",
            queryset=Servicio.objects.filter(tipo=TIPO_PRACTICA[tipo]),
            widget=forms.Select(
                attrs={'class': 'form-control'}
            )
        )

        class Meta:
            model = PracticaServicio
            fields = ["cantidad", "servicio"]

    return type( "PracticaServicioForm", (PracticaServicioBaseForm,), {} )



def practicaServicioFormSetFactory(tipo):

    return forms.inlineformset_factory(
        Practica,
        PracticaServicio,
        form=practicaServicioFormFactory(tipo),
        formset=BaseInitialFormSet,
        validate_min=True,
        min_num=1,
        extra=0,
        can_delete=True,
        can_order=True,
    )



def realizadaServicioFormFactory(tipo):

    class RealizadaServicioBaseForm(forms.ModelForm):

        cantidad =  forms.IntegerField(
            label="",
            min_value=1,
            widget=forms.TextInput(
                attrs={'class': 'form-control'}
            )
        )

        servicio = forms.ModelChoiceField(
            empty_label=None,
            label="",
            queryset=Servicio.objects.filter(tipo=TIPO_PRACTICA[tipo]),
            widget=forms.Select(
                attrs={'class': 'form-control'}
            )
        )

        observaciones = forms.CharField(
            label="",
            required = False,
            widget = forms.Textarea(
                attrs={
                    'cols':60,
                    'rows':2,
                    'class': 'form-control',
                    'placeholder': 'Observaciones...',
                }
            )
        )

        class Meta:
            model = RealizadaServicio
            fields = ["cantidad", "servicio", "observaciones"]

    return type( "RealizadaServicioForm", (RealizadaServicioBaseForm,), {} )



def realizadaServicioFormSetFactory(tipo):

    return forms.inlineformset_factory(
        Realizada,
        RealizadaServicio,
        form=realizadaServicioFormFactory(tipo),
        formset=BaseInitialFormSet,
        validate_min=True,
        min_num=1,
        extra=0,
        can_delete=True,
        can_order=True,
    )



def practicaProductoFormSetFactory(tipo):
    return PracticaProductoFormSet



def realizadaProductoFormSetFactory(tipo):
    return RealizadaProductoFormSet



def accionesFormFactory(choices):

    class AccionesBaseForm(forms.Form):

        accion = forms.CharField(
            label="Crear",
            widget=SubmitSelect(
                choices=choices,
                option_attrs={"class" : "btn btn-sm btn-default"},
            ),
        )

        def estadoInicial(self):
            return self.cleaned_data["accion"]

    return type("AccionesForm", (AccionesBaseForm,), {})



###############################################################################



def getInicializacionForm(estadoInicial):

    forms = {
        "presupuestada" : PresupuestadaForm,
        "programada" : ProgramadaForm,
        "realizada" : RealizadaForm
    }

    return forms[estadoInicial]