from decimal import Decimal
from datetime import datetime, date, time, timedelta

from django import forms
from django.core.validators import MinValueValidator

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



DATE_INPUT_FMTS = ("%d/%m/%y", "%d/%m/%Y")
TIME_INPUT_FMTS = ("%H:%M",)



class NombreModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj.nombre)



class ServicioModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        area = Areas[obj.tipo].nombrePlural.capitalize()
        nombre = str(obj.nombre)
        return "%s: %s" % (area, nombre)



class ProductoModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        nombre = obj.nombre
        compra = obj.precioDeCompra
        venta = obj.precioPorUnidad
        return "%s ($%.2f / $%.2f)" % (nombre, compra, venta)



class ActualizarPracticaBaseForm(forms.Form):

    mascota = NombreModelChoiceField(
        empty_label=None,
        queryset=Mascota.objects.habilitados(),
        widget=forms.Select(attrs={"class" : "form-control"}),
    )

    def __init__(self, practica, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if practica is not None:
            mascotas  = practica.cliente.mascota_set
            self.fields["mascota"].queryset = mascotas.habilitados()



class HorariosBaseForm(forms.Form):

    fecha = forms.DateField(
        input_formats=DATE_INPUT_FMTS,
        label="Fecha de inicio",
        widget=forms.DateInput(
            format=DATE_INPUT_FMTS[0],
            attrs={"class":"form-control"}
        ),
        error_messages={
            "required" : "La fecha de inicio es obligatoria",
            "invalid" : "La fecha debe tener el formato <dia>/<mes>/<año>",
        },
    )

    hora = forms.TimeField(
        input_formats=TIME_INPUT_FMTS,
        label="Hora de inicio",
        widget=forms.TimeInput(
            format=TIME_INPUT_FMTS[0],
            attrs={"class":"form-control"}
        ),
        error_messages={
            "required" : "La hora de inicio es obligatoria",
            "invalid" : "La hora debe tener el formato <horas>:<minutos>",
        },
    )

    duracion = forms.IntegerField(
        min_value=1,
        widget=forms.TextInput(attrs={"class":"form-control"}),
        error_messages={
            "required" : "La duracion es obligatoria",
            "invalid" : "La duracion debe ser un numero entero",
            "min_value" : "La duracion debe ser mayor que cero",
        }
    )

    def datetimeFinalizacion(self):
        inicio = self.datetimeInicio()
        duracion = self.timedeltaDuracion()
        return inicio+duracion

    def datetimeInicio(self):
        inicio = datetime.combine(
            self.cleaned_data["fecha"],
            self.cleaned_data["hora"]
        )
        return inicio

    def timedeltaDuracion(self):
        duracion = self.cleaned_data["duracion"]
        return timedelta(minutes=duracion)



# Practica y estados ##########################################################

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



class ModificarPracticaForm(forms.ModelForm):

    class Meta:
        model = Practica
        fields = [ "mascota" ]
        field_classes = {
            "mascota" : NombreModelChoiceField,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["mascota"].empty_label = None
        self.fields["mascota"].widget.attrs.update({"class" : "form-control"})
        if "instance" in kwargs and kwargs["instance"] is not None:
            mascotas = self.instance.cliente.mascota_set
            self.fields["mascota"].queryset = mascotas.habilitados()



class PresupuestadaForm(forms.Form):

    diasMantenimiento = forms.IntegerField(
        min_value=1,
        label="Dias de Mantenimiento",
        widget=forms.TextInput(attrs={"class":"form-control"}),
        error_messages={
            "required" : "Dias de mantenimiento del presupuesto es obligatorio",
            "invalid" : "La cantidad de dias debe ser un numero entero",
            "min_value" : "La cantidad de dias debe ser mayor que cero",
        }
    )

    @property
    def datos(self):
        datos = {
            "diasMantenimiento" : self.cleaned_data["diasMantenimiento"],
        }

        return datos

    @property
    def accion(self):
        return Practica.Acciones.presupuestar.name



class NuevaPresupuestadaForm(ActualizarPracticaBaseForm, PresupuestadaForm):

    field_order = [ "mascota" ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["mascota"].required = False
        self.fields["mascota"].empty_label = ""



class ProgramadaForm(HorariosBaseForm):

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



class NuevaProgramadaForm(ActualizarPracticaBaseForm, ProgramadaForm):
    field_order = [ "mascota" ]
    def __init__(self, practica, *args, precio=0, **kwargs):
        super().__init__(practica, *args, precio=precio, **kwargs)
        self.precio = precio



class ReprogramadaForm(HorariosBaseForm):

    motivoReprogramacion = forms.CharField(
        label="Motivo de reprogramacion",
        required = False,
        widget = forms.Textarea(attrs={
            "cols":60,
            "rows":3,
            "class":"form-control",
        }),
    )

    def clean(self):
        cleaned = super().clean()

        nuevaFecha = cleaned["fecha"]
        nuevaHora = cleaned["hora"]
        nuevaDuracion = cleaned["duracion"]

        fecha = self.initial["fecha"]
        hora = self.initial["hora"]
        duracion = self.initial["duracion"]

        nuevo = any(
            [ nuevaDuracion!=duracion, nuevaHora!=hora, nuevaFecha!=fecha ]
        )

        if not nuevo:
            raise forms.ValidationError("El nuevo turno no puede ser igual al actual")

        return cleaned

    @property
    def datos(self):
        return {
            "inicio" : self.datetimeInicio(),
            "finalizacion" : self.datetimeFinalizacion(),
            "motivoReprogramacion" : self.cleaned_data["motivoReprogramacion"],
        }

    @property
    def accion(self):
        return Practica.Acciones.reprogramar.name



class RealizadaForm(forms.Form):

    fechaInicio = forms.DateField(
        input_formats=DATE_INPUT_FMTS,
        label="Fecha de inicio",
        widget=forms.DateInput(
            format=DATE_INPUT_FMTS[0],
            attrs={"class":"form-control"}
        ),
        error_messages={
            "required" : "La fecha de inicio es obligatoria",
            "invalid" : "La fecha debe tener el formato <dia>/<mes>/<año>",
        },
    )

    horaInicio = forms.TimeField(
        input_formats=TIME_INPUT_FMTS,
        label="Hora de inicio",
        widget=forms.TimeInput(
            format=TIME_INPUT_FMTS[0],
            attrs={"class":"form-control"}
        ),
        error_messages={
            "required" : "La hora de inicio es obligatoria",
            "invalid" : "La hora debe tener el formato <horas>:<minutos>",
        },
    )

    fechaFinalizacion = forms.DateField(
        input_formats=DATE_INPUT_FMTS,
        label="Fecha de finalizacion",
        widget=forms.DateInput(
            format=DATE_INPUT_FMTS[0],
            attrs={"class":"form-control"}
        ),
        error_messages={
            "required" : "La fecha de finalizacion es obligatoria",
            "invalid" : "La fecha debe tener el formato <dia>/<mes>/<año>",
        },
    )

    horaFinalizacion = forms.TimeField(
        input_formats=TIME_INPUT_FMTS,
        label="Hora de finalizacion",
        widget=forms.TimeInput(
            format=TIME_INPUT_FMTS[0],
            attrs={"class":"form-control"}
        ),
        error_messages={
            "required" : "La hora de finalizacion es obligatoria",
            "invalid" : "La hora debe tener el formato <horas>:<minutos>",
        },
    )

    condicionPreviaMascota = forms.CharField(
        label="Condicion previa de la mascota",
        required = False,
        widget = forms.Textarea(attrs={
            "cols":60,
            "rows":3,
            "class":"form-control",
        })
    )

    resultados = forms.CharField(
        label="Resultados de la practica",
        required = False,
        widget = forms.Textarea(attrs={
            "cols":60,
            "rows":3,
            "class":"form-control",
        }),
    )

    @property
    def datos(self):

        inicio = datetime.combine(
            self.cleaned_data["fechaInicio"],
            self.cleaned_data["horaInicio"]
        )

        finalizacion = datetime.combine(
            self.cleaned_data["fechaFinalizacion"],
            self.cleaned_data["horaFinalizacion"]
        )

        datos = {
            "inicio" : inicio,
            "finalizacion" : finalizacion,
            "condicionPreviaMascota" : self.cleaned_data["condicionPreviaMascota"],
            "resultados" : self.cleaned_data["resultados"],
        }

        return datos

    @property
    def accion(self):
        return Practica.Acciones.realizar.name

    def clean(self):
        datos = self.datos
        if datos["inicio"] >= datos["finalizacion"]:
            raise forms.ValidationError("La fecha y hora de inicio debe ser anterior a la fecha y hora de finalizacion")
        return super().clean()



class NuevaRealizadaForm(ActualizarPracticaBaseForm, RealizadaForm):
    field_order = [ "mascota" ]



class CanceladaForm(forms.Form):

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



class ConfirmarFacturacionForm(forms.Form):

    @property
    def datos(self):
        return {}

    @property
    def accion(self):
        return Practica.Acciones.facturar.name



# Formsets ####################################################################

class BaseFormSet(forms.BaseFormSet):

    id_fields=None
    extra = 0
    can_order = False
    can_delete = False
    min_num = 1
    max_num = 1000
    absolute_max = 2000
    validate_min = True
    validate_max = False

    def __init__(self, *args, label=None, **kwargs):
        super().__init__(*args, **kwargs)
        if label is None:
            label = self.prefix.replace("_"," ").capitalize()
        self.label = label

    def ocurrencias(self, posicion):
        item = self.forms[posicion]
        if not item.is_valid():
            return None
        ocurrencias = []
        valores = tuple( item.cleaned_data[field] for field in self.id_fields )
        for i in range( len(self.forms) ):
            item = self.forms[i]
            if not item.is_valid():
                continue
            iesimo = tuple( item.cleaned_data[field] for field in self.id_fields )
            if iesimo == valores:
                ocurrencias.append(i)
        return ocurrencias

    def _vacios(self, i):
        vacios=[]
        form = self.forms[i]
        for field in self.id_fields:
            if (not field in form.cleaned_data) or (not form.cleaned_data[field]):
                vacios.append(field)
        return vacios

    def _validarIdentidades(self):
        for i in range( len(self.forms) ):
            form = self.forms[i]
            vacios = self._vacios(i)
            if len(vacios):
                self._ignorar_forms.append(i)

    def _validarOcurrencias(self):
        errores = []
        for i in range( len(self.forms) ):
            if (i in self._ignorar_forms):
                continue
            ocurrencias = self.ocurrencias(i)
            if (ocurrencias is not None) and (len(ocurrencias) >= 2):
                self._ignorar_forms.extend(ocurrencias)
                errores.append(forms.ValidationError(
                    "Cada item puede agregarse a lo sumo una vez, revise las filas: %s" % ", ".join([str(x+1) for x in ocurrencias]),
                ))
        return errores

    def clean(self):
        retorno = super().clean()
        # Array con posiciones en self.forms de forms no validos
        self._ignorar_forms = []
        #Valida que cada form tenga completo los campos de identidad
        self._validarIdentidades()
        #Valida que no hayan forms con la misma identidad
        errores = self._validarOcurrencias()
        if len(errores) > 0:
            raise forms.ValidationError(errores)
        return retorno

    @property
    def labeled_forms(self):
        forms = []
        label_format = self.label+" %d"
        for i in range( len(self.forms) ):
            forms.append({
                "label" : label_format % (i+1),
                "form" : self.forms[i]
            })
        return forms



class QuerysetFormSet(BaseFormSet):
    """ Formset para crear, modificar y eliminar objetos de un queryset

        form: subclase de ModelForm a utilizar con cada objeto
        id_fields: iterable con fields del form que determinan la identidad del objeto

        """

    def __init__(self, data=None, *args, queryset=None, **kwargs):
        self.queryset = queryset
        self.fields = tuple(self.form.Meta.fields)
        self.para_agregar = None
        self.para_eliminar = None
        self.para_actualizar = None
        self.para_conservar = None
        if "initial" in kwargs:
            del(kwargs["initial"])
        if data is None and queryset is not None:
            initial = queryset.values(*self.fields)
        else:
            initial = None
        super().__init__(data, *args, initial=initial, **kwargs)

    def comparar(self, o1, o2):
        for field in self.id_fields:
            if getattr(o1, field) != getattr(o2, field):
                return False
        return True

    def actualizar(self, o1, o2):
        cambios=0
        for field in self.fields:
            nuevo = getattr(o2, field)
            if getattr(o1, field) != nuevo:
                setattr(o1, field, nuevo)
                cambios += 1
        return cambios

    def _ubicar(self, list, item):
        ret = -1
        for i in range(len(list)):
            if self.comparar(list[i], item):
                return i
        return ret

    def _clasificar(self):

        if len(self._ignorar_forms):
            return

        enviados = self.instancias
        todos = [ x for x in self.queryset.all() ]

        eliminados   = []
        agregados   = []
        modificados = []
        conservados = []

        for obj in todos:
            i = self._ubicar(enviados, obj)
            if i == -1:
                eliminados.append(obj)
            else:
                if self.actualizar(obj, enviados[i]) > 0:
                    modificados.append(obj)
                else:
                    conservados.append(obj)
                del(enviados[i])
        agregados.extend(enviados)

        self.para_agregar = tuple(agregados)
        self.para_eliminar = tuple(eliminados)
        self.para_actualizar = tuple(modificados)
        self.para_conservar = tuple(conservados)

    @property
    def instancias(self):
        return [ form.instance for form in self.forms ]

    def clean(self):
        retorno = super().clean()
        if self.total_error_count() == 0:
            self._clasificar()
        return retorno

    def save(self):
        update_fields = tuple( field for field in self.fields if field not in self.id_fields )
        for item in self.para_agregar:
            item.save(force_insert=True)
        for item in self.para_actualizar:
            item.save(force_update=True, update_fields=update_fields)
        for item in self.para_eliminar:
            item.delete()



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
            productos = Producto.objects.habilitados().order_by("nombre")
            choices = tuple([
                (
                    producto.pk,
                    "{} (${} / ${})".format(producto.nombre, producto.precioDeCompra, producto.precioPorUnidad)
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
            queryset =  Producto.objects.habilitados().order_by("nombre")
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
                (servicio.pk, str(servicio)) for servicio in Servicio.objects.habilitados().order_by("nombre")
            ])
        self.fields["servicio"].choices = choices



class ConsultaServicioForm(PracticaServicioForm):

    def __init__(self, *args, choices=None, **kwargs):
        if choices is None:
            choices = tuple([
                (servicio.pk, servicio.nombre) for servicio in Servicio.objects.habilitados().filter(tipo=Areas.C.codigo).order_by("nombre")
            ])
        super().__init__(*args, choices=choices, **kwargs)



class CirugiaServicioForm(PracticaServicioForm):

    def __init__(self, *args, choices=None, **kwargs):
        if choices is None:
            choices = tuple([
                (servicio.pk, servicio.nombre) for servicio in Servicio.objects.habilitados().filter(tipo=Areas.Q.codigo).order_by("nombre")
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
        fields = ["cantidad", "servicio", "observaciones"]
        widgets = {
            "servicio" : forms.Select(
                attrs={'class': 'form-control'}
            ),
            "cantidad" : forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            "observaciones" : forms.Textarea(
                attrs={
                    "class" : "form-control",
                    "placeholder" : "Observaciones",
                    "cols" : 60,
                    "rows" : 3,
                }
            )
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
        self.fields["observaciones"].required = False
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

class FiltradoForm(forms.Form):

    estados = (
        (None, "Todos"),
    )

    ordenes = (
        ("d", "Descendente"),
        ("a", "Ascendente"),
    )

    criterios = (
        ("modificacion", "Fecha de ultima modificacion"),
        ("creacion", "Fecha de creacion"),
        ("estado", "Estado"),
        ("cliente", "Cliente"),
    )

    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control"})
    )

    mascota = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control"})
    )

    tipoDeAtencion = forms.CharField(
        required=False,
        label="Tipo de atencion",
        widget=forms.TextInput(attrs={"class":"form-control"})
    )

    desde = forms.DateField(
        required=False,
        input_formats=DATE_INPUT_FMTS,
        label="Desde",
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

    hasta = forms.DateField(
        required=False,
        input_formats=DATE_INPUT_FMTS,
        label="Hasta",
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
        widget=forms.TextInput(attrs={
            "placeholder":"Terminos a buscar...",
            "class":"form-control",
        })
    )

    estado = forms.TypedChoiceField(
        choices=estados,
        coerce=int,
        required=False,
        widget=forms.Select(attrs={"class":"form-control"}),
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

    def __init__(self, *args, choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        if choices is not None:
            self.fields["estado"].choices += tuple(choices)
        hoy = datetime.now().date().strftime(DATE_INPUT_FMTS[0])
        self.fields["desde"].widget.attrs.update({"placeholder" : hoy})
        self.fields["hasta"].widget.attrs.update({"placeholder" : hoy})

    def filtros(self):
        if self.cleaned_data:
            fields = ("cliente", "tipoDeAtencion", "desde", "hasta", "estado")
            datos = { k : self.cleaned_data[k] for k in fields }
            servicios = tuple(self.cleaned_data["servicios"].split())
            datos.update({"servicios" : servicios})
        return datos

    def criterio(self):
        if self.cleaned_data and "segun" in self.cleaned_data:
            return self.cleaned_data["segun"]
        return None

    def ascendente(self):
        if self.cleaned_data and "orden" in self.cleaned_data:
            return (self.cleaned_data["orden"] == "a")
        return None



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



class CreacionForm(forms.Form):

    modificar = forms.BooleanField(
        label="Modificar productos estimados",
        required=False,
    )

    acciones = forms.CharField(
        label="Accion",
        widget=SubmitSelect(
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

    @property
    def accion(self):
        return self.cleaned_data["acciones"]

    @property
    def modificarProductos(self):
        return self.cleaned_data["modificar"]
