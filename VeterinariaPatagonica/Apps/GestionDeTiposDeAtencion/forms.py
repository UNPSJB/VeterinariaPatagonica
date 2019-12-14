from django import forms
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator, DecimalValidator

from .models import TipoDeAtencion
from VeterinariaPatagonica.areas import Areas
from VeterinariaPatagonica.forms import BaseForm



TIME_INPUT_FMTS = [ "%H:%M" ]
DATETIME_INPUT_FMTS = ("%d/%m/%y %H:%M", "%d/%m/%Y %H:%M")
DATE_INPUT_FMTS = ("%d/%m/%y", "%d/%m/%Y")



class TipoDeAtencionForm(forms.ModelForm):

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
                "max_length" : "El nombre puede tener a lo sumo %d caracteres" % TipoDeAtencion.MAX_NOMBRE,
                "min_length" : "El nombre debe tener por lo menos %d caracteres" % TipoDeAtencion.MIN_NOMBRE,
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
                "invalid" : "El formato debe ser <horas>:<minutos>",
                "required" : "El inicio de horario de atencion es obligatorio"
            },
            "finFranjaHoraria" : {
                "invalid" : "El formato debe ser <horas>:<minutos>",
                "required" : "El fin de horario de atencion es obligatorio"
            },
            "recargo" : {
                "required" : "El recargo es obligatorio",
                "invalid" : "El valor ingresado no es válido, debe ingresar un valor numérico",
                "min_value" : ("Debe ingresar un valor no menor que {:.%df}" % (TipoDeAtencion.RECARGO_PARTE_DECIMAL)).format(TipoDeAtencion.RECARGO_MIN_VALUE),
                "max_value" : ("Debe ingresar un valor no mayor que {:.%df}" % (TipoDeAtencion.RECARGO_PARTE_DECIMAL)).format(TipoDeAtencion.RECARGO_MAX_VALUE),
                "max_digits" : "Debe ingresar a lo sumo %d digitos para la parte entera" % (TipoDeAtencion.RECARGO_PARTE_ENTERA),
                "max_decimal_places" : "Debe ingresar a lo sumo %d digitos para la parte decimal" % (TipoDeAtencion.RECARGO_PARTE_DECIMAL),
                "max_whole_digits" : "Debe ingresar a lo sumo %d digitos en total" % (TipoDeAtencion.RECARGO_PARTE_DECIMAL+TipoDeAtencion.RECARGO_PARTE_ENTERA),
            }
        }
        help_texts = {
            "nombre" : "Debe ingresar un nombre para identificar al tipo de atención, se permiten numeros, letras, espacios, guiones y puntos.",
            "descripcion" : "Puede agregar una descripción acerca de cuando debería asignarse este tipo de atención.",
            "tipoDeServicio" : "Aclare a que tipo de servicio se refiere.",
            "lugar" : "Indique el lugar donde se atendio o atendera al paciente.",
            "emergencia" : "Active la casilla de verificación si la atención se considera de emergencia.",
            "inicioFranjaHoraria" : "Indique desde que hora del dia es válido este tipo de atención.",
            "finFranjaHoraria" : "Indique hasta que hora del dia es válido este tipo de atención.",
            "recargo" : "Defina el porcentaje de recargo a aplicar a prácticas con este tipo de atención. El recargo no puede ser negativo y se aceptan hasta dos cifras decimales."
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
                message="El nombre puede tener numeros, letras, espacios, guiones y puntos."
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

        self.fields["tipoDeServicio"].choices = Areas.paresOrdenados()
        self.fields["lugar"].choices = TipoDeAtencion.LUGARES_DE_ATENCION

        self.fields["nombre"].widget.attrs.update({ "class" : "form-control" })
        self.fields["descripcion"].widget.attrs.update({ "class" : "form-control", "cols" : 60, "rows" : 4 })
        self.fields["tipoDeServicio"].widget.attrs.update({ "class" : "form-control" })
        self.fields["lugar"].widget.attrs.update({ "class" : "form-control" })
        self.fields["inicioFranjaHoraria"].widget.attrs.update({ "class" : "form-control" })
        self.fields["finFranjaHoraria"].widget.attrs.update({ "class" : "form-control" })
        self.fields["recargo"].widget.attrs.update({ "class" : "form-control" })



class ModificacionTipoDeAtencionForm(forms.ModelForm):

    class Meta:
        model = TipoDeAtencion
        fields = [
            "nombre",
            "descripcion",
        ]
        error_messages = {
            "nombre" : {
                "max_length" : "El nombre puede tener a lo sumo %d caracteres" % TipoDeAtencion.MAX_NOMBRE,
                "min_length" : "El nombre debe tener por lo menos %d caracteres" % TipoDeAtencion.MIN_NOMBRE,
                "required" : "El nombre es obligatorio"
            },
        }
        help_texts = {
            "nombre" : "Debe ingresar un nombre para identificar al tipo de atención, se permiten numeros, letras, espacios, guiones y puntos.",
            "descripcion" : "Puede agregar una descripción acerca de cuando debería asignarse este tipo de atención.",
        }
        widgets = {
            "descripcion" : forms.Textarea,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["descripcion"].required = False
        self.fields["nombre"].validators.insert(0,
            RegexValidator(
                TipoDeAtencion.REGEX_NOMBRE,
                message="El nombre puede tener numeros, letras, espacios, guiones y puntos."
            )
        )
        self.fields["nombre"].widget.attrs.update({ "class" : "form-control" })
        self.fields["descripcion"].widget.attrs.update({ "class" : "form-control", "cols" : 60, "rows" : 4 })



class FiltradoForm(BaseForm):

    nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class":"form-control", "placeholder" : "Nombre"})
    )

    lugar = forms.ChoiceField(
        required=False,
        choices=[("", "Lugar: cualquiera")] + [
            (tda[0], "Lugar: "+tda[1].lower()) for tda in TipoDeAtencion.LUGARES_DE_ATENCION
        ],
    )

    emergencia = forms.ChoiceField(
        required=False,
        choices=[
            ("", "Emergencia: cualquiera"),
            ("s", "Emergencia: si"),
            ("n", "Emergencia: no"),
        ],
    )

    desde = forms.TimeField(
        required=False,
        input_formats=TIME_INPUT_FMTS,
        label="Hora de inicio",
        widget=forms.TimeInput(
            format=TIME_INPUT_FMTS[0],
            attrs={
                "class":"form-control",
                "placeholder":"Desde",
            },
        ),
        error_messages={
            "invalid" : "Hora de inicio debe tener el formato <horas>:<minutos>",
        },
    )

    hasta = forms.TimeField(
        required=False,
        input_formats=TIME_INPUT_FMTS,
        label="Hora de finalizacion",
        widget=forms.TimeInput(
            format=TIME_INPUT_FMTS[0],
            attrs={
                "class":"form-control",
                "placeholder":"Hasta",
            },
        ),
        error_messages={
            "invalid" : "Hora de finalizacion debe tener el formato <horas>:<minutos>",
        },
    )

    def filtros(self):

        retorno = self.datosCumplen(bool)

        if "emergencia" in retorno:
            retorno["emergencia"] = (retorno["emergencia"] == "s")

        if "desde" in retorno and "hasta" in retorno:
            if retorno["desde"] > retorno["hasta"]:
                retorno["desdehasta"] = [ retorno["desde"], retorno["hasta"] ]
                del retorno["desde"]
                del retorno["hasta"]

        return retorno
