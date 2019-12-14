from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied

from VeterinariaPatagonica.areas import Areas
from VeterinariaPatagonica.tools import guardarWorkbook
from .models.practica import Practica
from .models.estado import *
from .gestionDePracticas import *
from .forms import  FiltradoRealizacionesForm

from openpyxl import Workbook


def listarXlsx(tipo, resultados, visibles, encabezados=None):

    filename = "%s-%s" % (tipo, datetime.now().strftime("%d%m%Y-%H%M%S-%f"))
    libro = Workbook()
    hoja = libro.create_sheet(filename, 0)
    fila = 1

    if encabezados:
        columna = 1
        for encabezado in encabezados:
            celda = hoja.cell(fila, columna, encabezado)
            columna += 1
        fila += 1

    for resultado in resultados:
        columna = 1
        if visibles[0]:
            celda = hoja.cell(fila, columna, resultado.id)
            columna += 1
        if visibles[1]:
            celda = hoja.cell(fila, columna, resultado.nombre_estado_actual)
            columna += 1
        if visibles[2]:
            celda = hoja.cell(fila, columna, str(resultado.cliente))
            columna += 1
        if visibles[3]:
            mascota = str(resultado.mascota) if resultado.mascota else ""
            celda = hoja.cell(fila, columna, mascota)
            columna += 1
        if visibles[4]:
            celda = hoja.cell(fila, columna, resultado.tipoDeAtencion.nombre)
            columna += 1
        if visibles[5]:
            celda = hoja.cell(fila, columna, resultado.precio)
            columna += 1
        if visibles[6]:
            celda = hoja.cell(fila, columna, resultado.marca_creacion)
            columna += 1
        if visibles[7]:
            celda = hoja.cell(fila, columna, resultado.marca_ultima_actualizacion)
            columna += 1
        if visibles[8]:
            celda = hoja.cell(fila, columna, resultado.nombre_creada_por)
            columna += 1
        if visibles[9]:
            celda = hoja.cell(fila, columna, resultado.nombre_atendida_por)
            columna += 1
        fila += 1

    response = HttpResponse(guardarWorkbook(libro), content_type="application/ms-excel")
    response["Content-Disposition"] = "attachment; filename=%s.xlsx" % filename
    return response


def realizaciones(request):

    usuario = request.user
    if isinstance(usuario, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    puedeRealizar = permisos.filtroPermitidas(usuario, Practica.Acciones.realizar)
    puedeListar = permisos.filtroPermitidas(usuario, Practica.Acciones.listar)
    if (puedeListar is None) or (puedeRealizar is None):
        raise PermissionDenied()

    practicas = Estado.anotarPracticas(
        Practica.objects.enEstado([Realizada, Facturada]).realizadasPor(usuario),
        estado_actual=True,
        atendida_por=True
    ).filter(puedeListar)

    gestor = GestorListadoRealizacion(
        campos = [
            ["iniciorealizacion", "Inicio"],
            ["duracionrealizacion", "Duración"],
            ["id", "Práctica"],
            ["estadoactual", "Estado Actual"],
            ["cliente", "Cliente"],
            ["mascota", "Mascota"],
            ["tipodeatencion", "Tipo de Atención"],
            ["precio", "Precio"],
            ["marcacreacion", "Creación"],
            ["marcaultimaactualizacion", "Última Actualización"],
            ["creadapor", "Creada por"],
            ["atendidapor", "Atendida por"],
        ],
        iniciales = {
            "seleccion" : (
                "iniciorealizacion",
                "duracionrealizacion",
                "id",
                "estadoactual",
                "cliente",
            ),
            "orden" : (
                ("iniciorealizacion", False),
            ),
        },
        clases={"filtrado" : FiltradoRealizacionesForm},
        queryset=practicas,
        mapaFiltrado=practicas.MAPEO_FILTRADO,
        mapaOrden=practicas.MAPEO_ORDEN,
    )

    gestor.cargar(request)
    gestor.paginacion["cantidad"].label = "Practicas por página"

    menu = [[], []]
    itemListar(usuario, menu[0], Areas.C)
    itemListar(usuario, menu[0], Areas.Q)
    itemListarTurnos(usuario, menu[0], Areas.Q)
    itemCrear(usuario, menu[1], Areas.C)
    itemCrear(usuario, menu[1], Areas.Q)

    template = loader.get_template( plantilla("listar", "realizaciones") )
    context = {
        "gestor" : gestor,
        "practicas" : practicas,
        "menu" : [ seccion for seccion in menu if len(seccion) ],
        "visibles" : permisos.permitidas(
            usuario,
            Practica.Acciones.ver_informacion_general,
            gestor.itemsActuales()
        )
    }
    return HttpResponse(template.render( context, request ))
