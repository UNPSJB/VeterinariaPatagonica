#Este archivo tools se puede utilizar en todos los modelos que tienen baja logica
#Sirve para realizar los filtros en los modelos
#Trabaja con QuerySet
from io import BytesIO
from zipfile import ZipFile, ZIP_STORED

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from .errores import VeterinariaPatagonicaError
from .forms import PaginacionForm, SeleccionForm, OrdenForm

from dal import autocomplete
from openpyxl.writer.excel import ExcelWriter


# class VeterinariaPatagonicaQuerySet(models.QuerySet):

#     def get(self, **kwargs):
#         try:
#             object = super().get(**kwargs)
#         except ObjectDoesNotExist:
#             raise VeterinariaPatagonicaError(
#                 titulo="Objeto '%s' no encontrado" % self.model.__name__,
#                 descripcion="El objeto solicitado no fue encontrado",
#             )
#         return object

#     def habilitados(self):
#         return self.filter(baja=False)

#     def deshabilitados(self):
#         return self.filter(baja=True)


#Esta clase sirve para gestionar las bajas
class BajasLogicasQuerySet(models.QuerySet):
    def habilitados(self):
        return self.filter(baja=False)

    def deshabilitados(self):
        return self.filter(baja=True)



#Esta funcion toma el diccionario (MAPPER) y retorna el objeto Q
def paramsToFilter(params, mapper):
    #raise Exception( str( params["cliente"] is not None ) )
    filters = models.Q()
    for item in params.items():
        key = item[0]
        value = item[1]
        if key in mapper: #and value:
            name = mapper[key]
            filters &= name(value) if callable(name) else models.Q(**{name: value})
    return filters



class R(models.Q):
    default=models.Q.OR



