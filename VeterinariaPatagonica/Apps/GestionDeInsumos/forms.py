from django import forms
from django.apps import apps
from django.core.validators import RegexValidator
from .models import Insumo


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
        model = Insumo
        exclude = [ 'baja' ]


class ModificacionModelForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = '__all__'
        widgets = {
            'descripcion' : forms.Textarea(attrs={ 'cols':60, 'rows':6 }),#Ver valores.
        }


class CreacionForm(forms.Form):
    nombre = forms.CharField(
        max_length = Insumo.MAX_NOMBRE,
        required = True,
        label = 'Nombre',
        widget = forms.TextInput,
        help_text="Nombre del insumo",
        error_messages = {
            'max_length' : "El nombre puede tener a lo sumo {} caracteres".format(Insumo.MAX_NOMBRE),
            'required' : "El nombre es obligatorio"
        },
        validators = [
            RegexValidator(
                Insumo.REGEX_NOMBRE,
                message="El nombre debe construirse de numeros, letras, espacios o guiones ('_' y '-')"
                )
		]
    )
    formaDePresentacion = forms.ChoiceField(
        choices = Insumo.UNIDADES,
        error_messages = {
            'invalid_choice' : "Opcion invalida",
            'blank' : "La unidad de medida es obligatoria"
        }
    )
    precioPorUnidad = forms.DecimalField(
        max_digits = Insumo.MAX_DIGITOS,
        decimal_places = Insumo.MAX_DECIMALES,
        error_messages = {
            'max_digits' : "Cantidad de digitos invalida"
        }
    )
    rubro = forms.CharField(
        help_text="Nombre del rubro al que pertenece",
        max_length = Insumo.MAX_NOMBRE,
        error_messages = {
            'blank' : "El rubro es obligatorio"
        }
    )

    def __init__(self, *args, **kwargs):

        self.field_order = [
            'nombre',
            'formaDePresentacion',
            'precioPorUnidad',
            'rubro'
        ]


        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class' : 'form-control'
                })


    def crear(self):
        insumo = Insumo.objects.create(

            nombre = self.cleaned_data['nombre'],
            formaDePresentacion = self.cleaned_data['formaDePresentacion'],
            precioPorUnidad = self.cleaned_data['precioPorUnidad'],
            rubro = self.cleaned_data['rubro']
		)

        return insumo


class ModificacionForm(CreacionForm):

    baja = forms.BooleanField(
        required = False,
        label = 'Deshabilitado',
        widget = forms.CheckboxInput,
        help_text='Habilitar o deshabilitar el insumo',
        error_messages = {},
        validators = [],
    )

    def cargar(self, instancia):

        instancia.nombre = self.cleaned_data['nombre']
        instancia.formaDePresentacion = self.cleaned_data['formaDePresentacion']
        instancia.precioPorUnidad = self.cleaned_data['precioPorUnidad']
        instancia.rubro = self.cleaned_data['rubro']
        instancia.baja = self.cleaned_data['baja']

        return instancia
