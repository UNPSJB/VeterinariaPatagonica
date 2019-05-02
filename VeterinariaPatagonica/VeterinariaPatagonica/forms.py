from django import forms



class LoginForm(forms.Form):

    usuario = forms.CharField(
        required=True,
        label = 'Usuario',
        widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder' : 'Usuario...'
        }),
        help_text="Nombre de usuario para iniciar sesion"
    )

    password = forms.CharField(
        required=True,
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class' : 'form-control',
            'placeholder' : 'Contraseña...'
        }),
        help_text="Contraseña de usuario"
    )


class OrdenListadoForm(forms.Form):

    def initial_columnas(self):
        return {
            x[1] : str(x[0]) for x in enumerate(self.nombres_columnas, start=1)
        }

    def primer_orden(self):
        return [[columna, False] for columna in self.nombres_columnas]

    def orden(self):

        data = self.clean()
        for columna in self.nombres_columnas:
            if (not columna in data) or (not data[columna]):
                return self.primer_orden()

        columnas = []
        for columna in self.nombres_columnas:
            valor = data[columna]
            columnas.append([abs(valor), valor>0, columna])
        columnas.sort()

        return [[nom, asc] for pos,asc,nom in columnas]

    def __init__(   self, *args, columnas=[], **kwargs ):
        super().__init__(*args, **kwargs)
        self.nombres_columnas = columnas
        if columnas:
            for columna, valor in self.initial_columnas().items():
                self.fields[columna] = forms.IntegerField(
                    required=False,
                    widget = forms.HiddenInput(
                        attrs={"value":valor}
                    ),
                )


class PaginaListadoForm(forms.Form):

    RESULTADOS = (
        (10, "10 Resultados por pagina"),
        (20, "20 Resultados por pagina"),
        (40, "40 Resultados por pagina"),
        (60, "60 Resultados por pagina"),
        (80, "80 Resultados por pagina"),
        (100, "100 Resultados por pagina"),
        (200, "200 Resultados por pagina"),
    )
    RESULTADOS_DEFAULT = RESULTADOS[0][0]

    def cantidad(self):
        cantidad = self.nombre_cantidad
        if self.is_valid():
            data = self.cleaned_data
            if (cantidad in data) and data[cantidad]:
                return data[cantidad]
        return PaginaListadoForm.RESULTADOS_DEFAULT

    def desde(self):
        desde = self.nombre_desde
        if self.is_valid():
            data = self.cleaned_data
            if (desde in data) and data[desde]:
                return data[desde]
        return 0

    def __init__(self,*args,nombre_cantidad="resultados",nombre_desde="desde",**kwargs):
        super().__init__(*args, **kwargs)

        self.nombre_desde = nombre_desde
        self.fields[nombre_desde] = forms.IntegerField(
            required=False,
            widget = forms.HiddenInput(
                attrs={"value":"0"}
            ),
        )

        self.nombre_cantidad = nombre_cantidad
        self.fields[nombre_cantidad] = forms.TypedChoiceField(
            choices = PaginaListadoForm.RESULTADOS,
            coerce=int,
            empty_value=None,
            required=False,
            widget = forms.Select(
                attrs={"class":"form-control"},
            ),
        )



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
    validate_max = False

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
        valores = tuple( item.cleaned_data[field] for field in self.id_fields )
        for i in range( len(self.forms) ):
            item = self.forms[i]
            if not item.is_valid() or i in self._ignorar_forms:
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
        errores = []
        for i in range( len(self.forms) ):
            form = self.forms[i]
            vacios = self._vacios(i)
            if len(vacios):
                self._ignorar_forms.append(i)
                if not self.ignorar_incompletos:
                    errores.append(forms.ValidationError(
                        "%s de la fila %d son obligatorios" % (", ".join(vacios).capitalize(), i+1),
                    ))
        return errores

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
        errores = []

        #Valida que cada form tenga completo los campos de identidad
        errores.extend( self._validarIdentidades() )

        #Valida que no hayan forms con la misma identidad
        errores.extend( self._validarOcurrencias() )

        if len(errores) > 0:
            raise forms.ValidationError(errores)
        return retorno

    @property
    def completos(self):
        return [
            self.forms[i].cleaned_data for i in range(len(self.forms)) if not i in self._ignorar_forms
        ]

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
