from django import forms
from django.apps import apps
from django.core.validators import RegexValidator
from .models import TipoDeAtencion



TIMEINPUT_FMTS = [ "%H:%M" ]



class TimeTextInput(forms.TextInput):

    def format_value(self, value):

        if value is None:
            return ''

        try:
            ret = value.strftime( TIMEINPUT_FMTS[0] )
        except AttributeError:
            ret = str(value)

        return ret



class CreacionModelForm(forms.ModelForm):

    class Meta:
        model = TipoDeAtencion
        exclude = [ 'baja' ]



class ModificacionModelForm(forms.ModelForm):

    class Meta:
        model = TipoDeAtencion
        fields = '__all__'
        widgets = {
            'descripcion' : forms.Textarea(attrs={ 'cols':60, 'rows':6 }),
        }



class CreacionForm(forms.Form):

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

    tipo_de_servicio = forms.ChoiceField(
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

    inicio_franja_horaria = forms.TimeField(
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

    fin_franja_horaria = forms.TimeField(
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

    recargo = forms.FloatField(
        required = True,
        label = 'Recargo',
        widget = forms.NumberInput,
        help_text="Porcentaje de recargo sobre el costo del servicio a aplicar",
        error_messages = {
            'required' : 'El recargo es obligatorio',
            'invalid' : 'Debe ingresar un valor entero o decimal, ejemplo: "100" ó "99,9"',
            'max_value' : 'Debe ingresar un valor no mayor al 100%',
            'min_value' : 'Debe ingresar un valor no menor que el 0%'
        },
        validators = [],
        max_value = 100,
        min_value = 0,
    )

    def __init__(self, *args, **kwargs):

        self.field_order = [
            'nombre',
            'descripcion',
            'tipo_de_servicio',
            'lugar',
            'emergencia',
            'inicio_franja_horaria',
            'fin_franja_horaria',
            'recargo'
        ]

        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class' : 'form-control'
                })


    def crear(self):
        tda = TipoDeAtencion.objects.create(

            nombre = self.cleaned_data['nombre'],
            descripcion = self.cleaned_data['descripcion'],
            emergencia = self.cleaned_data['emergencia'],
            recargo = self.cleaned_data['recargo'],
            lugar = self.cleaned_data['lugar'],
            tipo_de_servicio = self.cleaned_data['tipo_de_servicio'],
            inicio_franja_horaria = self.cleaned_data['inicio_franja_horaria'],
            fin_franja_horaria = self.cleaned_data['fin_franja_horaria']
		)

        return tda



class ModificacionForm(CreacionForm):

    baja = forms.BooleanField(
        required = False,
        label = 'Deshabilitado',
        widget = forms.CheckboxInput,
        help_text='Habilitar o deshabilitar el tipo de atencion',
        error_messages = {},
        validators = [],
    )

    def cargar(self, instancia):

        instancia.nombre = self.cleaned_data['nombre']
        instancia.descripcion = self.cleaned_data['descripcion']
        instancia.emergencia = self.cleaned_data['emergencia']
        instancia.baja = self.cleaned_data['baja']
        instancia.recargo = self.cleaned_data['recargo']
        instancia.lugar = self.cleaned_data['lugar']
        instancia.tipo_de_servicio = self.cleaned_data['tipo_de_servicio']
        instancia.inicio_franja_horaria = self.cleaned_data['inicio_franja_horaria']
        instancia.fin_franja_horaria = self.cleaned_data['fin_franja_horaria']

        return instancia
