from django.urls import reverse
from .settings import *
from math import ceil
from VeterinariaPatagonica.errores import VeterinariaPatagonicaError

def pathListar(tipo):
    return reverse(
        "%s:%s:listar" % (APP_NAME, tipo)
    )

def calcularPaginas(queryset):
    cantidad = ceil(queryset.count() / CLIENTES_POR_PAGINA)
    return max(cantidad, 1)

def clientesParaPagina(queryset, pagina, paginas):

    if not (1 <= pagina <= paginas):
        raise VeterinariaPatagonicaError("Pagina no existe", "Numero de pagina %s no valido" % str(pagina))

    n = (pagina-1) * CLIENTES_POR_PAGINA
    m = pagina * CLIENTES_POR_PAGINA

    return queryset[n:m]

def menuExportar(usuario, formato, area):
    menu = [[],[]]
    if formato != "xlsx":
        itemExportar(usuario, menu[0], "xlsx", area)
    itemListar(usuario, menu[1], area)
    return [ item for item in menu if len(item) ]