from django import forms
from django.core.validators import MinValueValidator
from django.core.exceptions import NON_FIELD_ERRORS
from django.urls import reverse_lazy

from VeterinariaPatagonica.forms import BaseFormSet, QuerysetFormSet, DesdeHastaForm, BaseForm
from VeterinariaPatagonica.areas import Areas
from VeterinariaPatagonica.widgets import SubmitButtons
from VeterinariaPatagonica.viewsAutocomplete import (
    servicioSelectLabelActiva,
    insumoSelectLabelActiva,
    tipoDeAtencionSelectLabelActiva,
    clienteSelectLabel,
    mascotaSelectLabel
)
from Apps.GestionDeClientes.models import Cliente
from Apps.GestionDeServicios.models import Servicio
from Apps.GestionDeProductos.models import Producto
from Apps.GestionDeTiposDeAtencion.models import TipoDeAtencion
from .models import *

from dal.autocomplete import ModelSelect2


DATETIME_INPUT_FMTS = ("%d/%m/%y %H:%M", "%d/%m/%Y %H:%M")
DATE_INPUT_FMTS = ("%d/%m/%y", "%d/%m/%Y")
TIME_INPUT_FMTS = ("%H:%M",)



class ServicioModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return servicioSelectLabelActiva(obj)



class ProductoModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return insumoSelectLabelActiva(obj)



class TipoDeAtencionModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return tipoDeAtencionSelectLabelActiva(obj)



class ClienteModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return clienteSelectLabel(obj)



class MascotaModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return mascotaSelectLabel(obj)



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
            self.fields["mascota"] = MascotaModelChoiceField(
                to_field_name="id",
                queryset=mascotas.habilitados(),
                widget=ModelSelect2(
                    url=reverse_lazy(
                        "autocomplete:mascota",
                        args=(self.practica.cliente.id,)
                    ),
                    attrs={"data-allow-clear" : "false"}
                ),
                help_text="Seleccione a cual mascota del cliente se registrará la práctica.",
                error_messages={
                    "required" : "Debe seleccionar alguna mascota",
                    "invalid_choice" : "La mascota seleccionada no es una opción válida"
                }
            )
            self.fields.move_to_end("mascota", last=False)
            if mascota_required:
                self.fields["mascota"].empty_label = None
            else:
                self.fields["mascota"].required = False



