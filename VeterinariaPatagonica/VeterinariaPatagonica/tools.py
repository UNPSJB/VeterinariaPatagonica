#Este archivo tools se puede utilizar en todos los modelos que tienen baja logica
#Sirve para realizar los filtros en los modelos
#Trabaja con QuerySet

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from .errores import VeterinariaPatagonicaError
from .forms import PaginaListadoForm, OrdenListadoForm
#from VeterinariaPatagonica.Apps.GestionDeProductos.models import Producto
from dal import autocomplete

from django.views.generic.base import TemplateView


class VeterinariaPatagonicaQuerySet(models.QuerySet):

    def get(self, **kwargs):
        try:
            object = super().get(**kwargs)
        except ObjectDoesNotExist:
            raise VeterinariaPatagonicaError(
                titulo="Objeto '%s' no encontrado" % self.model.__name__,
                descripcion="El objeto solicitado no fue encontrado",
            )
        return object

    def habilitados(self):
        return self.filter(baja=False)

    def deshabilitados(self):
        return self.filter(baja=True)


#Esta clase sirve para gestionar las bajas
class BajasLogicasQuerySet(VeterinariaPatagonicaQuerySet):
    def habilitados(self):
        return self.filter(baja=False)

    def deshabilitados(self):
        return self.filter(baja=True)

#Esta funcion toma el diccionario (MAPPER) y retorna el objeto Q
def paramsToFilter(params, Modelo):
    mapper = getattr(Modelo, "MAPPER", {})
    filters = models.Q()
    for item in params.items():
        key = item[0]
        value = item[1]
        if key in mapper and value:
            name = mapper[key]
            filters &= name(value) if callable(name) else models.Q(**{name: value})
    return filters


class R(models.Q):
    default=models.Q.OR

