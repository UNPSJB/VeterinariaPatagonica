from decimal import Decimal
from datetime import datetime, date, time, timedelta

from django import forms
from django.core.validators import MinValueValidator

from VeterinariaPatagonica.forms import BaseFormSet, QuerysetFormSet
from VeterinariaPatagonica.areas import Areas
from VeterinariaPatagonica.tools import paramsToFilter
from VeterinariaPatagonica.widgets import SubmitSelect
from VeterinariaPatagonica.errores import VeterinariaPatagonicaError
from Apps.GestionDeClientes.models import Cliente
from Apps.GestionDeMascotas.models import Mascota
from Apps.GestionDeServicios.models import Servicio
from Apps.GestionDeProductos.models import Producto
from Apps.GestionDeTiposDeAtencion.models import TipoDeAtencion
from .models import *

from dal import autocomplete



DATETIME_INPUT_FMTS = ("%d/%m/%y %H:%M", "%d/%m/%Y %H:%M")
DATE_INPUT_FMTS = ("%d/%m/%y", "%d/%m/%Y")
TIME_INPUT_FMTS = ("%H:%M",)



# Fields ######################################################################

class NombreModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj.nombre)



class ServicioModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.describir()



class ProductoModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.describir()



# Practica y estados ##########################################################

