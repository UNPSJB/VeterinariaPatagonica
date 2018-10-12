from django import forms
from .models import Practica
from django.core.validators import RegexValidator
#from localflavor.ar import forms as lforms #Lo comento porque me pincha [Matias]


'''class creacionModelForm(forms.ModelForm):
    class meta:
        model = Cliente'''

class PracticaForm(forms.ModelForm):
    class Meta:
        model = Practica

        fields = [ 'nombre',
                    'precio',
                    'cliente',
                    'servicios',
                    'insumosReales',
                    'tipoDeAtencion',
                    ]

        labels = {
            'nombre':'Nombre.',
            'precio':'Precio.',
            'cliente':'Cliente.',
            'servicios':'Servicios',
            'insumosReales':'Insumos Reales.',
            'tipoDeAtencion':'Tipo De Atención.',
            }

        error_messages = {
            'nombres' : {
                'max_length': ("Nombres demasiados largos"),
            },
            'precio' : {
                'min_value' : 'Debe ingresar un valor no menor que el 0%'
            },
        }

        widgets = {
            'nombre' : forms.TextInput(),
            'precio' : forms.TextInput(),
            'cliente': forms.TextInput(),
            'servicios' : forms.TextInput(),
            'insumosReales': forms.TextInput(),
            'tipoDeAtencion': forms.TextInput(),
        }
'''
    def clean_dniCuit(self):
        dato = self.data["dniCuit"]
        try:
            return lforms.ARDNIField().clean(dato)
        except forms.ValidationError:
            pass

        return lforms.ARCUITField().clean(dato)


    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
'''








'''





from django import forms
from django.apps import apps
from django.core.validators import RegexValidator
from .models import Practica


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
        model = Practica
        exclude = [ 'baja' ]

class ModificacionModelForm(forms.ModelForm):
    class Meta:
        model = Practica
        fields = '__all__'
        widgets = {
            'descripcion' : forms.Textarea(attrs={ 'cols':60, 'rows':6 }),#Ver valores.
        }

class CreacionForm(forms.Form):
    nombre = forms.CharField(
        max_length = Practica.MAX_NOMBRE,
        required = True,
        label = 'Nombre.',
        widget = forms.TextInput,
        help_text="Nombre del insumo",
        error_messages = {
            'max_length' : "El nombre puede tener a lo sumo {} caracteres".format(Practica.MAX_NOMBRE),
            'required' : "El nombre es obligatorio"
        },
        validators = [
            RegexValidator(
                Practica.REGEX_NOMBRE,
                message="El nombre debe construirse de numeros, letras, espacios o guiones ('_' y '-')"
                )]
    )
    precio = forms.DecimalField(
            label = 'Precio Total.',
            max_digits = Practica.MAX_DIGITOS,
            decimal_places = Practica.MAX_DECIMALES,
            error_messages = {
                'max_digits' : "Cantidad de digitos inválida."
            })
    #cliente.
    #servicios.
    #insumosReales.
    #tipoDeAtención.


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
'''
