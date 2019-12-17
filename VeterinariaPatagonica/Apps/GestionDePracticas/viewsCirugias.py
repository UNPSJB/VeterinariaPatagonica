from datetime import datetime

from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied

from VeterinariaPatagonica.areas import Areas
from VeterinariaPatagonica.errores import VeterinariaPatagonicaError
from VeterinariaPatagonica.forms import ExportarForm
from VeterinariaPatagonica import pdf
from .models.practica import Practica
from .models.estado import *
from .gestionDePracticas import *
from .views import listarXlsx, reporteHtml
from . import reportes


def contextoCreacion(request, idCreacion):
    return crearContexto(
        request,
        idCreacion,
        tipoPractica=Areas.Q.nombre(),
    )


def contextoModificacion(practica, accion=None):
    return {
        "tipo" : Areas.Q.nombre(),
        "practica" : practica,
        "accion" : accion,
        "errores" : [],
    }


def listar(request):

    usuario = request.user
    if isinstance(usuario, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    filtros = permisos.filtroPermitidas(usuario, Practica.Acciones.listar)
    if filtros is None:
        raise PermissionDenied()

    practicas = Estado.anotarPracticas(
        Practica.quirurgicas.all(),
        estado_actual=True,
        atendida_por=True
    ).filter(filtros)

    gestor = GestorListadoPractica(
        campos = [
            ["id", "Cirugía"],
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
                "id",
                "estadoactual",
                "cliente",
                "marcacreacion",
                "marcaultimaactualizacion",
            ),
            "orden" : (
                ("marcaultimaactualizacion", False),
                ("estadoactual", False),
            ),
        },
        clases={"filtrado" : FiltradoCirugiaForm},
        queryset=practicas,
        mapaFiltrado=practicas.MAPEO_FILTRADO,
        mapaOrden=practicas.MAPEO_ORDEN,
    )

    gestor.cargar(request)
    gestor.paginacion["cantidad"].label = "Cirugías por página"

    menu = [[], [], [], []]
    itemExportar(usuario, menu[0], "xlsx", Areas.Q)
    itemListarRealizaciones(usuario, menu[1])
    itemListarTurnos(usuario, menu[1], Areas.Q)
    itemCrear(usuario, menu[2], Areas.Q)
    itemReporte(usuario, menu[3], Areas.Q)

    template = loader.get_template( plantilla("listar", "cirugias") )
    context = {
        "tipo" : Areas.Q.nombre(),
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


def turnos(request):

    usuario = request.user
    if isinstance(usuario, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    puedeRealizar = permisos.filtroPermitidas(usuario, Practica.Acciones.realizar, areas=[Areas.Q])
    puedeListar = permisos.filtroPermitidas(usuario, Practica.Acciones.listar, areas=[Areas.Q])
    if (puedeListar is None) or (puedeRealizar is None):
        raise PermissionDenied()

    practicas = Estado.anotarPracticas(
        Practica.quirurgicas.enEstado(Programada),
        estado_actual=True,
        atendida_por=True
    ).filter(puedeListar)

    gestor = GestorListadoTurnos(
        campos = [
            ["inicioturno", "Inicio"],
            ["duracionturno", "Duración"],
            ["tiemporestante", "Tiempo restante"],
            ["id", "Cirugía"],
            ["programadapor", "Atendida por"],
            ["cliente", "Cliente"],
            ["mascota", "Mascota"],
            ["reprogramaciones", "Reprogramaciones"],
            ["tipodeatencion", "Tipo de Atención"],
            ["creadapor", "Creada por"],
            ["marcacreacion", "Creación"],
            ["marcaultimaactualizacion", "Ultima Actualización"],
        ],
        iniciales = {
            "seleccion" : (
                "inicioturno",
                "duracionturno",
                "tiemporestante",
                "id",
                "programadapor",
                "cliente",
            ),
        },
        clases={"filtrado" : FiltradoTurnosForm},
        queryset=practicas,
        mapaFiltrado=practicas.MAPEO_FILTRADO,
        mapaOrden=practicas.MAPEO_ORDEN,
    )

    gestor.cargar(request)
    gestor.paginacion["cantidad"].label = "Turnos por página"

    menu = [[], []]
    itemListarRealizaciones(usuario, menu[0])
    itemListar(usuario, menu[0], Areas.Q)
    itemCrear(usuario, menu[1], Areas.Q)

    template = loader.get_template( plantilla("listar", "turnos") )
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


def exportar(request, formato=None):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (LOGIN_URL, request.path))

    permitidas = permisos.filtroPermitidas(
        request.user,
        Practica.Acciones["exportar_%s" % formato],
        areas=Areas.Q
    )
    if permitidas is None:
        raise PermissionDenied()
    practicas = Estado.anotarPracticas(
        Practica.quirurgicas.all(),
        estado_actual=True,
        atendida_por=True,
    ).filter(permitidas)

    gestor = GestorListadoPractica(
        campos = [
            ["id", "Cirugía"],
            ["estadoactual", "Estado Actual"],
            ["cliente", "Cliente"],
            ["mascota", "Mascota"],
            ["tipodeatencion", "Tipo de Atención"],
            ["precio", "Precio"],
            ["marcacreacion", "Creación"],
            ["marcaultimaactualizacion", "Ultima Actualización"],
            ["creadapor", "Creada por"],
            ["atendidapor", "Atendida por"],
        ],
        iniciales = {
            "seleccion" : (
                "id",
                "estadoactual",
                "cliente",
                "marcacreacion",
                "marcaultimaactualizacion",
                "atendidapor",
            ),
            "orden" : (
                ("marcaultimaactualizacion", False),
                ("estadoactual", False),
            ),
        },
        clases={"filtrado" : FiltradoCirugiaForm},
        queryset=practicas,
        mapaFiltrado=practicas.MAPEO_FILTRADO,
        mapaOrden=practicas.MAPEO_ORDEN,
    )

    gestor.cargar(request)
    gestor.paginacion["cantidad"].label = "Cirugías por página"
    exportar = ExportarForm(request.GET)
    accion = exportar.accion()

    if accion == "":
        template = loader.get_template(plantilla("exportar", "cirugias"))
        context = {
            "formato" : formato,
            "gestor" : gestor,
            "exportar" : exportar,
            "menu" : menuExportar(request.user, formato, Areas.Q),
        }
        retorno = HttpResponse(template.render(context, request))
    else:
        nombre = "cirugias-%s" % datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        visibles = [ gestor[campo]["visible"] for campo in gestor.columnas ]
        encabezados = [ gestor[campo]["etiqueta"] for campo in gestor.columnasVisibles ]

        if accion=="exportar_pagina":
            cirugias = gestor.itemsActuales()
        elif accion=="exportar_todos":
            cirugias = gestor.items()

        contenido = listarXlsx("cirugias", cirugias, visibles, encabezados)
        retorno = HttpResponse(contenido, content_type="application/ms-excel")
        retorno["Content-Disposition"] = "attachment; filename=%s.xlsx" % nombre
    return retorno


def ver(request, id):

    usuario = request.user
    if isinstance(usuario, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    try:
        practica = Practica.quirurgicas.get(id=id)
    except Practica.DoesNotExist:
        raise VeterinariaPatagonicaError(
            "Error",
            "La cirugia con id %d no fue encontrada" % id
        )

    acciones = Practica.Acciones.ver_informacion_general
    if not permisos.paraPractica(usuario, acciones, practica):
        raise PermissionDenied()

    estados = practica.estados.all()
    tope = estados.count()
    try:
        n = int( request.GET["estado"] )
    except (ValueError, KeyError):
        n = 0

    n = n if (0 < n < tope) else tope-1
    estado = estados[n].related()
    accion = Practica.Acciones.ver_detalle_estado
    if not permisos.paraPractica(usuario, accion, practica, estado=estado):
        estado = None

    context = {
        "practica" : practica,
        "estado" : estado,
        "menu" : menuAcciones(usuario, Practica.Acciones.ver_informacion_general, practica),
        "historial" : enlacesHistorial(usuario, practica, n)
    }

    template = loader.get_template(plantilla("ver", "informacionGeneral"))
    return HttpResponse(template.render( context, request ))


def crear(request):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    if not permisos.paraCrear(request.user, Areas.Q):
        raise PermissionDenied()

    context = { "tipo" : Areas.Q.nombre(), "errores" : [] }
    acciones = accionesIniciales(request.user, Areas.Q)

    if request.method == "POST":

        formCreacion = CreacionForm(acciones, request.POST)
        formPractica = PracticaForm(request.POST)
        formsetServicios = CirugiaServicioFormSet(request.POST, prefix="servicio")

        if formPractica.is_valid() and formsetServicios.is_valid() and formCreacion.is_valid():

            idCreacion = idCrearPractica(request.session)
            servicios = formsetServicios.cleaned_data
            practica = { attr : obj.id for attr, obj in formPractica.cleaned_data.items() }
            accion = formCreacion.accion()

            guardar(request.session, idCreacion, "tipo", Areas.Q.nombre())
            guardar(request.session, idCreacion, "initialPractica", practica)
            guardar(request.session, idCreacion, "initialServicios", servicios)

            try:
                productos = buscarProductos(servicios)
            except VeterinariaPatagonicaError as error:
                context["errores"].append(error)
            else:
                guardar(request.session, idCreacion, "initialProductos", productos)
                if accion:
                    return HttpResponseRedirect(pathInicializar(Areas.Q.nombre(), accion, idCreacion))

                return HttpResponseRedirect(pathModificar(Areas.Q.nombre(), idCreacion))
    else:

        formCreacion = CreacionForm(acciones)
        formPractica = PracticaForm()
        formsetServicios = CirugiaServicioFormSet(prefix="servicio")

    context["formPractica"] = formPractica
    context["formsetServicios"] = formsetServicios
    context["acciones"] = formCreacion

    template = loader.get_template(plantilla("crear", "crear"))
    return HttpResponse(template.render(context, request))


def modificar(request, idCreacion):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    if not permisos.paraCrear(request.user, Areas.Q):
        raise PermissionDenied()

    try:
        context = contextoCreacion(request, idCreacion)
    except VeterinariaPatagonicaError as error:
        context = { "errores": [error] }
    else:
        try:
            initialPractica = obtener(request.session, idCreacion, "initialPractica")
        except VeterinariaPatagonicaError as error:
            context["errores"].append(error)
            initialPractica = {}
        try:
            initialServicios = obtener(request.session, idCreacion, "initialServicios")
        except VeterinariaPatagonicaError as error:
            context["errores"].append(error)
            initialServicios = ()
        acciones = accionesIniciales(request.user, Areas.Q)

        if request.method == "POST":

            formCreacion = CreacionForm(acciones, request.POST)
            formPractica = PracticaForm(request.POST, initial=initialPractica)
            formsetServicios = CirugiaServicioFormSet(request.POST, initial=initialServicios, prefix="servicio")

            if formPractica.is_valid() and formsetServicios.is_valid() and formCreacion.is_valid():
                accion = formCreacion.accion()

                if formPractica.has_changed():
                    initialPractica = { attr : obj.id for attr, obj in formPractica.cleaned_data.items() }
                    guardar(request.session, idCreacion, "initialPractica", initialPractica)

                if formsetServicios.has_changed():
                    initialServicios = formsetServicios.cleaned_data
                    try:
                        initialProductos = buscarProductos(initialServicios)
                    except VeterinariaPatagonicaError as error:
                        context["errores"].append(error)
                        accion = None
                    else:
                        guardar(request.session, idCreacion, "initialServicios", initialServicios)
                        guardar(request.session, idCreacion, "initialProductos", initialProductos)

                if accion:
                    return HttpResponseRedirect(pathInicializar(Areas.Q.nombre(), accion, idCreacion))
        else:
            formPractica = PracticaForm(initial=initialPractica)
            formsetServicios = CirugiaServicioFormSet(initial=initialServicios, prefix="servicio")
            formCreacion = CreacionForm(acciones)

        practica = obtenerPractica(request, idCreacion)
        detalles = obtenerDetalles(request, idCreacion)
        context["practica"] = practica
        context["detalles"] = detalles
        context["precio"]   = calcularPrecio(detalles, practica.tipoDeAtencion.recargo)
        context["duracion"] = calcularDuracion(detalles["servicios"])

        context["formPractica"] = formPractica
        context["formsetServicios"] = formsetServicios
        context["acciones"] = formCreacion

    template = loader.get_template(plantilla("crear", "modificar"))
    return HttpResponse(template.render(context, request))


def modificarProductos(request, idCreacion):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    if not permisos.paraCrear(request.user, Areas.Q):
        raise PermissionDenied()

    try:
        context = contextoCreacion(request, idCreacion)
    except VeterinariaPatagonicaError as error:
        context = { "errores": [error] }
    else:

        try:
            initialProductos = obtener(request.session, context["id"], "initialProductos")
        except VeterinariaPatagonicaError as error:
            context["errores"].append(error)
            initialProductos = ()
        acciones = accionesIniciales(request.user, Areas.Q)

        if request.method == "POST":

            formset = PracticaProductoFormSet(request.POST, initial=initialProductos, prefix="producto")
            formCreacion = CreacionForm(acciones, request.POST)

            if formset.is_valid() and formCreacion.is_valid():
                if formset.has_changed():
                    guardar(request.session, context["id"], "initialProductos", formset.cleaned_data)

                accion = formCreacion.accion()
                if accion:
                    return HttpResponseRedirect(pathInicializar(context["tipo"], accion, context["id"]))

        else:
            formset = PracticaProductoFormSet(initial=initialProductos, prefix="producto")
            formCreacion = CreacionForm(acciones)

        practica = obtenerPractica(request, idCreacion)
        detalles = obtenerDetalles(request, idCreacion)
        context["practica"] = practica
        context["detalles"] = detalles
        context["precio"]   = calcularPrecio(detalles, context["practica"].tipoDeAtencion.recargo)
        context["duracion"] = calcularDuracion(detalles["servicios"])
        context["acciones"] = formCreacion

        context["formset"] = formset

    template = loader.get_template(plantilla("crear", "productos"))
    return HttpResponse(template.render(context, request))


def crearPresupuestada(request, idCreacion):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    if not permisos.paraCrear(request.user, Areas.Q, accion=Practica.Acciones.presupuestar):
        raise PermissionDenied()

    try:
        context = contextoCreacion(request, idCreacion)
    except VeterinariaPatagonicaError as error:
        context = { "errores": [error] }
    else:
        try:
            practica = obtenerPractica(request, idCreacion)
            detalles = obtenerDetalles(request, idCreacion)

            if request.method == "POST":

                form = formPresupuestar(request.POST, practica=practica)
                if form.is_valid():
                    accion = form.accion()
                    datos = form.datos()
                    form.actualizarPractica()
                    try:
                        practica = persistir(request.user, practica, detalles, accion, datos)
                    except VeterinariaPatagonicaError as error:
                        context["errores"].append(error)
                    else:
                        eliminar(request.session, idCreacion)
                        return HttpResponseRedirect(pathVer(context["tipo"], practica.id))

            else:
                form = formPresupuestar(practica=practica)

            context["form"] = form
            context["practica"] = practica
            context["detalles"] = detalles
            context["precio"] = calcularPrecio(detalles, practica.tipoDeAtencion.recargo)
            context["duracion"] = calcularDuracion(detalles["servicios"])
            context["accion"] = "Crear presupuesto"


        except VeterinariaPatagonicaError as error:
            context["errores"].append(error)

    template = loader.get_template(plantilla("crear", "presupuestada"))
    return HttpResponse(template.render(context, request))


def crearProgramada(request, idCreacion):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    if not permisos.paraCrear(request.user, Areas.Q, accion=Practica.Acciones.programar):
        raise PermissionDenied()

    try:
        context = contextoCreacion(request, idCreacion)
    except VeterinariaPatagonicaError as error:
        context = { "errores": [error] }
    else:

        try:
            practica = obtenerPractica(request, idCreacion)
            verificarCreacion(practica, Practica.Acciones.programar.name)

            detalles = obtenerDetalles(request, idCreacion)
            precio = calcularPrecio(detalles, practica.tipoDeAtencion.recargo)
            duracion = calcularDuracion(detalles["servicios"])

            if request.method == "POST":

                form = formProgramar(request.POST, practica=practica, precio=precio, duracion=duracion)
                if form.is_valid():
                    accion = form.accion()
                    datos = form.datos()
                    form.actualizarPractica()
                    try:
                        practica = persistir(request.user, practica, detalles, accion, datos)
                    except VeterinariaPatagonicaError as error:
                        context["errores"].append(error)
                    else:
                        eliminar(request.session, idCreacion)
                        return HttpResponseRedirect(pathVer(context["tipo"], practica.id))

            else:
                form = formProgramar(practica=practica, precio=precio, duracion=duracion)

            context["form"] = form
            context["practica"] = practica
            context["detalles"] = detalles
            context["precio"] = precio
            context["duracion"] = duracion
            context["porcentajeAdelanto"] = (config("adelanto") * 100)
            context["accion"] = "Crear turno"

        except VeterinariaPatagonicaError as error:
            context["errores"].append(error)

    template = loader.get_template(plantilla("crear", "programada"))
    return HttpResponse(template.render(context, request))


def crearRealizada(request, idCreacion):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    if not permisos.paraCrear(request.user, Areas.Q, accion=Practica.Acciones.realizar):
        raise PermissionDenied()

    try:
        context = contextoCreacion(request, idCreacion)
    except VeterinariaPatagonicaError as error:
        context = { "errores": [error] }
    else:
        try:
            practica = obtenerPractica(request, idCreacion)
            verificarCreacion(practica, Practica.Acciones.realizar.name)

            detalles = obtenerDetalles(request, idCreacion)
            precio = calcularPrecio(detalles, practica.tipoDeAtencion.recargo)
            duracion = calcularDuracion(detalles["servicios"])

            if request.method == "POST":

                form = formRealizar(request.POST, practica=practica, duracion=duracion)
                if form.is_valid():
                    accion = form.accion()
                    datos = form.datos()
                    form.actualizarPractica()
                    try:
                        practica = persistir(request.user, practica, detalles, accion, datos)
                    except VeterinariaPatagonicaError as error:
                        context["errores"].append(error)
                    else:
                        eliminar(request.session, idCreacion)
                        return HttpResponseRedirect(pathVer(context["tipo"], practica.id))

            else:
                form = formRealizar(practica=practica, duracion=duracion)

            context["form"] = form
            context["practica"] = practica
            context["detalles"] = detalles
            context["precio"] = precio
            context["duracion"] = duracion
            context["accion"] = "Registrar realizacion"

        except VeterinariaPatagonicaError as error:
            context["errores"].append(error)

    template = loader.get_template(plantilla("crear", "realizada"))
    return HttpResponse(template.render(context, request))


def terminarCreacion(request, idCreacion):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    if not permisos.paraCrear(request.user, Areas.Q):
        raise PermissionDenied()

    context = contextoCreacion(request, idCreacion)
    eliminar(request.session, idCreacion)
    return HttpResponseRedirect(pathListar(Areas.Q.nombre()))


def programar(request, id):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    context = { "tipo" : Areas.Q.nombre(), "errores" : [] }

    try:
        practica = Practica.quirurgicas.get(id=id)
        verificarPractica(practica)
        verificarAccion(practica, Practica.Acciones.programar)
    except Practica.DoesNotExist as error:
        context["errores"].append(errorAccion(
            Practica.Acciones.programar,
            "Cirugia no encontrada"
        ))
    except VeterinariaPatagonicaError as error:
        context["errores"].append(error)
    else:

        if not permisos.paraPractica(request.user, Practica.Acciones.programar, practica):
            raise PermissionDenied()

        context = contextoModificacion(practica, "Guardar")
        precio = practica.total()
        duracion = practica.duracionTotalServicios()

        if request.method == "POST":
            form = formProgramar(request.POST, precio=precio, practica=practica, duracion
=duracion)

            if form.is_valid():
                accion = form.accion()
                datos = form.datos()
                form.actualizarPractica()

                try:
                    practica.save(force_update=True)
                    practica.hacer(request.user, accion, **datos)
                except VeterinariaPatagonicaError as error:
                    context["errores"].append(error)
                else:
                    return HttpResponseRedirect(pathVer(Areas.Q.nombre(), practica.id,))
        else:
            form = formProgramar(precio=precio, practica=practica, duracion=duracion)

        context["menu"] = menuAcciones(request.user, Practica.Acciones.programar, practica)
        context["form"] = form
        context["practica"] = practica
        context["accion"] = "Programar cirugia"

    template = loader.get_template(plantilla("actualizar", "programar"))
    return HttpResponse(template.render(context, request))


def reprogramar(request, id):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    context = { "tipo" : Areas.Q.nombre(), "errores" : [] }

    try:
        practica = Practica.quirurgicas.get(id=id)
        verificarPractica(practica)
        verificarAccion(practica, Practica.Acciones.reprogramar)
    except Practica.DoesNotExist as error:
        context["errores"].append(errorAccion(
            Practica.Acciones.reprogramar,
            "Cirugia no encontrada"
        ))
    except VeterinariaPatagonicaError as error:
        context["errores"].append(error)
    else:

        if not permisos.paraPractica(request.user, Practica.Acciones.reprogramar, practica):
            raise PermissionDenied()

        context = contextoModificacion(practica, "Guardar")

        if request.method == "POST":

            form = formReprogramar(request.POST, practica=practica)

            if form.is_valid():
                accion = form.accion()
                datos = form.datos()

                try:
                    practica.hacer(request.user, accion, **datos)
                except VeterinariaPatagonicaError as error:
                    context["errores"].append(error)
                else:
                    return HttpResponseRedirect(pathVer(Areas.Q.nombre(), practica.id,))
        else:
            form = formReprogramar(practica=practica)

        context["menu"] = menuAcciones(request.user, Practica.Acciones.reprogramar, practica)
        context["form"] = form
        context["practica"] = practica
        context["accion"] = "Reprogramar cirugia"

    template = loader.get_template(plantilla("actualizar", "reprogramar"))
    return HttpResponse(template.render(context, request))


def realizar(request, id):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    context = { "tipo" : Areas.Q.nombre(), "errores" : [] }

    try:
        practica = Practica.quirurgicas.get(id=id)
        verificarPractica(practica)
        verificarAccion(practica, Practica.Acciones.realizar)
    except Practica.DoesNotExist as error:
        context["errores"].append(errorAccion(
            Practica.Acciones.realizar,
            "Cirugia no encontrada"
        ))
    except VeterinariaPatagonicaError as error:
        context["errores"].append(error)
    else:

        if not permisos.paraPractica(request.user, Practica.Acciones.realizar, practica):
            raise PermissionDenied()

        context = contextoModificacion(practica, "Guardar")
        duracion = calcularDuracion(practica.practica_servicios.all())

        if request.method == "POST":

            form = formRealizar(request.POST, practica=practica, duracion=duracion)

            if form.is_valid():
                accion = form.accion()
                datos = form.datos()
                form.actualizarPractica()

                try:
                    practica.save(force_update=True)
                    practica.hacer(request.user, accion, **datos)
                except VeterinariaPatagonicaError as error:
                    context["errores"].append(error)
                else:
                    return HttpResponseRedirect(pathVer(Areas.Q.nombre(), practica.id,))

        else:
            form = formRealizar(practica=practica, duracion=duracion)

        context["menu"] = menuAcciones(request.user, Practica.Acciones.realizar, practica)
        context["form"] = form
        context["practica"] = practica
        context["accion"] = "Registrar realizacion de cirugia"

    template = loader.get_template(plantilla("actualizar", "realizar"))
    return HttpResponse(template.render(context, request))


def cancelar(request, id):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    context = { "tipo" : Areas.Q.nombre(), "errores" : [] }

    try:
        practica = Practica.quirurgicas.get(id=id)
        verificarAccion(practica, Practica.Acciones.cancelar)
    except Practica.DoesNotExist as error:
        context["errores"].append(errorAccion(
            Practica.Acciones.cancelar,
            "Cirugia no encontrada"
        ))
    except VeterinariaPatagonicaError as error:
        context["errores"].append(error)
    else:

        if not permisos.paraPractica(request.user, Practica.Acciones.cancelar, practica):
            raise PermissionDenied()

        context = contextoModificacion(practica, "Guardar")

        if request.method == "POST":

            form = CanceladaForm(request.POST)

            if form.is_valid():
                accion = form.accion()
                datos = form.datos()

                try:
                    practica.hacer(request.user, accion, **datos)
                except VeterinariaPatagonicaError as error:
                    context["errores"].append(error)
                else:
                    return HttpResponseRedirect(pathVer(Areas.Q.nombre(), practica.id,))

        else:

            form = CanceladaForm()

        context["menu"] = menuAcciones(request.user, Practica.Acciones.cancelar, practica)
        context["form"] = form
        context["accion"] = "Cancelar cirugia"

    template = loader.get_template(plantilla("actualizar", "cancelar"))
    return HttpResponse(template.render(context, request))


def modificarRealizacion(request, id):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    context = { "tipo" : Areas.Q.nombre(), "accion" : None, "errores" : [] }

    try:
        practica = Practica.quirurgicas.get(id=id)
        verificarEstado(practica, [Realizada])
    except Practica.DoesNotExist as error:
        context["errores"].append(errorAccion(
            Practica.Acciones.modificar,
            "Cirugia no encontrada"
        ))
    except VeterinariaPatagonicaError as error:
        context["errores"].append(error)
    else:

        if not permisos.paraPractica(request.user, Practica.Acciones.modificar, practica):
            raise PermissionDenied()

        context["accion"] = "Guardar"
        realizada = practica.estado()

        if request.method == "POST":

            servicios = PracticaRealizadaServicioFormSet(request.POST, instancia=realizada, prefix="servicio_realizado")
            productos = PracticaRealizadaProductoFormSet(request.POST, instancia=realizada, prefix="producto_utilizado")

            if servicios.is_valid() and productos.is_valid():

                try:
                    with transaction.atomic():
                        servicios.save()
                        productos.save()
                        realizada.completarPrecio()
                except dbError as error:
                    context["errores"] = [errorAccion(
                        Practica.Acciones.modificar_realizacion,
                        "Error al guardar datos"
                    )]
                else:
                    return HttpResponseRedirect(pathVer(Areas.Q.nombre(), practica.id))

        else:
            servicios = PracticaRealizadaServicioFormSet(instancia=realizada, prefix="servicio_realizado")
            productos = PracticaRealizadaProductoFormSet(instancia=realizada, prefix="producto_utilizado")

        context["menu"] = menuAcciones(request.user, Practica.Acciones.modificar, practica)
        context["servicios"] = servicios
        context["productos"] = productos

    template = loader.get_template(plantilla("modificar", "realizacion"))
    return HttpResponse(template.render(context, request))


def modificarInformacionClinica(request, id):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    context = { "tipo" : Areas.Q.nombre(), "accion" : None, "errores" : [] }
    try:
        practica = Practica.quirurgicas.get(id=id)
        verificarEstado(practica, [Realizada])
    except Practica.DoesNotExist as error:
        context["errores"].append(errorAccion(
            Practica.Acciones.modificar_informacion_clinica,
            "Cirugia no encontrada"
        ))
    except VeterinariaPatagonicaError as error:
        context["errores"].append(error)
    else:

        if not permisos.paraPractica(request.user, Practica.Acciones.modificar_informacion_clinica, practica):
            raise PermissionDenied()

        context["accion"] = "Guardar"
        realizada = practica.estado()

        if request.method == "POST":

            generales = ObservacionesGeneralesForm(request.POST, instance=realizada, prefix="observaciones_generales")
            servicios = ObservacionesServiciosFormSet(request.POST, instance=realizada)

            if generales.is_valid() and servicios.is_valid():
                try:
                    generales.save()
                    servicios.save()
                except dbError as error:
                    context["errores"] = [errorAccion(
                        Practica.Acciones.modificar_informacion_clinica,
                        "Error al guardar datos"
                    )]
                else:
                    return HttpResponseRedirect(pathVer(Areas.Q.nombre(), practica.id))

        else:
            generales = ObservacionesGeneralesForm(instance=realizada, prefix="observaciones_generales")
            servicios = ObservacionesServiciosFormSet(instance=realizada)

        context["menu"] = menuAcciones(request.user, Practica.Acciones.modificar_informacion_clinica, practica)
        context["generales"] = generales
        context["servicios"] = servicios

    template = loader.get_template(plantilla("modificar", "informacionClinica"))
    return HttpResponse(template.render(context, request))


def verInformacionClinica(request, id):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    context = { "tipo" : Areas.Q.nombre(), "accion" : None, "errores" : [] }

    try:
        practica = Practica.quirurgicas.get(id=id)
        verificarEstado(practica, [Realizada, Facturada])
    except Practica.DoesNotExist as error:
        context["errores"].append(errorAccion(
            Practica.Acciones.ver_informacion_clinica,
            "Cirugia no encontrada"
        ))
    except VeterinariaPatagonicaError as error:
        context["errores"].append(error)
    else:

        if not permisos.paraPractica(request.user, Practica.Acciones.ver_informacion_clinica, practica):
            raise PermissionDenied()

        realizada = practica.estados.realizacion()

        context["accion"] = "Guardar"
        context["practica"] = practica,
        context["realizada"] = realizada,
        context["menu"] = menuAcciones(request.user, Practica.Acciones.ver_informacion_clinica, practica)


    template = loader.get_template(plantilla("ver", "informacionClinica"))
    return HttpResponse(template.render(context, request))


def reportePdf(practicas, hoy, dias):

    canvas = pdf.crear()

    y = pdf.A4[1] - pdf.MARGEN
    y = -54 + pdf.titulo(canvas, y, "Reporte de cirugias al %s" % hoy.strftime("%d/%m/%Y"), 15, 0.5)
    y = -54 + reportes.perfiles(canvas, y, practicas, hoy, dias["perfiles"])
    y = -54 + reportes.realizacionesPorDia(canvas, y, practicas, hoy, dias["realizaciones"])
    y = -54 + reportes.porcentajesActualizacion(canvas, y, practicas, Areas.Q, hoy, dias["actualizaciones"])
    y = -54 + reportes.tiposDeAtencion(canvas, y, practicas, hoy, dias["tiposdeatencion"])

    return pdf.terminar(canvas)


def reporte(request):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    if not request.user.has_perm("GestionDePracticas.ver_reporte_cirugia"):
        raise PermissionDenied()

    retorno = ""
    form = FiltradoReportesForm(request.GET)
    practicas = Practica.quirurgicas.all()
    hoy = datetime.now().date()
    dias = form.dias()

    if form.accion() == "pdf":
        contenido = reportePdf(practicas, hoy, dias)
        nombre = "reporte-cirugias-%s" % hoy.strftime("%Y%m%d")
        retorno = HttpResponse(contenido, content_type="application/pdf")
        retorno["Content-Disposition"] = "attachment; filename=%s.pdf" % nombre

    else:
        context = reporteHtml(Areas.Q, practicas, hoy, dias)
        context["form"] = form
        template = loader.get_template(plantilla("reportes"))
        retorno = HttpResponse(template.render(context, request))

    return retorno
