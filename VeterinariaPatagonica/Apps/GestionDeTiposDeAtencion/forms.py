from django import forms
from django.apps import apps
from django.core.validators import RegexValidator
from .models import TipoDeAtencion



# Para el argumento input_formats de los TimeField:
TIMEINPUT_FMTS = [ "%H:%M" ]



class TimeTextInput(forms.TextInput):
    """ TextInput para objetos datetime.time """

    def format_value(self, value):
        """
        Si el value del TextInput es un datetime.time,
        mostrarlo segun el primer formato en TIMEINPUT_FMTS
        """
        if value is None:
            return ''

        try:
            ret = value.strftime( TIMEINPUT_FMTS[0] )
        except AttributeError:
            ret = str(value)

        return ret



class TipoDeAtencionForm(forms.ModelForm):
    """ ModelForm para creacion de Tipos de Atencion """


    #---------------------- Form Fields  ----------------------
    nombre = forms.CharField(
        required = True,
        label = 'Nombre',
        widget = forms.TextInput,
        help_text="Nombre del tipo de atencion",
        error_messages = {
            'max_length' : "El nombre puede tener a lo sumo {} caracteres".format(TipoDeAtencion.MAX_NOMBRE),
            'min_length' : "El nombre debe tener por lo menos {} caracteres".format(TipoDeAtencion.MIN_NOMBRE),
            'required' : "El nombre es obligatorio"
        },
        validators = [
            RegexValidator(
                TipoDeAtencion.REGEX_NOMBRE,
                message="El nombre debe construirse de numeros, letras, espacios y guiones ('_' y '-')"
            )
        ],
        max_length = TipoDeAtencion.MAX_NOMBRE,
        min_length =  TipoDeAtencion.MIN_NOMBRE,
    )

    descripcion = forms.CharField(
        required = False,
        label = 'Descripcion',
        widget = forms.Textarea(attrs={ 'cols':60, 'rows':6 }),
        help_text="Descripcion del tipo de atencion",
        error_messages = {},
        validators = [],
        max_length = None,
        min_length = None,
    )

    emergencia = forms.BooleanField(
        required = False,
        label = 'Emergencia',
        widget = forms.CheckboxInput,
        help_text="Determina el grado de urgencia del tipo de atencion",
        error_messages = {},
        validators = [],
    )

    tipoDeServicio = forms.ChoiceField(
        required = True,
        label = 'Tipo de servicio',
        widget = forms.Select,
        help_text='Tipo de servicio',
        error_messages = {
            'invalid_choice' : "La opcion no es valida",
            'required' : "El tipo de servicio es obligatorio"
        },
        validators = [],
        choices = apps.get_model('GestionDeServicios', 'Servicio', require_ready=False).TIPO,
    )

    lugar = forms.ChoiceField(
        required = True,
        label = 'Lugar',
        widget = forms.Select,
        help_text="Lugar en donde se realiza el tipo de atencion",
        error_messages = {
            'invalid_choice' : "La opcion no es valida",
            'required' : "El lugar de atencion es obligatorio"
        },
        validators = [],
        choices = TipoDeAtencion.LUGARES_DE_ATENCION,
    )

    inicioFranjaHoraria = forms.TimeField(
        required = True,
        label = 'Inicio horario de atencion',
        widget = TimeTextInput,
        help_text='Hora de inicio del tipo de atencion',
        error_messages = {
            'invalid' : 'El formato debe ser HH:MM, por ejemplo "01:23"',
            'required' : 'El inicio de horario de atencion es obligatorio'
        },
        validators = [],
        input_formats = TIMEINPUT_FMTS,
    )

    finFranjaHoraria = forms.TimeField(
        required = True,
        label = 'Fin horario de atencion',
        widget = TimeTextInput,
        help_text='Hora de finalizacion del tipo de atencion',
        error_messages = {
            'invalid' : 'El formato debe ser HH:MM, por ejemplo "01:23"',
            'required' : 'El inicio de horario de atencion es obligatorio'
        },
        validators = [],
        input_formats = TIMEINPUT_FMTS,
    )

    recargo = forms.DecimalField(
        required = True,
        label = 'Recargo',
        widget = forms.NumberInput,
        help_text="Porcentaje de recargo sobre el costo del servicio a aplicar",
        error_messages = {
            "required" : "El recargo es obligatorio",
            "invalid" : "Debe ingresar un valor entero o decimal, ejemplo: 100 ó 99,9",
            "min_value" : ("Debe ingresar un valor no menor que {:.%df}" % (TipoDeAtencion.RECARGO_PARTE_DECIMAL)).format(TipoDeAtencion.RECARGO_MIN_VALUE),
            "max_value" : ("Debe ingresar un valor no mayor que {:.%df}" % (TipoDeAtencion.RECARGO_PARTE_DECIMAL)).format(TipoDeAtencion.RECARGO_MAX_VALUE),
            "max_digits" : "Debe ingresar a lo sumo %d digitos para la parte entera" % (TipoDeAtencion.RECARGO_PARTE_ENTERA),
            "max_decimal_places" : "Debe ingresar a lo sumo %d digitos para la parte decimal" % (TipoDeAtencion.RECARGO_PARTE_DECIMAL),
            "max_whole_digits" : "Debe ingresar a lo sumo %d digitos en total" % (TipoDeAtencion.RECARGO_PARTE_DECIMAL+TipoDeAtencion.RECARGO_PARTE_ENTERA),
        },
        max_value=TipoDeAtencion.RECARGO_MAX_VALUE,
        min_value=TipoDeAtencion.RECARGO_MIN_VALUE,
        max_digits=TipoDeAtencion.RECARGO_PARTE_ENTERA+TipoDeAtencion.RECARGO_PARTE_DECIMAL,
        decimal_places=TipoDeAtencion.RECARGO_PARTE_DECIMAL,
        validators = [],
    )



    #---------------------- Orden de los Fields  ----------------------
    field_order = [
        'nombre',
        'descripcion',
        'tipoDeServicio',
        'lugar',
        'emergencia',
        'inicioFranjaHoraria',
        'finFranjaHoraria',
        'recargo'
    ]



    #---------------------- Modelo del ModelForm ----------------------
    class Meta:
        model = TipoDeAtencion
        exclude = [ 'baja' ]



    #----------------------Constructor ----------------------
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        #[TODO] Averiguar una mejor manera de hacer esto:
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class' : 'form-control'
                })


"""
class ModificacionForm(CreacionForm):
    #ModelForm para modificacion de Tipos de Atencion

    baja = forms.BooleanField(
        required = False,
        label = 'Deshabilitado',
        widget = forms.CheckboxInput,
        help_text='Deshabilitado',
        error_messages = {},
        validators = [],
    )

    class Meta:
        model = TipoDeAtencion
        fields = '__all__'
"""