class PracticaForm(forms.ModelForm):

    class Meta:
        model = Practica
        fields = [ "cliente", "tipoDeAtencion" ]
        labels = {
            "tipoDeAtencion" : "Tipo de atención"
        }
        help_texts = {
            "cliente" : "Debe agregar un cliente al cual asociarle la práctica. Puede seleccionarlo buscandolo por nombre, apellido o DNI.",
            "tipoDeAtencion" : "Elija el tipo de atención correspondiente.",
        }
        widgets = {
            "cliente" : ModelSelect2(
                url=reverse_lazy("autocomplete:cliente"),
                attrs={
                    "data-allow-clear" : "false"
                }
            ),
            "tipoDeAtencion" : ModelSelect2(
                url=reverse_lazy("autocomplete:tipoDeAtencion"),
                attrs={
                    "data-allow-clear" : "false"
                }
            ),
        }
        field_classes = {
            "cliente" : ClienteModelChoiceField,
            "tipoDeAtencion" : TipoDeAtencionModelChoiceField,
        }
        error_messages={
            "cliente" : {
                "required" : "Debe seleccionar un cliente",
                "invalid_choice" : "El cliente seleccionado no es una opción válida"
            },
            "tipoDeAtencion" : {
                "required" : "Debe seleccionar un tipo de atención",
                "invalid_choice" : "El tipo de atención seleccionado no es una opción válida"
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tipoDeAtencion"].empty_label = None
        self.fields["tipoDeAtencion"].label = "Tipo de atención"
        self.fields["tipoDeAtencion"].queryset = TipoDeAtencion.objects.habilitados()
        self.fields["cliente"].empty_label = None
        self.fields["cliente"].label = "Cliente"
        self.fields["cliente"].queryset = Cliente.objects.habilitados()


class PresupuestadaForm(DesdeHastaForm, ActualizarPracticaBaseForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, unidadDuracion="days", **kwargs)

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

        self.fields["hasta"].help_text = "Ingrese la fecha hasta la cual es válido el presupuesto."
        self.fields["duracion"].help_text = "Ingrese la cantidad de dias que sera válido el presupuesto."

    def datos(self):
        return {
            "diasMantenimiento" : self.timedeltaDuracion().days,
        }

    def accion(self):
        return Practica.Acciones.presupuestar.name



class ProgramadaForm(DesdeHastaForm, ActualizarPracticaBaseForm):

    adelanto = forms.DecimalField(
        help_text="Debe ingresar la suma (en pesos) del adelanto cobrado al cliente.",
        max_digits = Practica.MAX_DIGITOS,
        decimal_places = Practica.MAX_DECIMALES,
        widget = forms.TextInput(),
        error_messages={
            "required" : "El adelanto es obligatorio.",
            "invalid" : "El adelanto ingresado contiene caracteres no válidos, uilice números y el signo separador de decimales.",
            "max_digits" : "El adelanto ingresado tiene demasiados dígitos no decimales, no utilice mas de %d dígitos para la parte entera del adelanto." % (Practica.MAX_DIGITOS - Practica.MAX_DECIMALES),
            "max_decimal_places" : "El adelanto ingresado tiene demasiados dígitos decimales, no utilice mas de %d dígitos decimales." % Practica.MAX_DECIMALES,
            "max_whole_digits" : "El adelanto ingresado tiene demasiados dígitos, no utilice mas de %d dígitos." % Practica.MAX_DIGITOS,
        }
    )

    def __init__(self, *args, precio=0, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["desde"].help_text = "Debe ingresar la fecha y hora de inicio del turno."
        self.fields["hasta"].help_text = "Puede ingresar la fecha y hora de finalizacion del turno."
        self.fields["duracion"].help_text = "Puede ingresar la duración (en minutos) del turno."
        self.precio = precio

    def clean(self):
        retorno = super().clean()
        if "adelanto" not in self.errors:
            if self.cleaned_data["adelanto"] < 0:
                self.add_error(
                    "adelanto",
                    forms.ValidationError("El adelanto no puede ser menor a cero")
                )
            elif self.cleaned_data["adelanto"] > self.precio:
                self.add_error(
                    "adelanto",
                    forms.ValidationError("El adelanto no puede ser mayor al precio de la práctica: %s" % self.precio.to_eng_string())
                )
        return retorno

    def datos(self):
        return {
            "inicio" : self.datetimeInicio(),
            "finalizacion" : self.datetimeFinalizacion(),
            "adelanto" : self.cleaned_data["adelanto"] if self.is_valid() else None,
        }

    def accion(self):
        return Practica.Acciones.programar.name



class ReprogramadaForm(DesdeHastaForm, ActualizarPracticaBaseForm):

    motivo = forms.CharField(
        required = False,
        label="Motivo de reprogramación",
        help_text = "Puede agregar el motivo declarado por el cliente para la reprogramación del turno.",
        widget = forms.Textarea(attrs={
            "cols":60,
            "rows":3,
            "class":"form-control",
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["desde"].help_text = "Debe ingresar la nueva fecha y hora de inicio del turno."
        self.fields["hasta"].help_text = "Puede ingresar la nueva fecha y hora de finalizacion del turno."
        self.fields["duracion"].help_text = "Puede ingresar una nueva duración (en minutos) para el turno."


    def clean(self):
        retorno = super().clean()
        errores  = self.has_error(NON_FIELD_ERRORS, "lapso_incoherente")
        errores |= self.has_error("desde")
        errores |= self.has_error("hasta")
        if not errores:
            nuevoDesde = retorno["desde"]
            nuevoHasta = retorno["hasta"]
            anteriorDesde = self.initial["desde"]
            anteriorHasta = self.initial["hasta"]
            igual = (nuevoDesde == anteriorDesde) and (nuevoHasta == anteriorHasta)
            if igual:
                self.add_error(
                    None,
                    forms.ValidationError("El nuevo turno no puede ser igual al actual")
                )
        return retorno

    def datos(self):
        return {
            "inicio" : self.datetimeInicio(),
            "finalizacion" : self.datetimeFinalizacion(),
            "motivoReprogramacion" : self.cleaned_data["motivo"] if self.is_valid() else None,
        }

    def accion(self):
        return Practica.Acciones.reprogramar.name



class RealizadaForm(DesdeHastaForm, ActualizarPracticaBaseForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["desde"].help_text = "Debe ingresar la fecha y hora a la cual comenzó la realización de la práctica."
        self.fields["hasta"].help_text = "Puede ingresar la fecha y hora de finalizacion de la realización."
        self.fields["duracion"].help_text = "Puede ingresar la duración (en minutos) de la realización."

    def datos(self):
        return {
            "inicio" : self.datetimeInicio(),
            "finalizacion" : self.datetimeFinalizacion(),
        }

    def accion(self):
        return Practica.Acciones.realizar.name



class CanceladaForm(ActualizarPracticaBaseForm):

    motivo = forms.CharField(
        required = False,
        help_text = "Puede agregar el motivo por el cual el cliente cancelo la práctica.",
        widget = forms.Textarea(attrs={
            "cols":60,
            "rows":3,
            "class":"form-control",
        }),
    )

    def datos(self):

        datos = {
            "motivo" : self.cleaned_data["motivo"] if self.is_valid() else None,
        }

        return datos

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
        help_texts = {
            "condicionPreviaMascota" : "Puede registrar la condición de la mascota observada por el veterinario antes de la atención.",
            "resultados" : "Puede registrar la condición de la mascota observada por el veterinario después de la atención.",
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
        self.fields["observaciones"].label = self.instance.servicio.nombre.capitalize()



class ObservacionesServiciosBaseFormSet(forms.BaseInlineFormSet):

    def clean(self):
        retorno = super().clean()
        recibidos = self.total_form_count()
        iniciales = self.initial_form_count()
        originales = self.instance.servicios.count()
        if not (recibidos == iniciales == originales):
            raise forms.ValidationError("Cantidad de servicios no válida")
        return retorno



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



class PracticaProductoForm(forms.Form):

    cantidad =  forms.IntegerField(
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

    producto = ProductoModelChoiceField(
        empty_label=None,
        to_field_name="id",
        queryset=Producto.objects.habilitados(),
        widget=ModelSelect2(
            url=reverse_lazy(
                "autocomplete:insumo"
            ),
            attrs={
                "data-allow-clear": "false",
            }
        ),
        error_messages={
            "required" : "El producto es obligatorio",
            "invalid_choice" : "El producto seleccionado no es una opción válida",
        }
    )

    def clean(self):
        retorno = super().clean()
        if not self.errors:
            retorno["producto"] = retorno["producto"].id
        return retorno


class PracticaProductoFormSet(BaseFormSet):
    form=PracticaProductoForm
    id_fields=["producto"]


class PracticaServicioForm(forms.Form):

    def clean(self):
        retorno = super().clean()
        if not self.errors:
            retorno["servicio"] = retorno["servicio"].id
        return retorno



class ConsultaServicioForm(PracticaServicioForm):

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

    servicio = ServicioModelChoiceField(
        queryset=Servicio.objects.habilitados().filter(tipo=Areas.C.codigo()),
        empty_label=None,
        to_field_name="id",
        widget=ModelSelect2(
            url=reverse_lazy(
                "autocomplete:servicio",
                args=(Areas.C.codigo(),)
            ),
            attrs={
                "data-allow-clear": "false",
            }
        ),
        error_messages={
            "required" : "El servicio es obligatorio",
            "invalid_choice" : "El servicio seleccionado no es una opción válida",
        }
    )



class CirugiaServicioForm(PracticaServicioForm):

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

    servicio = ServicioModelChoiceField(
        queryset=Servicio.objects.habilitados().filter(tipo=Areas.Q.codigo()),
        empty_label=None,
        to_field_name="id",
        widget=ModelSelect2(
            url=reverse_lazy(
                "autocomplete:servicio",
                args=(Areas.Q.codigo(),)
            ),
            attrs={
                "data-allow-clear": "false",
            }
        ),
        error_messages={
            "required" : "El servicio es obligatorio",
            "invalid_choice" : "El servicio seleccionado no es una opción válida",
        }
    )



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
            "servicio" : ModelSelect2(
                url=reverse_lazy(
                    "autocomplete:servicio"
                ),
                attrs={
                    "data-allow-clear": "false",
                }
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
            "servicio" : {
                "required" : "El servicio es obligatorio",
                "invalid_choice" : "El servicio seleccionado no es una opción válida",
            }
        }
        field_classes = {
            "servicio" : ServicioModelChoiceField,
        }

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if queryset is None:
            queryset =  Servicio.objects.habilitados()
        self.fields["servicio"].queryset = queryset
        self.fields["cantidad"].validators.append(
            MinValueValidator(1, message="La cantidad debe ser mayor que cero")
        )


class PracticaRealizadaServicioFormSet(QuerysetFormSet):

    extra = 0
    ignorar_incompletos = True
    id_fields = [ "servicio" ]
    form = PracticaRealizadaServicioForm

    def __init__(self, *args, instancia=None, **kwargs):
        self.instancia = instancia
        queryset = self.instancia.realizada_servicios.all()
        super().__init__(*args, queryset=queryset, **kwargs)

    def clean(self):
        retorno = super().clean()
        if self.total_error_count() == 0:
            tipo = self.instancia.practica.tipo
            delTipo = 0
            for instancia in self.instancias():
                if instancia in self.para_eliminar:
                    continue
                if instancia.servicio.tipo == tipo:
                    delTipo += 1
            if delTipo == 0:
                tipo = Areas[tipo].nombre()
                raise forms.ValidationError(
                    "La %s debe tener algún servicio de tipo '%s'." % (tipo, tipo)
                )
            for instancia in self.para_agregar:
                instancia.realizada = self.instancia
        return retorno


class TurnoRealizadoServicioForm(PracticaRealizadaServicioForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["servicio"].required = False
        self.fields["cantidad"].required = False
        self.fields["servicio"].widget.attrs["data-allow-clear"] = "true"


class TurnoRealizadoServicioFormSet(QuerysetFormSet):

    min_num = 0
    extra = 1
    ignorar_incompletos = True
    id_fields = [ "servicio" ]
    form = TurnoRealizadoServicioForm

    def __init__(self, *args, instancia=None, **kwargs):
        self.instancia = instancia
        i = instancia.practica.practica_servicios.count()
        queryset = self.instancia.realizada_servicios.all()[i:]
        super().__init__(*args, queryset=queryset, **kwargs)

    def clean(self):
        retorno = super().clean()
        if self.total_error_count() == 0:
            for instancia in self.para_agregar:
                if instancia.cantidad is None:
                    self.para_agregar.remove(instancia)
                else:
                    instancia.realizada = self.instancia
            for instancia in self.para_actualizar:
                if instancia.cantidad is None:
                    self.para_actualizar.remove(instancia)
                else:
                    instancia.realizada = self.instancia
        return retorno


class PracticaRealizadaProductoForm(forms.ModelForm):

    class Meta:
        model = RealizadaProducto
        fields = ["cantidad", "producto"]
        widgets = {
            "producto" : ModelSelect2(
                url=reverse_lazy("autocomplete:insumo"),
                attrs={
                    "data-allow-clear": "false",
                }
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
            "producto" : {
                "required" : "El producto es obligatorio",
                "invalid_choice" : "El producto seleccionado no es una opción válida",
            }
        }
        field_classes = {
            "producto" : ProductoModelChoiceField,
        }

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if queryset is None:
            queryset =  Producto.objects.habilitados()
        self.fields["producto"].queryset = queryset
        self.fields["producto"].empty_label = None
        self.fields["cantidad"].validators.append(
            MinValueValidator(1, message="La cantidad debe ser mayor que cero")
        )


class PracticaRealizadaProductoFormSet(QuerysetFormSet):

    extra = 0
    ignorar_incompletos = True
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
        return retorno

    def save(self, *args, **kwargs):

        #[TODO]: Revisar
        actualizacionStock = {}

        cantidadesAnteriores = RealizadaProducto.objects.filter(
            id__in=[ item.id for item in self.para_actualizar ]
        ).values("id", "cantidad")

        cantidadesAnteriores = {
            item["id"] : item["cantidad"] for item in cantidadesAnteriores
        }

        for item in self.para_agregar:
            actualizacionStock[item.producto.id] = -item.cantidad

        for item in self.para_eliminar:
            actualizacionStock[item.producto.id] = item.cantidad

        for item in self.para_actualizar:
            actualizacionStock[item.producto.id] = cantidadesAnteriores[item.id] - item.cantidad

        Producto.objects.actualizarStock(actualizacionStock)
        super().save(*args, **kwargs)


class TurnoRealizadoProductoForm(PracticaRealizadaProductoForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["producto"].required = False
        self.fields["cantidad"].required = False
        self.fields["producto"].widget.attrs["data-allow-clear"] = "true"


class TurnoRealizadoProductoFormSet(QuerysetFormSet):

    min_num = 0
    extra = 1
    ignorar_incompletos = True
    id_fields = [ "producto" ]
    form = TurnoRealizadoProductoForm

    def __init__(self, *args, instancia=None, **kwargs):
        self.instancia = instancia
        i = instancia.practica.practica_productos.count()
        queryset = self.instancia.realizada_productos.all()[i:]
        super().__init__(*args, queryset=queryset, **kwargs)

    def clean(self):
        retorno = super().clean()
        if self.total_error_count() == 0:
            for instancia in self.para_agregar:
                if instancia.cantidad is None:
                    self.para_agregar.remove(instancia)
                else:
                    instancia.realizada = self.instancia
            for instancia in self.para_actualizar:
                if instancia.cantidad is None:
                    self.para_actualizar.remove(instancia)
                else:
                    instancia.realizada = self.instancia
        return retorno


class CreacionForm(forms.Form):

    acciones = forms.CharField(
        required=False,
        label="",
        widget=SubmitButtons(
            option_attrs={"class" : "btn btn-sm btn-default"},
        ),
    )

    def __init__(self, acciones, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = []
        for accion in Practica.Acciones:
            if accion in acciones:
                choices.append( (accion.name, accion.name.capitalize()) )
        self.fields["acciones"].widget.choices = choices

    def accion(self):
        return self.cleaned_data["acciones"] if self.is_valid() else None



class FiltradoForm(BaseForm):

    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Cliente"})
    )

    mascota = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Mascota"})
    )

    tipo_de_atencion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Tipo de atención"}),
    )

    estado = forms.TypedChoiceField(
        choices=((None, "En cualquier estado"),),
        coerce=int,
        required=False,
        widget=forms.Select(attrs={"class":"form-control"}),
    )

    def filtros(self):
        return self.datosCumplen(bool)

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



class FiltradoRealizacionesForm(BaseForm):

    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Cliente"})
    )

    mascota = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Mascota"})
    )

    estado = forms.TypedChoiceField(
        coerce=int,
        required=False,
        widget=forms.Select(attrs={"class":"form-control"}),
        choices=tuple(
            [(None, "Estado: cualquiera")] + [
                (estado.TIPO, "Estado: " + estado.__name__.lower()) for estado in [
                    Realizada,
                    Facturada
                ]
            ]
        ),
    )

    tipo = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={"class":"form-control"}),
        choices=tuple(
            [(None, "Tipo: cualquiera")] + [
                (area[0], "Tipo: " + area[1]) for area in Areas.paresOrdenados()
            ]
        ),
    )

    tipo_de_atencion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Tipo de atención"}),
    )

    realizada_desde = forms.DateTimeField(
        required=False,
        input_formats=DATETIME_INPUT_FMTS,
        widget=forms.DateTimeInput(
            format=DATETIME_INPUT_FMTS[0],
            attrs={
                "class":"form-control",
                "placeholder":"Desde",
            },
        ),
    )

    realizada_hasta = forms.DateTimeField(
        required=False,
        input_formats=DATETIME_INPUT_FMTS,
        widget=forms.DateTimeInput(
            format=DATETIME_INPUT_FMTS[0],
            attrs={
                "class":"form-control",
                "placeholder":"Hasta",
            },
        ),
    )

    def filtros(self):
        return self.datosCumplen(bool)



class FiltradoTurnosForm(BaseForm):

    programada_por = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Registrado por"})
    )

    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Cliente"})
    )

    mascota = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Mascota"})
    )

    tipo_de_atencion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Tipo de atención"}),
    )

    programada_desde = forms.DateTimeField(
        required=False,
        input_formats=DATETIME_INPUT_FMTS,
        widget=forms.DateTimeInput(
            format=DATETIME_INPUT_FMTS[0],
            attrs={
                "class":"form-control",
                "placeholder":"Desde",
            },
        ),
    )

    programada_hasta = forms.DateTimeField(
        required=False,
        input_formats=DATETIME_INPUT_FMTS,
        widget=forms.DateTimeInput(
            format=DATETIME_INPUT_FMTS[0],
            attrs={
                "class":"form-control",
                "placeholder":"Hasta",
            },
        ),
    )

    def filtros(self):
        return self.datosCumplen(bool)


class FiltradoReportesForm(BaseForm):

    PERFILES_CHOICES = [
        ["7", "Últimos 7 días"],
        ["14", "Últimos 14 días"],
    ]
    REALIZACIONES_CHOICES = [
        ["30", "Últimos 30 días"],
        ["60", "Últimos 60 días"],
    ]
    ACTUALIZACIONES_CHOICES = [
        ["30", "Últimos 30 días"],
        ["60", "Últimos 60 días"],
    ]
    TIPOSDEATENCION_CHOICES = [
        ["90", "Últimos 90 días"],
        ["180", "Últimos 180 días"],
    ]

    perfiles = forms.ChoiceField(
        required=False,
        label="Perfil de tipos de atención",
        choices=PERFILES_CHOICES,
        initial=PERFILES_CHOICES[0][0],
        error_messages={
            "invalid_choice" : "La opción seleccionada no es válida"
        },
        widget=forms.Select(
            attrs={
                "class" : "form-control",
            }
        ),
    )

    realizaciones = forms.ChoiceField(
        required=False,
        label="Realizaciones por dia",
        choices=REALIZACIONES_CHOICES,
        initial=REALIZACIONES_CHOICES[0][0],
        error_messages={
            "invalid_choice" : "La opción seleccionada no es válida"
        },
        widget=forms.Select(
            attrs={
                "class" : "form-control",
            }
        ),
    )

    actualizaciones = forms.ChoiceField(
        required=False,
        label="Porcentajes de actualizaciones",
        choices=ACTUALIZACIONES_CHOICES,
        initial=ACTUALIZACIONES_CHOICES[0][0],
        error_messages={
            "invalid_choice" : "La opción seleccionada no es válida"
        },
        widget=forms.Select(
            attrs={
                "class" : "form-control",
            }
        ),
    )

    tiposdeatencion = forms.ChoiceField(
        required=False,
        label="Comparación de tipos de atención",
        choices=TIPOSDEATENCION_CHOICES,
        initial=TIPOSDEATENCION_CHOICES[0][0],
        error_messages={
            "invalid_choice" : "La opción seleccionada no es válida"
        },
        widget=forms.Select(
            attrs={
                "class" : "form-control",
            }
        ),
    )

    acciones = forms.CharField(
        required=False,
        label="",
        widget=SubmitButtons(
            option_attrs={"class" : "btn btn-sm btn-default"},
            choices=[
                ["html", "Actualizar"],
                ["pdf", "Generar archivo PDF"],
            ]
        ),
    )

    def dias(self):
        datos = self.datos(vacios=False)
        retorno = {
            "perfiles" : int(datos["perfiles"]),
            "realizaciones" : int(datos["realizaciones"]),
            "actualizaciones" : int(datos["actualizaciones"]),
            "tiposdeatencion" : int(datos["tiposdeatencion"]),
        }
        return retorno

    def accion(self):
        datos = self.datos(vacios=False)
        return datos["acciones"]