class GestorListadoQuerySet:

    paginasDistancia = 5

    def __getitem__(self, nombre):
        return self.campos[nombre]

    def __iter__(self):
        for nombre in self.columnasVisibles:
            yield self[nombre]

    def inicioPagina(self, pagina):
        return ((pagina-1)*self.tamanioPagina) +1

    def finPagina(self, pagina):
        ultimo = self.inicioPagina(pagina) + self.tamanioPagina -1
        return min(ultimo, self.numeroItems)

    def rangoActual(self):
        return self.rangoPagina(self.paginaActual)

    def rangoPagina(self, pagina):
        desde = self.inicioPagina(pagina)
        hasta = self.finPagina(pagina)
        return (desde, hasta)

    def itemsActuales(self):
        return self.itemsPagina(self.paginaActual)

    def itemsPagina(self, pagina):
        desde, hasta = self.rangoPagina(pagina)
        return self.queryset[desde-1:hasta]

    def items(self):
        return self.queryset

    def ordenandoSegun(self):
        if self.ordenActual:
            return self.ordenActual[0]
        return None

    def hacerFiltrado(self, filtros):
        self.queryset = self.queryset.filter(
            paramsToFilter(filtros, self.mapaFiltrado)
        )

    def hacerSeleccion(self, visibles):
        for campo in self.campos.values():
            campo["visible"] = False
        for nombre in visibles:
            self.campos[nombre]["visible"] = True
        self.columnasVisibles = tuple([
            nombre for nombre in self.columnas if self.campos[nombre]["visible"]
        ])

    def hacerOrden(self, orden):
        self.ordenActual = orden
        for posicion, (nombre, direccion) in enumerate(orden, start=1):
            self.campos[nombre]["orden"]     = posicion
            self.campos[nombre]["direccion"] = direccion
        argumentos = []
        for nombre, ascendente in orden:
            if self.campos[nombre]["visible"]:
                fields = self.mapaOrden[nombre]
                if not ascendente:
                    fields = ["-" + field for field in fields ]
                argumentos += fields
        self.queryset = self.queryset.order_by(*argumentos)

    def hacerPaginacion(self, cantidad, pagina):
        self.numeroItems    = self.queryset.count()
        self.tamanioPagina  = cantidad or self.numeroItems
        self.primerPagina   = 1
        if self.tamanioPagina > 0:
            self.ultimaPagina   = int((self.numeroItems-1)/self.tamanioPagina)+1
        else:
            self.ultimaPagina   = 1
        self.paginaActual   = min(pagina, self.ultimaPagina)
        self.anteriorPagina = max(self.paginaActual-1, self.primerPagina)
        self.proximaPagina  = min(self.paginaActual+1, self.ultimaPagina )

    def cargarFormulario(self, nombre, data=None):
        return self.clases[nombre](
            data=data,
            **self.argumentos[nombre]
        )

    def cargarSeleccion(self, data=None):
        self._actualizarArgumentosSeleccion()
        self.seleccion = self.cargarFormulario("seleccion", data)
        datos = self.seleccion.datos()
        self.hacerSeleccion(datos["seleccionados"])
        for lista in self.seleccion.errors.values():
            self.errores["seleccion"].extend(lista)

    def cargarFiltrado(self, data=None):
        self.filtrado = self.cargarFormulario("filtrado", data)
        self.hacerFiltrado(self.filtrado.filtros())
        for lista in self.filtrado.errors.values():
            self.errores["filtrado"].extend(lista)

    def cargarOrden(self, data=None):
        self._actualizarArgumentosOrden()
        self.orden = self.cargarFormulario("orden", data)
        datos = self.orden.datos(False)
        orden = self._ordenDeData(datos)
        if datos["ordenar"]:
            self._actualizarOrden(datos["ordenar"], orden)
        self.hacerOrden(orden)
        for lista in self.orden.errors.values():
            self.errores["orden"].extend(lista)
        self._actualizarArgumentosOrden()
        self.orden = self.cargarFormulario("orden")

    def cargarPaginacion(self, data=None):
        self._actualizarArgumentosPaginacion()
        self.paginacion = self.cargarFormulario("paginacion", data)

        datos = self.paginacion.datos(False)
        cantidad = datos["cantidad"]
        pagina = datos["pagina"] or datos["pagina_actual"]

        self.hacerPaginacion(cantidad, pagina)
        for lista in self.paginacion.errors.values():
            self.errores["paginacion"].extend(lista)
        self._actualizarArgumentosPaginacion()
        self.paginacion = self.cargarFormulario("paginacion")

    def cargar(self, request):

        self._get = bool(request.GET)
        if self._get:
            data = request.GET
        else:
            data = None

        if self.seleccionar:
            self.cargarSeleccion(data)
        if self.filtrar:
            self.cargarFiltrado(data)
        if self.ordenar:
            self.cargarOrden(data)
        if self.paginar:
            self.cargarPaginacion(data)

    def numeroErrores(self):
        return sum(
            len(errores) for errores in self.errores.values()
        )

    def erroresValidacion(self):
        retorno = []
        for form, etiqueta in (
            ("orden", "Orden de resultados") ,
            ("paginacion", "Paginación de resultados"),
            ("seleccion", "Selección de campos"),
            ("filtrado", "Filtrado de resultados"),
        ):
            if self.errores[form]:
                retorno.append(
                    {"label" : etiqueta, "errors" : self.errores[form] }
                )
        return retorno

    def _actualizarArgumentosOrden(self):
        campos = [
            (nombre, self[nombre]["etiqueta"]) for nombre in self.columnasVisibles
        ]

        if self.orden:
            orden = self.ordenActual
            choices = self._choicesOrden()
            ordenar = self._codificarOrden( *self.ordenandoSegun() )
        else:
            orden = self._ordenInicial(self.iniciales["orden"])
            choices = None
            ordenar = None

        initial = self._dataDeOrden(orden)
        initial["ordenar"] = ordenar

        self.argumentos["orden"]["initial"] = initial
        self.argumentos["orden"]["choices"] = choices
        self.argumentos["orden"]["campos"]  = campos

    def _actualizarArgumentosSeleccion(self):
            campos = [
                (nombre, self[nombre]["etiqueta"]) for nombre in self.columnas
            ]
            initial = {}
            if "seleccion" in self.iniciales and self.iniciales["seleccion"]:
                initial["seleccionados"] = self.iniciales["seleccion"]
            if "seleccionados" not in initial:
                initial["seleccionados"] = [ nombre for nombre in self.columnas ]
            self.argumentos["seleccion"]["initial"] = initial
            self.argumentos["seleccion"]["campos"] = campos

    def _actualizarArgumentosPaginacion(self):
        if self.paginacion:
            choices = self._choicesPaginas()
            initial = {
                "pagina_actual" : self.paginaActual,
                "cantidad" : self.tamanioPagina,
                "pagina" : self.paginaActual
            }
        else:
            choices = None
            initial = self.iniciales["paginacion"] or {}
            if self._get:
                initial["cantidad"] = 0
        self.argumentos["paginacion"]["choices"] = choices
        self.argumentos["paginacion"]["initial"] = initial

    def _actualizarOrden(self, codigo, orden):
        nuevo = self._decodificarOrden(codigo)
        if nuevo == orden[0]:
            orden[0][1] = not orden[0][1]
        else:
            try:
                posicion = orden.index(nuevo)
            except:
                posicion = 0
            if posicion:
                item = orden.pop(posicion)
                orden.insert(0, item)

    def _codificarOrden(self, nombre, direccion):
        retorno = "+" if direccion else "-"
        return retorno + nombre

    def _decodificarOrden(self, codigo):
        return [codigo[1:], (codigo[0]=="+")]

    def _dataDeOrden(self, orden):
        nombres, direcciones = zip(*orden)
        nombres = list(nombres)
        direcciones = list(direcciones)
        data = {}
        for i in range(len(nombres)):
            data[nombres[i]] = (i+1) if direcciones[i] else -(i+1)
        return data

    def _ordenDeData(self, data):
        numerados = []
        pendientes = []
        ultimo = 0
        for nombre in self.columnasVisibles:
            if nombre in data:
                valor = data[nombre]
                numerados.append([abs(valor), valor>0, nombre])
                ultimo = abs(valor) if abs(valor) > ultimo else ultimo
            else:
                pendientes.append(nombre)
        for nombre in pendientes:
            ultimo += 1
            numerados.append([abs(ultimo), True, nombre])
        numerados.sort(key=lambda x: x[0])
        return [
            [nombre, direccion] for numero, direccion, nombre in numerados
        ]

    def _ordenInicial(self, orden):
        orden = () if orden is None else orden
        nombres     = []
        direcciones = []
        for nombre, direccion in orden:
            if nombre in self.columnasVisibles:
                nombres.append(nombre)
                direcciones.append(bool(direccion))
        for nombre in self.columnasVisibles:
            if nombre not in nombres:
                nombres.append(nombre)
                direcciones.append(True)
        return [
            [nombres[i], direcciones[i]] for i in range(len(nombres))
        ]

    def _choicesPaginas(self):
        retorno = []
        if self.ultimaPagina > self.primerPagina:
            menor = max(self.paginaActual-self.paginasDistancia, self.primerPagina)
            mayor = min(self.paginaActual+self.paginasDistancia, self.ultimaPagina )
            retorno.extend([
                (self.primerPagina,    "Primera"),
                (self.anteriorPagina,  "Anterior")
            ])
            retorno.extend(
                (num, str(num)) for num in range(menor, mayor+1)
            )
            retorno.extend([
                (self.proximaPagina,   "Siguiente"),
                (self.ultimaPagina,    "Ultima")
            ])
        return retorno

    def _choicesOrden(self):
        return [
            (
                self._codificarOrden(nombre, self.campos[nombre]["direccion"]),
                self.campos[nombre]["etiqueta"]
            ) for nombre in self.columnasVisibles
        ]

    def __init__(self, queryset=None, campos=[], clases={}, iniciales={}, mapaFiltrado={},  mapaOrden={}, **kwargs):
        self.columnas = tuple(next(zip(*campos)))
        self.columnasVisibles = tuple(self.columnas)
        self.queryset = queryset
        self.campos = {}
        for nombre, etiqueta in campos:
            self.campos[nombre] = {
                "visible" : True,
                "nombre" : nombre,
                "etiqueta" : etiqueta,
            }

        self.argumentos = {
            "filtrado" : {},
            "seleccion" : {},
            "paginacion" : {},
            "orden" : {}
        }

        for form in ("paginacion", "seleccion", "orden", "filtrado"):
            if form in kwargs and kwargs[form] is not None:
                self.argumentos[form].update(kwargs[form])
            self.argumentos[form]["initial"] = {}
            if "prefix" not in self.argumentos[form]:
                self.argumentos[form]["prefix"] = form

        self.iniciales = {
            "paginacion" :  None,
            "orden" :       None,
            "seleccion" :   None,
            "filtrado" :    None,
        }
        self.iniciales.update(iniciales)

        self.clases = {
            "paginacion" :  PaginacionForm,
            "orden" :       OrdenForm,
            "seleccion" :   SeleccionForm,
            "filtrado" :    None
        }
        self.clases.update(clases)

        self.paginar    = self.clases["paginacion"] is not None
        self.ordenar    = self.clases["orden"] is not None
        self.seleccionar= self.clases["seleccion"] is not None
        self.filtrar    = self.clases["filtrado"] is not None

        self.paginacion = None
        self.orden      = None
        self.seleccion  = None
        self.filtrado   = None

        self.mapaFiltrado = mapaFiltrado
        self.mapaOrden    = mapaOrden
        self.errores = {
            "paginacion" : [],
            "orden" :      [],
            "seleccion" :  [],
            "filtrado" :   [],
        }


def guardarWorkbook(workbook):
    bufer = BytesIO()
    writer = ExcelWriter(
        workbook,
        ZipFile(bufer, "w", compression=ZIP_STORED, allowZip64=False)
    )
    writer.save()
    bytes = bufer.getvalue()
    del(bufer)
    return bytes