class GestorListado:

    def etiqueta(self, columna):
        for nombre,etiqueta in self.orden:
            if columna == nombre:
                return etiqueta
        return None

    def nombres_columnas(self):
        return [ nombre for nombre,etiqueta in self.orden ]

    def inicio_pagina(self, numero_pagina):
        return (numero_pagina-1)*self.tamanio_pagina

    def rango_pagina(self, numero_pagina):
        desde = self.inicio_pagina(numero_pagina)
        hasta = min(desde+self.tamanio_pagina, self.numero_items)
        return (desde, hasta)

    def en_primer_pagina(self):
        return self.pagina_actual == self.primer_pagina

    def en_ultima_pagina(self):
        return self.pagina_actual == self.ultima_pagina

    def _proximo(self, orden, item):

        proximo_orden = [ o.copy() for o in orden ]
        posicion = proximo_orden.index(item)
        proximo = proximo_orden.pop(posicion)

        if posicion == 0:
            proximo[1] = not proximo[1]
        proximo_orden.insert(0, proximo)

        return proximo_orden

    def _url(self, orden):

        get = self.get.copy()
        for posicion,item in enumerate(orden, start=1):
            nombre = item[0]
            ascendente = item[1]
            signo = 1 if ascendente else -1
            get[nombre] = str(posicion*signo)

        return "%s?%s" % (self.path, get.urlencode())

    def _pagina(self, numero):
        numero = max(numero, self.primer_pagina)
        numero = min(numero, self.ultima_pagina)
        primera, ultima = self.rango_pagina(numero)
        return {
            "numero": numero,
            "primera": primera,
            "ultima": ultima,
            "habilitada": self.pagina_actual != numero,
            "url" : self.url_pagina.format(primera),
        }


    def cargar(self, request):

        self.formOrden = self.ClaseOrden(
            request.GET,
            columnas=self.nombres_columnas(),
        ) if self.orden else None


        self.formPagina = self.ClasePagina(
            request.GET,
            nombre_cantidad=self.clave_cantidad,
            nombre_desde=self.clave_desde
        )

        self.path = request.path
        #raise Exception(str(request.GET))
        self.get = request.GET.copy()
        desde = self.formPagina.desde()
        self.get[self.clave_desde] = "{:d}"
        self.url_pagina = "%s?%s" % (self.path, self.get.urlencode(safe="{}:"))
        self.get[self.clave_desde] = str(desde)

        return (self.formOrden is None or self.formOrden.is_valid()) \
        and (self.formPagina is None or self.formPagina.is_valid())

    @property
    def paginas(self):

        get = self.get.copy()
        primera = max(self.pagina_actual-self.paginas_distancia, self.primer_pagina)
        ultima = min(self.pagina_actual+self.paginas_distancia, self.ultima_pagina )

        retorno = {
            "primera" : self._pagina(self.primer_pagina),
            "anterior" : self._pagina(self.pagina_actual-1),
            "paginas" : [],
            "siguiente" : self._pagina(self.pagina_actual+1),
            "ultima" : self._pagina(self.ultima_pagina),
        }
        for numero in range(primera, ultima+1):
            retorno["paginas"].append(self._pagina(numero))

        return retorno

    @property
    def encabezado(self):
        retorno = {}
        orden = self.formOrden.orden()

        for item in orden:
            nombre = item[0]
            proximo = self._proximo(orden, item)
            retorno[nombre] = {
                "etiqueta" : self.etiqueta(nombre),
                "url" : self._url(proximo),
                "activa" : (item == orden[0]),
            }

        for nombre,ascendente in orden:
            retorno[nombre]["ascendente"] = ascendente

        return retorno

    def actualizar(self, cantidad=None, desde=None, numero_items=None):

        if numero_items is None:
            numero_items = self.numero_items
        if desde is None:
            desde = self.formPagina.desde()
        if cantidad is None:
            cantidad = self.formPagina.cantidad()

        self.tamanio_pagina = cantidad

        self.primer_pagina = 1
        self.ultima_pagina = int((numero_items-1)/self.tamanio_pagina)+1
        self.pagina_actual = int(desde/self.tamanio_pagina)+1
        self.numero_paginas = self.ultima_pagina

        self.primer_item = 0
        self.ultimo_item = numero_items-1
        self.numero_items = numero_items
        self.rango_actual = self.rango_pagina(self.pagina_actual)

    def __init__(self, orden=[]):

        self.orden = tuple([ tuple(item) for item in orden ])

        self.ClaseOrden = OrdenListadoForm
        self.ClasePagina = PaginaListadoForm

        self.clave_desde = "desde"
        self.clave_cantidad = "resultados"
        self.paginas_distancia = 7
        self.numero_items = 0


class GestorListadoQueryset(GestorListado):

    def filtrar(self):
        queryset = self.queryset.filter(
            paramsToFilter(self.formFiltros.filtros(), self.Clase)
        )
        self.actualizar(queryset)

    def ordenar(self):
        argumentos = []
        for nombre,ascendente in self.formOrden.orden():
            fields = self.queryset.MAPEO_ORDEN[nombre]
            if not ascendente:
                fields = ["-" + field for field in fields ]
            argumentos += fields
        self.queryset = self.queryset.order_by(*argumentos)

    def items_actuales(self):
        desde, hasta = self.rango_actual
        return self.queryset[desde:hasta]

    def items_pagina(self, numero_pagina):
        desde, hasta = self.rango_pagina(numero_pagina)
        return self.queryset[desde:hasta]

    def items(self):
        return self.queryset

    def actualizar(self, queryset):
        self.queryset = queryset
        super().actualizar(numero_items=queryset.count())

    def cargar(self, request, queryset, clase=None):
        super().cargar(request)
        if self.ClaseFiltros:
            self.formFiltros = self.ClaseFiltros(request.GET)

        self.Clase = clase
        self.actualizar(queryset)

    def __init__(self, *args, claseFiltros=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.ClaseFiltros = claseFiltros

'''
class productoAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        qs = Producto.objects.all()

        if self.q:
           qs = qs.filter(Q(descripcion__icontains=self.q) | Q(nombre__icontains=self.q) | Q(marca__icontains=self.q))

        return qs


'''
