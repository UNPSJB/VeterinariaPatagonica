from datetime import datetime

from django.db import transaction
from django.db.utils import Error as ErrorBD
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
from .views import listarXlsx
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
    visibles = [ gestor[campo]["visible"] for campo in gestor.columnas ]
    encabezados = [ gestor[campo]["etiqueta"] for campo in gestor.columnasVisibles ]

    if formato=="xlsx":
        listar=listarXlsx

    if accion=="exportar_pagina":
        response = listar(Areas.C.nombre(), gestor.itemsActuales(), visibles, encabezados)
    elif accion=="exportar_todos":
        response = listar(Areas.C.nombre(), gestor.items(), visibles, encabezados)
    else:
        template = loader.get_template(plantilla("exportar", "cirugias"))
        context = {
            "formato" : formato,
            "gestor" : gestor,
            "exportar" : exportar,
            "menu" : menuExportar(request.user, formato, Areas.Q),
        }
        response = HttpResponse(template.render(context, request))
    return response


def ver(request, id):

    usuario = request.user
    if isinstance(usuario, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (config("login_url"), request.path))

    acciones = Practica.Acciones.ver_informacion_general
    practica = Practica.quirurgicas.get(id=id)
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

    try:
        acciones = accionesIniciales(request.user, Areas.Q)

        if request.method == "POST":

            formCreacion = CreacionForm(acciones, request.POST)
            formPractica = PracticaForm(request.POST)
            formsetServicios = CirugiaServicioFormSet(request.POST, prefix="servicio")

            if formPractica.is_valid() and formsetServicios.is_valid() and formCreacion.is_valid():

                idCreacion = idCrearPractica(request.session)
                servicios = formsetServicios.cleaned_data
                accion = formCreacion.accion()

                guardar(request.session, idCreacion, "tipo", Areas.Q.nombre())
                guardar(request.session, idCreacion, "practicaData", formPractica.data)
                guardar(request.session, idCreacion, "serviciosData", servicios)

                try:
                    productos = buscarProductos(servicios)
                except VeterinariaPatagonicaError as error:
                    context["errores"].append( errorDatos(error, Areas.Q.nombre(), idCreacion) )
                else:
                    guardar(request.session, idCreacion, "productosData", productos)

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


    except VeterinariaPatagonicaError as error:
        context["errores"] .append( errorSolicitud(error) )

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
        context = { "errores": [errorSolicitud(error, Areas.Q.nombre())] }
    else:

        acciones = accionesIniciales(request.user, Areas.Q)

        if request.method == "POST":

            formCreacion = CreacionForm(acciones, request.POST)
            formPractica = PracticaForm(request.POST)
            formsetServicios = CirugiaServicioFormSet(request.POST, prefix="servicio")

            if formPractica.is_valid() and formsetServicios.is_valid() and formCreacion.is_valid():

                accion = formCreacion.accion()
                servicios = formsetServicios.cleaned_data

                try:
                    productos = buscarProductos(servicios)
                except VeterinariaPatagonicaError as error:
                    context["errores"].append( errorDatos(error, Areas.Q.nombre(), idCreacion) )
                else:

                    guardar(request.session, idCreacion, "practicaData", formPractica.data)
                    guardar(request.session, idCreacion, "serviciosData", servicios)
                    guardar(request.session, idCreacion, "productosData", productos)

                    if accion:
                        return HttpResponseRedirect(pathInicializar(Areas.Q.nombre(), accion, idCreacion))
        else:

            try:
                data = obtener(request.session, idCreacion, "practicaData")
            except VeterinariaPatagonicaError as error:
                context["errores"].append(errorDatos(error))
                data = None
            formPractica = PracticaForm(data)

            try:
                servicios = obtener(request.session, idCreacion, "serviciosData")
            except VeterinariaPatagonicaError as error:
                context["errores"].append(errorDatos(error))
                servicios = ()

            formsetServicios = CirugiaServicioFormSet(initial=servicios, prefix="servicio")
            formCreacion = CreacionForm(acciones)

        practica = obtenerPractica(request, idCreacion)
        detalles = obtenerDetalles(request, idCreacion)
        precio = calcularPrecio(detalles, practica.tipoDeAtencion.recargo)
        duracion = calcularDuracion(detalles["servicios"])
        context["practica"] = practica
        context["detalles"] = detalles
        context["precio"] = precio
        context["duracion"] = duracion

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
        context = { "errores": [errorSolicitud(error, Areas.Q.nombre())] }
    else:

        acciones = accionesIniciales(request.user, Areas.Q)
        practica = obtenerPractica(request, idCreacion)

        if request.method == "POST":

            formCreacion = CreacionForm(acciones, request.POST)
            formset = PracticaProductoFormSet(request.POST, prefix="producto")

            if formset.is_valid() and formCreacion.is_valid():

                accion = formCreacion.accion()
                guardar(request.session, context["id"], "productosData", formset.cleaned_data)

                if accion:
                    return HttpResponseRedirect(pathInicializar(context["tipo"], accion, context["id"]))

        else:
            try:
                productosInitial = obtener(request.session, context["id"], "productosData")
            except VeterinariaPatagonicaError as error:
                context["errores"].append(errorDatos(error))
                productosInitial = ()

            formset = PracticaProductoFormSet(initial=productosInitial, prefix="producto")
            formCreacion = CreacionForm(acciones)

        detalles = obtenerDetalles(request, idCreacion)
        precio = calcularPrecio(detalles, practica.tipoDeAtencion.recargo)
        duracion = calcularDuracion(detalles["servicios"])
        context["formset"] = formset
        context["practica"] = practica
        context["detalles"] = detalles
        context["precio"] = precio
        context["duracion"] = duracion
        context["acciones"] = formCreacion

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
        context = { "errores": [errorSolicitud(error, Areas.Q.nombre())] }
    else:
        try:
            practica = obtenerPractica(request, idCreacion)
            detalles = obtenerDetalles(request, idCreacion)
            precio = calcularPrecio(detalles, practica.tipoDeAtencion.recargo)
            duracion = calcularDuracion(detalles["servicios"])

            if request.method == "POST":

                form = formPresupuestar(request.POST, practica=practica)
                if form.is_valid():
                    accion = form.accion()
                    datos = form.datos()
                    form.actualizarPractica()

                    try:
                        practica = persistir(request.user, practica, detalles, accion, datos)
                    except ErrorBD as error:
                        context["errores"].append(errorBD(**context))
                    else:
                        eliminar(request.session, idCreacion)
                        return HttpResponseRedirect(pathVer(context["tipo"], practica.pk))

            else:
                form = formPresupuestar(practica=practica)

            context["form"] = form
            context["practica"] = practica
            context["detalles"] = detalles
            context["precio"] = precio
            context["duracion"] = duracion
            context["accion"] = "Crear presupuesto"


        except VeterinariaPatagonicaError as error:
            context["errores"].append(errorDatos(error, **context))

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
        context = { "errores": [errorSolicitud(error, Areas.Q.nombre())] }
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
                    except ErrorBD as error:
                        context["errores"].append(errorBD(**context))
                    else:
                        eliminar(request.session, idCreacion)
                        return HttpResponseRedirect(pathVer(context["tipo"], practica.pk))

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
            context["errores"].append(errorDatos(error, **context))

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
        context = { "errores": [errorSolicitud(error, Areas.Q.nombre())] }
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
                    except ErrorBD as error:
                        context["errores"].append(errorBD(**context))
                    except VeterinariaPatagonicaError as error:
                        context["errores"] = [ errorProducto(error) ]

                    else:
                        eliminar(request.session, idCreacion)
                        return HttpResponseRedirect(pathVer(context["tipo"], practica.pk))

            else:
                form = formRealizar(practica=practica, duracion=duracion)

            context["form"] = form
            context["practica"] = practica
            context["detalles"] = detalles
            context["precio"] = precio
            context["duracion"] = duracion
            context["accion"] = "Registrar realizacion"

        except VeterinariaPatagonicaError as error:
            context["errores"].append(errorDatos(error, **context))

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
    except VeterinariaPatagonicaError as error:
        context["errores"].append(errorSolicitud(error))
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
                    context["errores"].append(errorAccion(practica, accion))
                else:
                    return HttpResponseRedirect(pathVer(Areas.Q.nombre(), practica.pk,))
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

    try:
        practica = Practica.quirurgicas.get(id=id)
        verificarPractica(practica)
        verificarAccion(practica, Practica.Acciones.reprogramar)
    except VeterinariaPatagonicaError as error:
        context = { "tipo" : Areas.Q.nombre(), "errores" : [errorSolicitud(error)] }
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
                    context["errores"].append(errorAccion(practica, accion))
                else:
                    return HttpResponseRedirect(pathVer(Areas.Q.nombre(), practica.pk,))
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

    try:
        practica = Practica.quirurgicas.get(id=id)
        verificarPractica(practica)
        verificarAccion(practica, Practica.Acciones.realizar)
    except VeterinariaPatagonicaError as error:
        context = { "tipo" : Areas.Q.nombre(), "errores" : [errorSolicitud(error)] }
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
                    context["errores"].append(errorAccion(practica, accion, descripcion=error.descripcion))
                else:
                    return HttpResponseRedirect(pathVer(Areas.Q.nombre(), practica.pk,))

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

    try:
        practica = Practica.quirurgicas.get(id=id)
        verificarAccion(practica, Practica.Acciones.cancelar)
    except VeterinariaPatagonicaError as error:
        context = { "tipo" : Areas.Q.nombre(), "errores" : [errorSolicitud(error)] }
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
                    context["errores"].append(errorAccion(practica, accion))
                else:
                    return HttpResponseRedirect(pathVer(Areas.Q.nombre(), practica.pk,))

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

    try:
        practica = Practica.quirurgicas.get(id=id)
        verificarEstado(practica, [Realizada])
    except VeterinariaPatagonicaError as error:
        context = { "tipo" : Areas.Q.nombre(), "errores" : [errorSolicitud(error)] }
    else:

        if not permisos.paraPractica(request.user, Practica.Acciones.modificar, practica):
            raise PermissionDenied()

        realizada = practica.estado()
        context = { "tipo" : Areas.Q.nombre(), "accion" : "Guardar" }

        if request.method == "POST":

            servicios = PracticaRealizadaServicioFormSet(request.POST, instancia=realizada, prefix="servicio_realizado")
            productos = PracticaRealizadaProductoFormSet(request.POST, instancia=realizada, prefix="producto_utilizado")

            if servicios.is_valid() and productos.is_valid():

                try:
                    with transaction.atomic():
                        servicios.save()
                        productos.save()
                        realizada.completarPrecio()
                except ErrorBD as error:
                    context["errores"] = [ errorBD() ]
                except VeterinariaPatagonicaError as error:
                    context["errores"] = [ errorProducto(error) ]

                else:
                    return HttpResponseRedirect(pathVer(Areas.Q.nombre(), practica.pk))

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

    try:
        practica = Practica.quirurgicas.get(id=id)
        verificarEstado(practica, [Realizada])
    except VeterinariaPatagonicaError as error:
        context = { "tipo" : Areas.Q.nombre(), "errores" : [errorSolicitud(error)] }
    else:

        if not permisos.paraPractica(request.user, Practica.Acciones.modificar_informacion_clinica, practica):
            raise PermissionDenied()

        realizada = practica.estado()
        context = { "tipo" : Areas.Q.nombre(), "accion" : "Guardar" }

        if request.method == "POST":

            generales = ObservacionesGeneralesForm(request.POST, instance=realizada, prefix="observaciones_generales")
            servicios = ObservacionesServiciosFormSet(request.POST, instance=realizada)

            if generales.is_valid() and servicios.is_valid():
                try:
                    generales.save()
                    servicios.save()
                except ErrorBD as error:
                    context["errores"] = [ errorBD() ]
                else:
                    return HttpResponseRedirect(pathVer(Areas.Q.nombre(), practica.pk))

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

    try:
        practica = Practica.quirurgicas.get(id=id)
        verificarEstado(practica, [Realizada, Facturada])
    except VeterinariaPatagonicaError as error:
        context = { "tipo" : Areas.Q.nombre(), "errores" : [errorSolicitud(error)] }
    else:

        if not permisos.paraPractica(request.user, Practica.Acciones.ver_informacion_clinica, practica):
            raise PermissionDenied()

        realizada = practica.estados.realizacion()
        context = {
            "tipo" : Areas.Q.nombre(),
            "practica" : practica,
            "realizada" : realizada,
            "menu" : menuAcciones(request.user, Practica.Acciones.ver_informacion_clinica, practica)
        }

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