class ActualizarPracticaBaseForm(forms.Form):

    def actualizarPractica(self):
        if "mascota" in self.fields:
            mascota = self.cleaned_data["mascota"]
            self.practica.mascota = mascota

    def __init__(self, *args, practica=None, mascota_required=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.practica = practica

        if (self.practica is not None) and (self.practica.mascota is None):
            mascotas  = self.practica.cliente.mascota_set
            self.fields["mascota"] = NombreModelChoiceField(
                queryset=mascotas.habilitados(),
                widget=forms.Select(attrs={"class" : "form-control"}),
            )
            self.fields.move_to_end("mascota", last=False)
            if mascota_required:
                self.fields["mascota"].empty_label = None
            else:
                self.fields["mascota"].required = False



class DesdeHastaForm(forms.Form):

    desde = forms.DateTimeField(
        input_formats=DATETIME_INPUT_FMTS,
        label="Fecha y hora de inicio",
        widget=forms.DateInput(
            format=DATETIME_INPUT_FMTS[0],
            attrs={
                "class":"form-control",
            },
        ),
        error_messages={
            "required" : "Fecha y hora de inicio son obligatorias",
            "invalid" : "Fecha y hora de inicio deben tener el formato <dia>/<mes>/<año> <horas>:<minutos>",
        },
    )

    hasta = forms.DateTimeField(
        required=False,
        input_formats=DATETIME_INPUT_FMTS,
        label="Fecha y hora de finalizacion",
        widget=forms.DateInput(
            format=DATETIME_INPUT_FMTS[0],
            attrs={
                "class":"form-control",
            },
        ),
        error_messages={
            "required" : "Fecha y hora de finalizacion son obligatorias",
            "invalid" : "Fecha y hora de finalizacion deben tener el formato <dia>/<mes>/<año> <horas>:<minutos>",
        },
    )

    duracion = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.TextInput(attrs={"class":"form-control"}),
        error_messages={
            "required" : "La duracion es obligatoria",
            "invalid" : "La duracion debe ser un numero entero",
            "min_value" : "La duracion debe ser mayor que cero",
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unidad = "minutes"

    def datetimeInicio(self):
        if hasattr(self, "cleaned_data") and "desde" in self.cleaned_data:
            return self.cleaned_data["desde"]
        else:
            return None

    def datetimeFinalizacion(self):
        if hasattr(self, "cleaned_data") and "hasta" in self.cleaned_data:
            return self.cleaned_data["hasta"]
        else:
            return None

    def timedeltaDuracion(self):
        if hasattr(self, "cleaned_data") and "duracion" in self.cleaned_data:
            kwargs = {self.unidad : self.cleaned_data["duracion"]}
            return timedelta(**kwargs)
        else:
            return None

    def clean(self):
        retorno = super().clean()

        inicio = retorno["desde"] if "desde" in retorno else None
        finalizacion = retorno["hasta"] if "hasta" in retorno else None
        lapso = retorno["duracion"] if "duracion" in retorno else None

        if (finalizacion == lapso == None):
            raise forms.ValidationError("La fecha y hora de finalizacion (o duracion) son obligatorias)")
        else:
            if finalizacion == None:
                retorno["hasta"] = inicio + self.timedeltaDuracion()
            elif lapso == None:
                retorno["duracion"] = finalizacion - inicio
            else:
                if (inicio + self.timedeltaDuracion() != finalizacion):
                    raise forms.ValidationError("La fecha y hora de finalizacion no coincide con la duracion")

        if retorno["desde"] > retorno["hasta"]:
            raise forms.ValidationError("La fecha y hora de inicio debe ser anterior a la finalizacion")

        self.cleaned_data.update(retorno)
        return retorno



class PracticaForm(forms.ModelForm):

    class Meta:
        model = Practica
        fields = [ "cliente", "tipoDeAtencion" ]
        labels = {
            "tipoDeAtencion" : "Tipo de atencion"
        }
        widgets = {
            "cliente" :  autocomplete.ModelSelect2(url='/GestionDeMascotas/clienteAutocomplete'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["cliente"].empty_label = None
        self.fields["cliente"].queryset = Cliente.objects.habilitados()
        self.fields["cliente"].widget.attrs.update({"class":"form-control"})

        self.fields["tipoDeAtencion"].empty_label = None
        self.fields["tipoDeAtencion"].label = "Tipo de atencion"
        self.fields["tipoDeAtencion"].queryset = TipoDeAtencion.objects.habilitados()
        self.fields["tipoDeAtencion"].widget.attrs.update({"class":"form-control"})



class PresupuestadaForm(DesdeHastaForm, ActualizarPracticaBaseForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unidad = "days"

        self.fields["desde"].input_formats=DATE_INPUT_FMTS
        self.fields["hasta"].input_formats=DATE_INPUT_FMTS
        self.fields["desde"].widget.format=DATE_INPUT_FMTS[0]
        self.fields["hasta"].widget.format=DATE_INPUT_FMTS[0]

        self.fields["desde"].widget.input_type = "hidden"

        self.fields["hasta"].label = "Fecha de vencimiento"
        self.fields["hasta"].error_messages = {
            "required" : "La fecha de vencimiento es obligatoria",
            "invalid" : "La fecha de vencimiento debe tener el formato <dia>/<mes>/<año>",
        }

        self.fields["duracion"].label = "Dias de vigencia"
        self.fields["duracion"].error_messages = {
            "required" : "La cantidad de dias de vigencia es obligatoria",
            "invalid" : "La cantidad de dias de vigencia debe ser un numero entero",
            "min_value" : "La cantidad de dias de vigencia debe ser mayor que cero",
        }

    @property
    def datos(self):
        return {
            "diasMantenimiento" : self.timedeltaDuracion().days,
        }

    @property
    def accion(self):
        return Practica.Acciones.presupuestar.name



class ProgramadaForm(DesdeHastaForm, ActualizarPracticaBaseForm):

    adelanto = forms.DecimalField(
        max_digits = Practica.MAX_DIGITOS,
        decimal_places = Practica.MAX_DECIMALES,
        widget = forms.TextInput(),
    )

    def __init__(self, *args, precio=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.precio = precio

    def clean(self):
        retorno = super().clean()

        if "adelanto" in self.cleaned_data:
            if (0 > self.cleaned_data["adelanto"]):
                raise forms.ValidationError("El adelanto no puede ser menor a cero")
            if (self.cleaned_data["adelanto"] > self.precio):
                raise forms.ValidationError("El adelanto no puede ser mayor al precio de la practica: %s" % self.precio.to_eng_string())

        return retorno

    @property
    def datos(self):
        return {
            "inicio" : self.datetimeInicio(),
            "finalizacion" : self.datetimeFinalizacion(),
            "adelanto" : self.cleaned_data["adelanto"],
        }

    @property
    def accion(self):
        return Practica.Acciones.programar.name



class ReprogramadaForm(DesdeHastaForm, ActualizarPracticaBaseForm):

    motivo = forms.CharField(
        label="Motivo de reprogramacion",
        required = False,
        widget = forms.Textarea(attrs={
            "cols":60,
            "rows":3,
            "class":"form-control",
        }),
    )

    def clean(self):
        retorno = super().clean()

        nuevoDesde = retorno["desde"]
        nuevoHasta = retorno["hasta"]
        nuevaDuracion = retorno["duracion"]

        anteriorDesde = self.initial["desde"]
        anteriorHasta = self.initial["hasta"]
        anteriorDuracion = self.initial["duracion"]

        nuevo = any([
            nuevaDuracion != anteriorDuracion,
            nuevoHasta != anteriorHasta,
            nuevoDesde != anteriorDesde,
        ])

        if not nuevo:
            raise forms.ValidationError("El nuevo turno no puede ser igual al actual")

        return retorno

    @property
    def datos(self):
        return {
            "inicio" : self.datetimeInicio(),
            "finalizacion" : self.datetimeFinalizacion(),
            "motivoReprogramacion" : self.cleaned_data["motivo"],
        }

    @property
    def accion(self):
        return Practica.Acciones.reprogramar.name



class RealizadaForm(DesdeHastaForm, ActualizarPracticaBaseForm):

    @property
    def datos(self):
        return {
            "inicio" : self.datetimeInicio(),
            "finalizacion" : self.datetimeFinalizacion(),
        }

    @property
    def accion(self):
        return Practica.Acciones.realizar.name

    def clean(self):
        retorno = super().clean()
        if retorno["desde"] >= retorno["hasta"]:
            raise forms.ValidationError("La fecha y hora de inicio debe ser anterior a la fecha y hora de finalizacion")
        return retorno



class CanceladaForm(ActualizarPracticaBaseForm):

    motivo = forms.CharField(
        required = False,
        widget = forms.Textarea(attrs={
            "cols":60,
            "rows":3,
            "class":"form-control",
        }),
    )

    @property
    def datos(self):

        datos = {
            "motivo" : self.cleaned_data["motivo"],
        }

        return datos

    @property
    def accion(self):
        return Practica.Acciones.cancelar.name



class ObservacionesGeneralesForm(forms.ModelForm):

    class Meta:
        model = Realizada
        fields = ["condicionPreviaMascota", "resultados"]
        widgets = {
            "condicionPreviaMascota" : forms.Textarea(attrs={
                "cols":60,
                "rows":3,
                "class":"form-control",
            }),
            "resultados" : forms.Textarea(attrs={
                "cols":60,
                "rows":3,
                "class":"form-control",
            }),
        }

        labels = {
            "condicionPreviaMascota" : "Condicion previa de la mascota",
            "resultados" : "Resultados de la practica",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["condicionPreviaMascota"].required = False
        self.fields["resultados"].required = False



class ObservacionesServiciosBaseForm(forms.ModelForm):

    class Meta:
        model = RealizadaServicio
        fields = ["servicio", "observaciones"]
        widgets = {
            "servicio" : forms.HiddenInput(),
            "observaciones" : forms.Textarea(attrs={
                "cols":60,
                "rows":3,
                "class":"form-control",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["observaciones"].required = False
        self.fields["observaciones"].label = self.instance.servicio.nombre



class ObservacionesServiciosBaseFormSet(forms.BaseInlineFormSet):

    def clean(self):

        recibidos = self.total_form_count()
        iniciales = self.initial_form_count()
        originales = self.instance.servicios.count()

        if not recibidos == iniciales == originales:
            raise forms.ValidationError("Cantidad de formularios de servicios no valida")

        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



ObservacionesServiciosFormSet = forms.inlineformset_factory(
    Realizada,
    RealizadaServicio,
    fields=("observaciones", "servicio"),
    form=ObservacionesServiciosBaseForm,
    formset=ObservacionesServiciosBaseFormSet,
    extra=0,
    can_order=False,
    can_delete=False,
    validate_min=False,
    validate_max=False,
)



# Formsets de productos #######################################################

class PracticaProductoForm(forms.Form):

    cantidad =  forms.IntegerField(
        required=True,
        min_value=1,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        ),
        error_messages={
            "required" : "La cantidad es obligatoria",
            "invalid" : "La cantidad debe ser un numero entero",
            "min_value" : "La cantidad debe ser mayor que cero",
        }
    )

    producto = forms.TypedChoiceField(
        coerce=int,
        choices=(),
        empty_value=None,
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )

    def __init__(self, *args, choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        if choices is None:
            productos = Producto.objects.habilitados().order_by("precioPorUnidad", "nombre")
            choices = tuple([
                (
                    producto.pk,
                    producto.describir(),
                ) for producto in productos
            ])
        self.fields["producto"].choices = choices



class PracticaProductoFormSet(BaseFormSet):
    form=PracticaProductoForm
    id_fields=["producto"]



class PracticaRealizadaProductoForm(forms.ModelForm):

    class Meta:
        model = RealizadaProducto
        fields = ["cantidad", "producto"]
        widgets = {
            "producto" : forms.Select(
                attrs={'class': 'form-control'}
            ),
            "cantidad" : forms.TextInput(
                attrs={'class': 'form-control'}
            ),
        }
        field_classes = {
            "producto" : ProductoModelChoiceField,
        }

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if queryset is None:
            queryset =  Producto.objects.habilitados().order_by("precioPorUnidad", "nombre")
        self.fields["producto"].queryset = queryset
        self.fields["producto"].empty_label = None
        self.fields["cantidad"].validators.insert(0, MinValueValidator(
            1,
            message="Cantidad debe ser mayor que cero"
        ))




class PracticaRealizadaProductoFormSet(QuerysetFormSet):

    id_fields = [ "producto" ]
    form = PracticaRealizadaProductoForm

    def __init__(self, *args, instancia=None, **kwargs):
        self.instancia = instancia
        queryset = self.instancia.realizada_productos.all()
        super().__init__(*args, queryset=queryset, **kwargs)

    def clean(self):
        retorno = super().clean()
        if self.total_error_count() == 0:
            for instancia in self.para_agregar:
                instancia.realizada = self.instancia
                instancia.precio = instancia.producto.precioDeCompra
        return retorno



# Formsets de servicios #######################################################

class PracticaServicioForm(forms.Form):

    cantidad =  forms.IntegerField(
        required=True,
        min_value=1,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        ),
        error_messages={
            "required" : "La cantidad es obligatoria",
            "invalid" : "La cantidad debe ser un numero entero",
            "min_value" : "La cantidad debe ser mayor que cero",
        }
    )

    servicio = forms.TypedChoiceField(
        empty_value=None,
        coerce=int,
        choices=(),
        widget=forms.Select(
            attrs={'class': 'form-control'}
        ),
    )

    def __init__(self, *args, choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        if choices is None:
            choices = tuple([
                (servicio.pk, servicio.describir()) for servicio in Servicio.objects.habilitados().order_by("nombre")
            ])
        self.fields["servicio"].choices = choices



class ConsultaServicioForm(PracticaServicioForm):

    def __init__(self, *args, choices=None, **kwargs):
        if choices is None:
            choices = tuple([
                (servicio.pk, servicio.describir()) for servicio in Servicio.objects.habilitados().filter(
                    tipo=Areas.C.codigo,
                ).order_by(
                    "nombre"
                )
            ])
        super().__init__(*args, choices=choices, **kwargs)



class CirugiaServicioForm(PracticaServicioForm):

    def __init__(self, *args, choices=None, **kwargs):
        if choices is None:
            choices = tuple([
                (servicio.pk, servicio.describir()) for servicio in Servicio.objects.habilitados().filter(
                    tipo=Areas.Q.codigo,
                ).order_by(
                    "nombre"
                )
            ])
        super().__init__(*args, choices=choices, **kwargs)



class PracticaServicioFormSet(BaseFormSet):
    form=PracticaServicioForm
    id_fields=["servicio"]



class ConsultaServicioFormSet(BaseFormSet):
    form=ConsultaServicioForm
    id_fields=["servicio"]



class CirugiaServicioFormSet(BaseFormSet):
    form=CirugiaServicioForm
    id_fields=["servicio"]



class PracticaRealizadaServicioForm(forms.ModelForm):

    class Meta:
        model = RealizadaServicio
        fields = ["cantidad", "servicio"]
        widgets = {
            "servicio" : forms.Select(
                attrs={'class': 'form-control'}
            ),
            "cantidad" : forms.TextInput(
                attrs={'class': 'form-control'}
            ),
        }
        error_messages = {
            "cantidad" : {
                "required" : "La cantidad es obligatoria",
                "invalid" : "La cantidad debe ser un numero entero",
            },
        }
        field_classes = {
            "servicio" : ServicioModelChoiceField,
        }

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if queryset is None:
            queryset =  Servicio.objects.habilitados().order_by("tipo", "nombre")
        self.fields["servicio"].queryset = queryset
        self.fields["servicio"].empty_label=None
        self.fields["cantidad"].validators.append(MinValueValidator(
            1,
            message="La cantidad debe ser mayor que cero"
        ))



class ConsultaRealizadaServicioForm(PracticaRealizadaServicioForm):

    def __init__(self, *args, queryset=None, **kwargs):
        if queryset is None:
            queryset = Servicio.objects.habilitados().filter(tipo=Areas.C.codigo).order_by("nombre")
        super().__init__(*args, queryset=queryset, **kwargs)



class CirugiaRealizadaServicioForm(PracticaRealizadaServicioForm):

    def __init__(self, *args, queryset=None, **kwargs):
        if queryset is None:
            queryset = Servicio.objects.habilitados().filter(tipo=Areas.Q.codigo).order_by("nombre")
        super().__init__(*args, queryset=queryset, **kwargs)



class ConsultaRealizadaServicioFormSet(QuerysetFormSet):

    id_fields = [ "servicio" ]
    form = ConsultaRealizadaServicioForm

    def __init__(self, *args, instancia=None, **kwargs):
        self.instancia = instancia
        queryset = self.instancia.realizada_servicios.all()
        super().__init__(*args, queryset=queryset, **kwargs)

    def clean(self):
        retorno = super().clean()
        if self.total_error_count() == 0:
            for instancia in self.para_agregar:
                instancia.realizada = self.instancia
        return retorno



class CirugiaRealizadaServicioFormSet(QuerysetFormSet):

    id_fields = [ "servicio" ]
    form = PracticaRealizadaServicioForm

    def __init__(self, *args, instancia=None, **kwargs):
        self.instancia = instancia
        queryset = self.instancia.realizada_servicios.all()
        super().__init__(*args, queryset=queryset, **kwargs)

    def clean(self):
        retorno = super().clean()
        if self.total_error_count() == 0:
            for instancia in self.para_agregar:
                instancia.realizada = self.instancia
        retorno



# Otras #######################################################################



class CreacionForm(forms.Form):

    acciones = forms.CharField(
        required=False,
        label="",
        widget=SubmitSelect(
            option_attrs={"class" : "btn btn-sm btn-default"},
        ),
    )

    def __init__(self, acciones, *args, vacio=None, **kwargs):
        super().__init__(*args, **kwargs)
        choices = []
        if vacio is not None:
            choices.append( ("", vacio) )
        for accion in Practica.Acciones:
            if accion in acciones:
                choices.append( (accion.name, accion.name.capitalize()) )
        self.fields["acciones"].widget.choices = choices

    @property
    def accion(self):
        return self.cleaned_data["acciones"]



class BusquedaForm(forms.Form):

    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Nombres/Apellidos/DNI/CUIT..."})
    )

    mascota = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Nombre/Patente..."})
    )

    tipo_de_atencion = forms.CharField(
        required=False,
        label="Tipo de atencion",
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Nombre..."})
    )

    ultima_mod_desde = forms.DateField(
        required=False,
        input_formats=DATE_INPUT_FMTS,
        label="Ultima actualizacion desde el dia",
        widget=forms.DateInput(
            format=DATE_INPUT_FMTS[0],
            attrs={
                "class":"form-control",
            }
        ),
        error_messages={
            "invalid" : "La fecha debe tener el formato <dia>/<mes>/<año>",
        },
    )

    ultima_mod_hasta = forms.DateField(
        required=False,
        input_formats=DATE_INPUT_FMTS,
        label="Ultima actualizacion hasta el dia",
        widget=forms.DateInput(
            format=DATE_INPUT_FMTS[0],
            attrs={
                "class":"form-control",
            }
        ),
        error_messages={
            "invalid" : "La fecha debe tener el formato <dia>/<mes>/<año>",
        },
    )

    servicios = forms.CharField(
        required=False,
        label="Servicios previstos",
        widget=forms.TextInput(attrs={
            "placeholder":"Terminos a buscar...",
            "class":"form-control",
        })
    )

    productos = forms.CharField(
        required=False,
        label="Productos previstos",
        widget=forms.TextInput(attrs={
            "placeholder":"Terminos a buscar...",
            "class":"form-control",
        })
    )

    servicios_realizados = forms.CharField(
        required=False,
        label="Servicios realizados",
        widget=forms.TextInput(attrs={
            "placeholder":"Terminos a buscar...",
            "class":"form-control",
        })
    )

    productos_utilizados = forms.CharField(
        required=False,
        label="Productos utilizados",
        widget=forms.TextInput(attrs={
            "placeholder":"Terminos a buscar...",
            "class":"form-control",
        })
    )

    estados = forms.TypedMultipleChoiceField(
        choices=tuple(),
        coerce=int,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class":"form-control"}),
    )

    def __init__(self, *args, choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        if choices is not None:
            self.fields["estados"].choices += tuple(choices)
        hoy = datetime.now().date().strftime(DATE_INPUT_FMTS[0])
        self.fields["ultima_mod_desde"].widget.attrs.update({"placeholder" : hoy})
        self.fields["ultima_mod_hasta"].widget.attrs.update({"placeholder" : hoy})

    def filtros(self):
        retorno = {}
        data = self.cleaned_data

        fields = ("cliente", "mascota", "tipo_de_atencion", "ultima_mod_desde", "ultima_mod_hasta", "estados")
        for field in fields:
            if field in data and data[field]:
                retorno[field] = data[field]

        fields = ("servicios", "productos", "servicios_realizados", "productos_utilizados")
        for field in fields:
            if field in data and data[field]:
                retorno[field] = data[field].split()

        return retorno



class BusquedaCirugiaForm(BusquedaForm):

    def __init__(self, *args, **kwargs):
        choices = (
            (estado.TIPO, estado.__name__) for estado in [
                Presupuestada,
                Programada,
                Realizada,
                Cancelada,
                Facturada
            ]
        )
        super().__init__(*args, choices=choices, **kwargs)



class BusquedaConsultaForm(BusquedaForm):

    def __init__(self, *args, **kwargs):
        choices = (
            (estado.TIPO, estado.__name__) for estado in [
                Presupuestada,
                Realizada,
                Cancelada,
                Facturada
            ]
        )
        super().__init__(*args, choices=choices, **kwargs)



class FiltradoForm(forms.Form):

    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Cliente"})
    )

    mascota = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Mascota"})
    )

    estado = forms.TypedChoiceField(
        choices=((None, "Todos"),),
        coerce=int,
        required=False,
        widget=forms.Select(attrs={"class":"form-control"}),
    )

    def filtros(self):
        retorno = {}

        fields = ("cliente", "mascota")
        for field in fields:
            if field in self.cleaned_data and self.cleaned_data[field]:
                retorno[field] = self.cleaned_data[field]

        if "estado" in self.cleaned_data and self.cleaned_data["estado"]:
            retorno["estados"] = [ self.cleaned_data["estado"] ]

        return retorno

    def __init__(self, *args, choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        if choices is not None:
            self.fields["estado"].choices += tuple(choices)



class FiltradoCirugiaForm(FiltradoForm):

    def __init__(self, *args, **kwargs):
        choices = (
            (estado.TIPO, estado.__name__) for estado in [
                Presupuestada,
                Programada,
                Realizada,
                Cancelada,
                Facturada
            ]
        )
        super().__init__(*args, choices=choices, **kwargs)



class FiltradoConsultaForm(FiltradoForm):

    def __init__(self, *args, **kwargs):
        choices = (
            (estado.TIPO, estado.__name__) for estado in [
                Presupuestada,
                Realizada,
                Cancelada,
                Facturada
            ]
        )
        super().__init__(*args, choices=choices, **kwargs)
