from django import forms
from django.apps import apps
from django.core.validators import RegexValidator
from .models import Mascota

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
        model = Mascota
        exclude = [ 'baja' ]



class ModificacionModelForm(forms.ModelForm):

    class Meta:
        model = Mascota
        fields = '__all__'
        widgets = {
            'descripcion' : forms.Textarea(attrs={ 'cols':60, 'rows':6 }),
        }



class CreacionForm(forms.Form):

    nombre = forms.CharField(
        required = True,
        label = 'Nombre',
        widget = forms.TextInput,
        help_text="Nombre de la mascota",
        error_messages = {
            'max_length' : "El nombre puede tener a lo sumo {} caracteres".format(Mascota.MAX_NOMBRE),
            'min_length' : "El nombre debe tener por lo menos {} caracteres".format(Mascota.MIN_NOMBRE),
            'required' : "El nombre es obligatorio"
        },
        validators = [
            RegexValidator(
                Mascota.REGEX_NOMBRE,
                message="El nombre debe construirse de numeros, letras, espacios y guiones ('_' y '-')"
            )
		],
        max_length = Mascota.MAX_NOMBRE,
        min_length =  Mascota.MIN_NOMBRE,
    )

    raza = forms.CharField(
        required = False,
        label = 'Descripcion',
        widget = forms.Textarea(attrs={ 'cols':60, 'rows':6 }),
        help_text="Raza de la mascota",
        error_messages={
            'max_length': "El nombre puede tener a lo sumo {} caracteres".format(Mascota.MAX_NOMBRE),
            'min_length': "El nombre debe tener por lo menos {} caracteres".format(Mascota.MIN_NOMBRE),
            'required': "El nombre es obligatorio"
        },
        validators=[
            RegexValidator(
                Mascota.REGEX_NOMBRE,
                message="El nombre debe construirse de numeros, letras, espacios y guiones ('_' y '-')"
            )
        ],
        max_length = Mascota.MAXRAZA,
        min_length = None,
    )
    especie = forms.CharField(
        required=False,
        label='Descripcion',
        widget=forms.Textarea(attrs={'cols': 60, 'rows': 6}),
        help_text="Especie de la mascota",
        error_messages={
            'max_length': "El nombre puede tener a lo sumo {} caracteres".format(Mascota.MAX_NOMBRE),
            'min_length': "El nombre debe tener por lo menos {} caracteres".format(Mascota.MIN_NOMBRE),
            'required': "El nombre es obligatorio"
        },
        validators=[
            RegexValidator(
                Mascota.REGEX_NOMBRE,
                message="El nombre debe construirse de numeros, letras, espacios y guiones ('_' y '-')"
            )
        ],
        max_length=Mascota.MAXESPECIE,
        min_length=None,
    )



    def __init__(self, *args, **kwargs):


        self.field_order = [
            'nombre',
            'raza',
            'especie',

        ]
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class' : 'form-control'
                })


    def crear(self):
        mascota = Mascota.objects.create(

            nombre = self.cleaned_data['nombre'],
            raza = self.cleaned_data['raza'],
            especie= self.cleaned_data['especie'],
		)
        return mascota



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

        return instancia
