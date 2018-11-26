from django import forms
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator, DecimalValidator

from .models import TipoDeAtencion
from VeterinariaPatagonica.areas import Areas



# Para el argumento input_formats de los TimeField:
TIME_INPUT_FMTS = [ "%H:%M" ]



class TipoDeAtencionForm(forms.ModelForm):
    """ ModelForm para tipos de atencion """

    class Meta:

        model = TipoDeAtencion

        fields = [
            "nombre",
            "descripcion",
            "tipoDeServicio",
            "lugar",
            "emergencia",
            "inicioFranjaHoraria",
            "finFranjaHoraria",
            "recargo"
        ]

        labels = {
            "tipoDeServicio" : "Tipo de servicio",
            "inicioFranjaHoraria" : "Inicio de franja horaria",
            "finFranjaHoraria" : "Fin de franja horaria",
        }

        error_messages = {
            "nombre" : {
                "max_length" : "El nombre puede tener a lo sumo {} caracteres".format(TipoDeAtencion.MAX_NOMBRE),
                "min_length" : "El nombre debe tener por lo menos {} caracteres".format(TipoDeAtencion.MIN_NOMBRE),
                "required" : "El nombre es obligatorio"
            },
            "tipoDeServicio" : {
                "invalid_choice" : "Tipo de servicio no valido",
                "required" : "El tipo de servicio es obligatorio"
            },
            "lugar" : {
                "invalid_choice" : "Lugar de atencion no valido",
                "required" : "El lugar de atencion es obligatorio"
            },
            "inicioFranjaHoraria" : {
                "invalid" : "El formato debe ser <horas>:<minutos>, por ejemplo 01:23",
                "required" : "El inicio de horario de atencion es obligatorio"
            },
            "finFranjaHoraria" : {
                "invalid" : "El formato debe ser <horas>:<minutos>, por ejemplo 01:23",
                "required" : "El fin de horario de atencion es obligatorio"
            },
            "recargo" : {
                "required" : "El recargo es obligatorio",
                "invalid" : "Debe ingresar un valor entero o decimal, ejemplo: 100 o 99,9",
                "min_value" : ("Debe ingresar un valor no menor que {:.%df}" % (TipoDeAtencion.RECARGO_PARTE_DECIMAL)).format(TipoDeAtencion.RECARGO_MIN_VALUE),
                "max_value" : ("Debe ingresar un valor no mayor que {:.%df}" % (TipoDeAtencion.RECARGO_PARTE_DECIMAL)).format(TipoDeAtencion.RECARGO_MAX_VALUE),
                "max_digits" : "Debe ingresar a lo sumo %d digitos para la parte entera" % (TipoDeAtencion.RECARGO_PARTE_ENTERA),
                "max_decimal_places" : "Debe ingresar a lo sumo %d digitos para la parte decimal" % (TipoDeAtencion.RECARGO_PARTE_DECIMAL),
                "max_whole_digits" : "Debe ingresar a lo sumo %d digitos en total" % (TipoDeAtencion.RECARGO_PARTE_DECIMAL+TipoDeAtencion.RECARGO_PARTE_ENTERA),
            }
        }

        widgets = {
            "descripcion" : forms.Textarea,
            "inicioFranjaHoraria" : forms.TimeInput,
            "finFranjaHoraria" : forms.TimeInput,
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["descripcion"].required = False
        self.fields["emergencia"].required = False
        self.fields["nombre"].validators.insert(0,
            RegexValidator(
                TipoDeAtencion.REGEX_NOMBRE,
                message="El nombre puede tener numeros, letras, espacios y guiones"
            )
        )
        self.fields["recargo"].validators.extend([
            MaxValueValidator(
                TipoDeAtencion.RECARGO_MAX_VALUE
            ),
            MinValueValidator(
                TipoDeAtencion.RECARGO_MIN_VALUE
            ),
            DecimalValidator(
                TipoDeAtencion.RECARGO_PARTE_ENTERA+TipoDeAtencion.RECARGO_PARTE_DECIMAL,
                TipoDeAtencion.RECARGO_PARTE_DECIMAL
            )
        ])

        self.fields["inicioFranjaHoraria"].input_formats = TIME_INPUT_FMTS
        self.fields["finFranjaHoraria"].input_formats = TIME_INPUT_FMTS
        self.fields["inicioFranjaHoraria"].widget.format = TIME_INPUT_FMTS[0]
        self.fields["finFranjaHoraria"].widget.format = TIME_INPUT_FMTS[0]

        self.fields["tipoDeServicio"].choices = Areas.choices()
        self.fields["lugar"].choices = TipoDeAtencion.LUGARES_DE_ATENCION

        self.fields["nombre"].widget.attrs.update({ "class" : "form-control" })
        self.fields["descripcion"].widget.attrs.update({ "class" : "form-control", "cols" : 60, "rows" : 4 })
        self.fields["tipoDeServicio"].widget.attrs.update({ "class" : "form-control" })
        self.fields["lugar"].widget.attrs.update({ "class" : "form-control" })
        self.fields["inicioFranjaHoraria"].widget.attrs.update({ "class" : "form-control" })
        self.fields["finFranjaHoraria"].widget.attrs.update({ "class" : "form-control" })
        self.fields["recargo"].widget.attrs.update({ "class" : "form-control" })