def reporteHtml(practicas, hoy, dias):

    fecha = hoy - timedelta(days=dias["perfiles"])
    antes, despues = reportes.clasificarRealizaciones(practicas, fecha)
    perfiles = {
        "dias" : dias["perfiles"],
        "fecha" : fecha,
        "datos" : {
            "antes" : reportes.datosPerfiles(
                reportes.contarRealizaciones(antes)
            ),
            "despues" : reportes.datosPerfiles(
                reportes.contarRealizaciones(despues)
            ),
        }
    }

    fecha = hoy - timedelta(days=dias["realizaciones"])
    realizacionesPorDia = {
        "dias" : dias["realizaciones"],
        "fecha" : fecha,
        "datos" : reportes.datosRealizacionesPorDia(
            reportes.realizacionesEntre(practicas, fecha, hoy)
        ),
    }

    fecha = hoy - timedelta(days=dias["actualizaciones"])
    seleccionadas = reportes.creadasEntre(practicas, fecha, hoy)
    porcentajesActualizacion = {
        "datos" : None,
        "dias" : dias["actualizaciones"],
        "fecha" : fecha,
    }
    if seleccionadas:
        porcentajesActualizacion["datos"] = reportes.datosPorcentajesActualizacion(
            reportes.calcularNiveles(seleccionadas, Areas.Q)
        )


    fecha = hoy - timedelta(days=dias["tiposdeatencion"])
    tdas = reportes.buscarTDA(practicas, fecha)
    habilitados = tdas.filter(baja=False)
    deshabilitados = tdas.filter(baja=True)
    tiposDeAtencion = {
        "fecha" : fecha,
        "dias" : dias["tiposdeatencion"],
        "habilitados" : habilitados.count(),
        "deshabilitados" : deshabilitados.count(),
    }
    if habilitados:
        normales, raros, descarte = reportes.clasificar(reportes.preparar(habilitados))
        tiposDeAtencion["normales"] = normales
        tiposDeAtencion["raros"] = raros
        tiposDeAtencion["descarte"] = descarte
        tiposDeAtencion["datos"] = {
            "normales" : reportes.datosTiposDeAtencion(normales),
            "raros" : reportes.datosTiposDeAtencion(raros),
        }


    return {
        "hoy" : hoy,
        "tipo" : Areas.Q.nombre(),
        "perfiles" : perfiles,
        "realizacionesPorDia" : realizacionesPorDia,
        "porcentajesActualizacion" : porcentajesActualizacion,
        "tiposDeAtencion" : tiposDeAtencion,
    }


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
        context = reporteHtml(practicas, hoy, dias)
        context["form"] = form
        template = loader.get_template(plantilla("reportes"))
        retorno = HttpResponse(template.render(context, request))

    return retorno
