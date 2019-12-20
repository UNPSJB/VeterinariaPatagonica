from datetime import timedelta

from django import forms

from VeterinariaPatagonica.widgets import SubmitChoices, SubmitButtons


class PaginacionSubmitButtons(SubmitButtons):
    selected_attribute = {"disabled": True}


class LoginForm(forms.Form):

    usuario = forms.CharField(
        required=True,
        label = "Usuario",
        widget = forms.TextInput(attrs={
            "class": "form-control",
            "placeholder" : "Usuario"
        }),
        help_text="Nombre de usuario para iniciar sesion"
    )

    password = forms.CharField(
        required=True,
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class" : "form-control",
            "placeholder" : "Contraseña"
        }),
        help_text="Contraseña de usuario"
    )


class BaseForm(forms.Form):

    _datos = None

    def suprimirErrores(self, campo, codigos):
        suprimir = []
        encontrados = 0
        if campo in self.errors:
            errores = self.errors[campo].as_data()
            for error in errores:
                if error.code in codigos:
                    suprimir.append(error)
                    encontrados += 1
            if encontrados:
                for error in suprimir:
                    errores.remove(error)
                if not len(errores):
                    del(self.errors[campo])
        return encontrados


    def datos(self, vacios=True):
        if self._datos is None:
            self._datos = {}
            default = []
            if not self.is_bound:
                if not vacios:
                    default.extend(self.fields.keys())
                else:
                    for nombre, campo in self.fields.items():
                        if campo.required:
                            default.append(nombre)
                        else:
                            self._datos[nombre] = campo.empty_values[0]
            else:
                if not self.is_valid():
                    for nombre in self.fields.keys():
                        if nombre not in self.cleaned_data:
                            default.append(nombre)

                if not vacios:
                    for nombre, valor in self.cleaned_data.items():
                        if valor in self.fields[nombre].empty_values:
                            default.append(nombre)
                        else:
                            self._datos[nombre] = valor
                else:
                    self._datos.update(self.cleaned_data)
            for nombre in default:
                self._datos[nombre] = self.get_initial_for_field(
                    self.fields[nombre],
                    nombre
                )
        return self._datos

    def datosCumplen(self, funcion):
        return {
            campo:valor for campo, valor in self.datos().items() if funcion(valor)
        }


class SeleccionForm(BaseForm):

    def clean(self):
        data = super().clean()
        suprimidos = self.suprimirErrores(
            "seleccionados",
            ["invalid_choice", "invalid_list"]
        )
        if suprimidos:
            self.add_error(
                None,
                forms.ValidationError("Algunos datos del formulario no eran válidos y se adoptaron valores por defecto.")
            )
        return data

    seleccionados = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        error_messages={
            "required" : "El listado debe tener algun campo visible",
        }
    )

    def __init__(self, *args, campos=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["seleccionados"].choices = [
            (nombre, etiqueta) for nombre, etiqueta in campos
        ]


class OrdenForm(BaseForm):

    def clean(self):
        data = super().clean()
        suprimidos = 0
        for campo in self.fields:
            suprimidos += self.suprimirErrores(
                campo,
                ["invalid", "invalid_choice"]
            )
        if suprimidos:
            self.add_error(
                None,
                forms.ValidationError("Algunos datos del formulario no eran válidos y se adoptaron valores por defecto.")
            )
        return data

    def __init__(self, *args, campos=(), choices=None, **kwargs):
        super().__init__(*args, **kwargs)

        for pos, (nombre, etiqueta) in enumerate(campos, start=len(campos)+1):
            self.fields[nombre] = forms.IntegerField(
                required=False,
                widget = forms.HiddenInput(),
                label = etiqueta,
                initial = pos
            )
        if choices is None:
            self.fields["ordenar"] = forms.CharField(
                required=False,
                widget = forms.HiddenInput(),
            )
        else:
            self.fields["ordenar"] = forms.ChoiceField(
                required=False,
                widget = SubmitChoices(
                    selected_class="activo",
                    option_attrs={"class" : "btn btn-sm btn-default encabezado"}
                ),
                choices=choices,
            )


class PaginacionForm(BaseForm):

    def clean(self):
        data = super().clean()
        suprimidos = 0
        for campo in self.fields:
            suprimidos += self.suprimirErrores(
                campo,
                ["invalid", "min_value"]
            )
        if suprimidos:
            self.add_error(
                None,
                forms.ValidationError("Algunos datos del formulario no eran válidos y se adoptaron valores por defecto.")
            )
        return data

    pagina_actual = forms.IntegerField(
        required=False,
        min_value=1,
        initial=1,
        widget = forms.HiddenInput()
    )

    cantidad = forms.IntegerField(
        required=False,
        min_value=0,
        initial=10,
        widget = forms.NumberInput(
            attrs={"class" : "form-control"},
        ),
    )

    def __init__(self, *args, choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        if choices is None:
            self.fields["pagina"] = forms.IntegerField(
                required=False,
                min_value=1,
                widget = forms.HiddenInput(),
            )
        elif choices:
            self.fields["pagina"] = forms.ChoiceField(
                required=False,
                widget = PaginacionSubmitButtons(
                    selected_class="activo",
                    option_attrs={"class" : "btn btn-sm btn-default"},
                ),
                choices=choices
            )


class ExportarForm(forms.Form):

    prefix="exportacion"

    acciones = forms.CharField(
        required=False,
        label="",
        widget=SubmitButtons(
            option_attrs={"class" : "btn btn-sm btn-default"},
            choices=(
                ("exportar_pagina", "Exportar página"),
                ("exportar_todos", "Exportar todos"),
            )
        ),
    )

    def accion(self):
        if self.is_valid():
            retorno = self.cleaned_data["acciones"]
        else:
            retorno = ""
        return retorno


class BaseFormSet(forms.BaseFormSet):

    id_fields=None
    ignorar_incompletos = False
    extra = 0
    can_order = False
    can_delete = False
    min_num = 1
    max_num = 1000
    absolute_max = 2000
    validate_min = True
    validate_max = True

    def __init__(self, *args, label=None, **kwargs):
        super().__init__(*args, **kwargs)
        if label is None:
            label = self.prefix.replace("_"," ").capitalize()
        self.label = label
        self._ignorar_forms = []

    def ocurrencias(self, posicion):
        item = self.forms[posicion]
        if not item.is_valid():
            return None
        ocurrencias = []
        valores = self._datosId(item.cleaned_data)
        for i in range(len(self.forms)):
            item = self.forms[i]
            if not item.is_valid() or i in self._ignorar_forms:
                continue
            iesimo = self._datosId(item.cleaned_data)
            if iesimo == valores:
                ocurrencias.append(i)
        return ocurrencias

    def _datosId(self, cleaned_data):
        return tuple(cleaned_data[field] for field in self.id_fields)

    def _vacios(self, i):
        vacios=[]
        form = self.forms[i]
        for field in self.id_fields:
            if field not in form.cleaned_data:
                vacios.append(field)
            else:
                vacio = form.cleaned_data[field] in form.fields[field].empty_values
                if vacio:
                    vacios.append(field)
        return vacios

    def _validarIdentidades(self):
        errores = []
        for i in range(len(self.forms)):
            form = self.forms[i]
            vacios = self._vacios(i)
            if len(vacios):
                self._ignorar_forms.append(i)
                if not self.ignorar_incompletos:
                    errores.append(forms.ValidationError(
                        "%s de la fila %d: sin completar" % (", ".join(vacios).capitalize(), i+1),
                    ))
        return errores

    def _validarOcurrencias(self):
        errores = []
        for i in range(len(self.forms)):
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
        errores = []
        errores.extend( self._validarIdentidades() )
        errores.extend( self._validarOcurrencias() )
        if len(errores) > 0:
            raise forms.ValidationError(errores)
        return retorno

    def completos(self):
        return [
            self.forms[i].cleaned_data for i in range(len(self.forms)) if not i in self._ignorar_forms
        ]

    def labeled_forms(self):
        forms = []
        label_format = self.label+" %d"
        for i in range(len(self.forms)):
            forms.append({
                "label" : label_format % (i+1),
                "form" : self.forms[i]
            })
        return forms

    def equivale(self, datos):
        retorno = None
        if self.is_valid():
            datosCompletos = self.completos()
            if len(datos) != len(datosCompletos):
                retorno = False
            else:
                idsCompletos = [self._datosId(completo) for completo in datosCompletos]
                retorno = True
                for dato in datos:
                    id = self._datosId(dato)
                    try:
                        i = idsCompletos.index(id)
                    except ValueError:
                        retorno = False
                    else:
                        if datosCompletos[i] != dato:
                            retorno = False
                    if not retorno:
                        break
        return retorno


class QuerysetFormSet(BaseFormSet):

    def __init__(self, data=None, *args, queryset=None, **kwargs):
        self.queryset = queryset
        self.fields = tuple(self.form.Meta.fields)
        self.para_agregar = None
        self.para_eliminar = None
        self.para_actualizar = None
        self.para_conservar = None
        self._instancias = None
        if "initial" in kwargs:
            del(kwargs["initial"])
        if queryset is not None:
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
        enviados = self.instancias()
        todos = [ x for x in self.queryset.all() ]
        eliminados  = []
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
        self.para_agregar = agregados
        self.para_eliminar = eliminados
        self.para_actualizar = modificados
        self.para_conservar = conservados

    def instancias(self):
        retorno = []
        for i in range(len(self.forms)):
            if i not in self._ignorar_forms:
                retorno.append(self.forms[i].instance)
        return retorno

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


class DesdeHastaForm(BaseForm):

    DATETIME_INPUT_FMTS = ("%d/%m/%y %H:%M", "%d/%m/%Y %H:%M")
    DATE_INPUT_FMTS = ("%d/%m/%y", "%d/%m/%Y")
    TIME_INPUT_FMTS = ("%H:%M",)

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

    def __init__(self, *args, unidadDuracion="minutes", minimo=None, maximo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.unidadDuracion = unidadDuracion
        self.minimo = minimo
        if self.minimo is not None:
            if self.minimo.second + self.minimo.microsecond > 0:
                self.minimo = self.minimo.replace(second=0, microsecond=0)+timedelta(minutes=1)
        self.maximo = maximo
        if self.maximo is not None:
            self.maximo = self.maximo.replace(second=0, microsecond=0)
            if self.minimo is not None and self.maximo < self.minimo:
                self.maximo = self.minimo

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

    def datetimeInicio(self):
        retorno = None
        if self.is_valid():
            retorno = self.cleaned_data["desde"]
        return retorno

    def datetimeFinalizacion(self):
        retorno = None
        if self.is_valid():
            retorno = self.cleaned_data["hasta"]
        return retorno

    def timedeltaDuracion(self):
        retorno = None
        if self.is_valid():
            retorno = timedelta(**{self.unidadDuracion : self.cleaned_data["duracion"]})
        return retorno

    def clean(self):
        retorno = super().clean()

        validos  = "desde" not in self.errors
        validos &= "hasta" not in self.errors
        validos &= "duracion" not in self.errors

        if validos:
            inicio = retorno["desde"]
            finalizacion = retorno["hasta"]
            if retorno["duracion"] is not None:
                lapso = timedelta(**{ self.unidadDuracion : retorno["duracion"] })
            else:
                lapso = None

            if finalizacion == lapso == None:
                self.add_error(
                    None,
                    forms.ValidationError("La fecha y hora de finalización (o duración) son obligatorias", code="lapso_incoherente")
                )
            elif finalizacion == None:
                    retorno["hasta"] = inicio + lapso
            elif lapso == None:
                retorno["duracion"] = finalizacion - inicio
            else:
                if (inicio + lapso) != finalizacion:
                    self.add_error(
                        None,
                        forms.ValidationError("La fecha y hora de finalización no coinciden con la duración", code="lapso_incoherente")
                    )
                if retorno["desde"] >= retorno["hasta"]:
                    self.add_error(
                        None,
                        forms.ValidationError("La fecha y hora de inicio debe ser anterior a la fecha y hora de finalización.", code="lapso_incoherente")
                    )
            if self.minimo is not None and retorno["desde"] < self.minimo:
                self.add_error(
                    "desde",
                    forms.ValidationError(
                        "La fecha y hora de inicio no puede ser menor a las %s del %s." % (
                            self.minimo.strftime("%H:%M"),
                            self.minimo.strftime("%d/%m/%Y"),
                        ),
                        code="inicio_menor_minimo"
                    )
                )
            if self.maximo is not None and retorno["hasta"] > self.maximo:
                self.add_error(
                    "hasta",
                    forms.ValidationError(
                        "La fecha y hora de finalizacion no puede ser mayor a las %s del %s." % (
                            self.maximo.strftime("%H:%M"),
                            self.maximo.strftime("%d/%m/%Y"),
                        ),
                        code="finalizacion_mayor_maximo"
                    )
                )
        return retorno
