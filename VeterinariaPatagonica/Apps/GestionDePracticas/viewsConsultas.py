from django.db.utils import Error as ErrorBD
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone as djangotimezone

from VeterinariaPatagonica.areas import Areas
from VeterinariaPatagonica.errores import VeterinariaPatagonicaError
from .models.practica import Practica
from .models.estado import *
from .permisos import *
from .gestionDePracticas import *



def contextoCreacion(request, idCreacion, accion=None):
    return crearContexto(
        request,
        idCreacion,
        tipoPractica=Areas.C.nombre,
        accion=accion
    )



def contextoModificacion(practica, accion=None):
    return {
        "tipo" : Areas.C.nombre,
        "practica" : practica,
        "accion" : accion,
        "errores" : [],
    }



@login_required(redirect_field_name='proxima')
def listar(request):

    gestor = GestorListadoPractica(
        orden=[
            ["orden_id", "Consulta"],
            ["orden_cliente", "Cliente"],
            ["orden_mascota", "Mascota"],
            ["orden_actualizacion", "Ultima Actualizacion"],
        ],
        claseFiltros=FiltradoConsultaForm,
    )

    practicas = Practica.consultas.conEstadoActual()
    gestor.cargar(request, practicas, clase=Practica)

    if gestor.formFiltros.is_valid():
        gestor.filtrar()
        gestor.ordenar()

    template = loader.get_template( plantilla("listar") )
    context = {"tipo" : Areas.C.nombre, "gestor" : gestor}

    return HttpResponse(template.render( context, request ))



@login_required(redirect_field_name='proxima')
def ver(request, id):

    practica = Practica.consultas.get(id=id)
    estados = practica.estados.all()
    tope = estados.count()

    try:
        n = int( request.GET["estado"] )
    except (ValueError, KeyError):
        n = 0

    n = n if (0 < n < tope) else tope-1
    estado = estados[n].related()

    acciones = crearUrls(
        [
            Practica.Acciones.realizar,
            Practica.Acciones.cancelar,
            Practica.Acciones.facturar,
        ],
        practica,
        request.user
    )

    context = {
        "practica" : practica,
        "estado" : estado,
        "acciones" :  acciones,
    }

    template = loader.get_template(plantilla(str(estado).lower()))
    return HttpResponse(template.render( context, request ))



@login_required(redirect_field_name='proxima')
def buscar(request):

    gestor = GestorListadoPractica(claseFiltros=BusquedaConsultaForm)
    gestor.cargar(
        request,
        Practica.consultas.none(),
        clase=Practica
    )

    if gestor.formFiltros.is_valid() and gestor.formFiltros.filtros():
        gestor.actualizar(Practica.consultas.conEstadoActual())
        gestor.filtrar()

    context = {
        "tipo" : Areas.C.nombre,
        "gestor" : gestor,
    }

    template = loader.get_template( plantilla("buscar") )
    return HttpResponse(template.render( context, request ))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CREAR, raise_exception=True)
def crear(request):

    context = { "tipo" : Areas.C.nombre, "errores" : [] }

    try:
        acciones = accionesIniciales(request.user, Areas.C)

        if request.method == "POST":

            formCreacion = CreacionForm(acciones, request.POST, vacio="Guardar")
            formPractica = PracticaForm(request.POST)
            formsetServicios = CirugiaServicioFormSet(request.POST, prefix="servicio")

            if formPractica.is_valid() and formsetServicios.is_valid() and formCreacion.is_valid():

                idCreacion = idCrearPractica(request.session)
                servicios = formsetServicios.cleaned_data
                accion = formCreacion.accion

                guardar(request.session, idCreacion, "tipo", Areas.C.nombre)
                guardar(request.session, idCreacion, "practicaData", formPractica.data)
                guardar(request.session, idCreacion, "serviciosData", servicios)

                try:
                    productos = buscarProductos(servicios)
                except VeterinariaPatagonicaError as error:
                    context["errores"].append( errorDatos(error, Areas.C.nombre, idCreacion) )
                else:
                    guardar(request.session, idCreacion, "productosData", productos)

                    if accion:
                        return HttpResponseRedirect(pathInicializar(Areas.C.nombre, accion, idCreacion))

                    return HttpResponseRedirect(pathModificar(Areas.C.nombre, idCreacion))
        else:

            formCreacion = CreacionForm(acciones, vacio="Guardar")
            formPractica = PracticaForm()
            formsetServicios = CirugiaServicioFormSet(prefix="servicio")

        context["formPractica"] = formPractica
        context["formsetServicios"] = formsetServicios
        context["acciones"] = formCreacion


    except VeterinariaPatagonicaError as error:
        context["errores"] .append( errorSolicitud(error) )

    template = loader.get_template(plantilla('crear'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CREAR, raise_exception=True)
def modificar(request, idCreacion):

    try:
        context = contextoCreacion(request, idCreacion)
    except VeterinariaPatagonicaError as error:
        context = { "errores": [errorSolicitud(error, Areas.C.nombre)] }
    else:

        acciones = accionesIniciales(request.user, Areas.C)

        if request.method == "POST":

            formCreacion = CreacionForm(acciones, request.POST, vacio="Guardar")
            formPractica = PracticaForm(request.POST)
            formsetServicios = CirugiaServicioFormSet(request.POST, prefix="servicio")

            if formPractica.is_valid() and formsetServicios.is_valid() and formCreacion.is_valid():

                accion = formCreacion.accion
                servicios = formsetServicios.cleaned_data

                try:
                    productos = buscarProductos(servicios)
                except VeterinariaPatagonicaError as error:
                    context["errores"].append( errorDatos(error, Areas.C.nombre, idCreacion) )
                else:

                    guardar(request.session, idCreacion, "practicaData", formPractica.data)
                    guardar(request.session, idCreacion, "serviciosData", servicios)
                    guardar(request.session, idCreacion, "productosData", productos)

                    if accion:
                        return HttpResponseRedirect(pathInicializar(Areas.C.nombre, accion, idCreacion))
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
                servicios = {}
            formsetServicios = CirugiaServicioFormSet(initial=servicios, prefix="servicio")

            formCreacion = CreacionForm(acciones, vacio="Guardar")

        practica = obtenerPractica(request, idCreacion)
        detalles = obtenerDetalles(request, idCreacion)
        precio = calcularPrecio(detalles, practica.tipoDeAtencion.recargo)
        duracion = calcularDuracion(detalles["servicios"])
        context["practica"] = practica
        context["servicios"] = detalles["servicios"]
        context["precio"] = precio
        context["duracion"] = duracion

        context["formPractica"] = formPractica
        context["formsetServicios"] = formsetServicios
        context["acciones"] = formCreacion

    template = loader.get_template(plantilla('modificar'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CREAR, raise_exception=True)
def modificarProductos(request, idCreacion):

    try:
        context = contextoCreacion(request, idCreacion)
    except VeterinariaPatagonicaError as error:
        context = { "errores": [errorSolicitud(error, Areas.C.nombre)] }
    else:

        acciones = accionesIniciales(request.user, Areas.C)

        practica = obtenerPractica(request, idCreacion)

        if request.method == "POST":

            formCreacion = CreacionForm(acciones, request.POST, vacio="Guardar")
            formset = PracticaProductoFormSet(request.POST, prefix="producto")

            if formset.is_valid() and formCreacion.is_valid():

                accion = formCreacion.accion
                guardar(request.session, context["id"], "productosData", formset.cleaned_data)

                if accion:
                    return HttpResponseRedirect(pathInicializar(context["tipo"], accion, context["id"]))

        else:
            try:
                productosInitial = obtener(request.session, context["id"], "productosData")
            except VeterinariaPatagonicaError as error:
                context["errores"].append(errorDatos(error))
                productosInitial = {}

            formset = PracticaProductoFormSet(initial=productosInitial, prefix="producto")
            formCreacion = CreacionForm(acciones, vacio="Guardar")

        detalles = obtenerDetalles(request, idCreacion)
        precio = calcularPrecio(detalles, practica.tipoDeAtencion.recargo)
        duracion = calcularDuracion(detalles["servicios"])
        context["formset"] = formset
        context["practica"] = practica
        context["servicios"] = detalles["servicios"]
        context["precio"] = precio
        context["duracion"] = duracion
        context["acciones"] = formCreacion

    template = loader.get_template(plantilla('productos'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CREAR+PERMISOS_PRESUPUESTAR, raise_exception=True)
def crearPresupuestada(request, idCreacion):

    try:
        context = contextoCreacion(request, idCreacion, Practica.Acciones.presupuestar.name)
    except VeterinariaPatagonicaError as error:
        context = { "errores": [errorSolicitud(error, Areas.C.nombre)] }
    else:

        try:
            practica = obtenerPractica(request, idCreacion)
            detalles = obtenerDetalles(request, idCreacion)
            precio = calcularPrecio(detalles, practica.tipoDeAtencion.recargo)
            duracion = calcularDuracion(detalles["servicios"])

            if request.method == "POST":

                form = formPresupuestar(request.POST, practica=practica)
                if form.is_valid():
                    accion = form.accion
                    datos = form.datos
                    form.actualizarPractica()

                    try:
                        practica = persistir(practica, detalles, accion, datos)
                    except ErrorBD as error:
                        context["errores"].append(errorBD(**context))
                    else:
                        eliminar(request.session, idCreacion)
                        return HttpResponseRedirect(pathVer(context["tipo"], practica.pk))

            else:
                form = formPresupuestar(practica=practica)

            context["form"] = form
            context["practica"] = practica
            context["servicios"] = detalles["servicios"]
            context["precio"] = precio
            context["duracion"] = duracion
            context["accion"] = "Crear presupuesto"


        except VeterinariaPatagonicaError as error:
            context["errores"].append(errorDatos(error, **context))

    template = loader.get_template(plantilla('crearPresupuestada'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CREAR+PERMISOS_REALIZAR, raise_exception=True)
def crearRealizada(request, idCreacion):

    try:
        context = contextoCreacion(request, idCreacion, Practica.Acciones.realizar.name)
    except VeterinariaPatagonicaError as error:
        context = { "errores": [errorSolicitud(error, Areas.C.nombre)] }
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
                    accion = form.accion
                    datos = form.datos
                    form.actualizarPractica()

                    try:
                        practica = persistir(practica, detalles, accion, datos)
                    except ErrorBD as error:
                        context["errores"].append(errorBD(**context))
                    else:
                        eliminar(request.session, idCreacion)
                        return HttpResponseRedirect(pathVer(context["tipo"], practica.pk))

            else:
                form = formRealizar(practica=practica, duracion=duracion)

            context["form"] = form
            context["practica"] = practica
            context["servicios"] = detalles["servicios"]
            context["precio"] = precio
            context["duracion"] = duracion
            context["accion"] = "Registrar realizacion"

        except VeterinariaPatagonicaError as error:
            context["errores"].append(errorDatos(error, **context))

    template = loader.get_template(plantilla('crearRealizada'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CREAR, raise_exception=True)
def terminarCreacion(request, idCreacion):

    try:
        context = contextoCreacion(request, idCreacion)
    except VeterinariaPatagonicaError as error:
        context = { "errores": [errorSolicitud(error, Areas.C.nombre)] }
    else:
        eliminar(request.session, idCreacion)
        return HttpResponseRedirect(pathListar(Areas.C.nombre))

    template = loader.get_template("error.html")
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_REALIZAR, raise_exception=True)
def realizar(request, id):

    try:
        practica = Practica.consultas.get(id=id)
        verificarPractica(practica)
        verificarAccion(practica, Practica.Acciones.realizar)
    except VeterinariaPatagonicaError as error:
        context = { "tipo" : Areas.C.nombre, "errores" : [errorSolicitud(error)] }
    else:

        context = contextoModificacion(practica, "Guardar")
        duracion = calcularDuracion(practica.practica_servicios.all())

        if request.method == 'POST':

            form = formRealizar(request.POST, practica=practica, duracion=duracion)

            if form.is_valid():
                accion = form.accion
                datos = form.datos
                form.actualizarPractica()

                try:
                    practica.save(force_update=True)
                    practica.hacer(accion, **datos)
                except VeterinariaPatagonicaError as error:
                    context["errores"].append(errorAccion(practica, accion))
                else:
                    return HttpResponseRedirect(pathVer(Areas.C.nombre, practica.pk,))

        else:
            form = formRealizar(practica=practica, duracion=duracion)

        context["form"] = form
        context["practica"] = practica
        context["servicios"] = practica.practica_servicios.all()
        context["precio"] = practica.total()
        context["duracion"] = duracion
        context["accion"] = "Registrar realizacion"

    template = loader.get_template(plantilla('realizar'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CANCELAR, raise_exception=True)
def cancelar(request, id):

    try:
        practica = Practica.consultas.get(id=id)
        verificarAccion(practica, Practica.Acciones.cancelar)
    except VeterinariaPatagonicaError as error:
        context = { "tipo" : Areas.C.nombre, "errores" : [errorSolicitud(error)] }
    else:

        context = contextoModificacion(practica, "Guardar")

        if request.method == 'POST':

            form = CanceladaForm(request.POST)

            if form.is_valid():
                accion = form.accion
                datos = form.datos

                try:
                    practica.hacer(accion, **datos)
                except VeterinariaPatagonicaError as error:
                    context["errores"].append(errorAccion(practica, accion))
                else:
                    return HttpResponseRedirect(pathVer(Areas.C.nombre, practica.pk,))

        else:

            form = CanceladaForm()

        context["form"] = form
        context["accion"] = "Completar cancelacion"

    template = loader.get_template(plantilla('cancelar'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_DETALLES, raise_exception=True)
def modificarDetalles(request, id):

    try:
        practica = Practica.consultas.get(id=id)
        verificarEstado(practica, [Realizada])
    except VeterinariaPatagonicaError as error:
        context = { "tipo" : Areas.C.nombre, "errores" : [errorSolicitud(error)] }
    else:
        realizada = practica.estado()
        context = { "tipo" : Areas.C.nombre, "accion" : "Guardar" }

        if request.method == "POST":

            servicios = ConsultaRealizadaServicioFormSet(request.POST, instancia=realizada, prefix="servicio_realizado")
            productos = PracticaRealizadaProductoFormSet(request.POST, instancia=realizada, prefix="producto_utilizado")

            if servicios.is_valid() and productos.is_valid():
                try:
                    servicios = servicios.save()
                    productos = productos.save()
                    realizada.completarPrecio()
                except ErrorBD as error:
                    context["errores"] = [ errorBD() ]
                else:
                    return HttpResponseRedirect(pathVer(Areas.C.nombre, practica.pk))

        else:
            servicios = ConsultaRealizadaServicioFormSet(instancia=realizada, prefix="servicio_realizado")
            productos = PracticaRealizadaProductoFormSet(instancia=realizada, prefix="producto_utilizado")

        context["servicios"] = servicios
        context["productos"] = productos

    template = loader.get_template(plantilla("modificarDetalles"))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_DETALLES, raise_exception=True)
def modificarObservaciones(request, id):

    try:
        practica = Practica.consultas.get(id=id)
        verificarEstado(practica, [Realizada])
    except VeterinariaPatagonicaError as error:
        context = { "tipo" : Areas.C.nombre, "errores" : [errorSolicitud(error)] }
    else:
        realizada = practica.estado()
        context = { "tipo" : Areas.C.nombre, "accion" : "Guardar" }

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
                    return HttpResponseRedirect(pathVer(Areas.C.nombre, practica.pk))

        else:
            generales = ObservacionesGeneralesForm(instance=realizada, prefix="observaciones_generales")
            servicios = ObservacionesServiciosFormSet(instance=realizada)

        context["generales"] = generales
        context["servicios"] = servicios

    template = loader.get_template(plantilla("modificarObservaciones"))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_DETALLES, raise_exception=True)
def verObservaciones(request, id):

    try:
        practica = Practica.consultas.get(id=id)
        verificarEstado(practica, [Realizada, Facturada])
    except VeterinariaPatagonicaError as error:
        context = { "tipo" : Areas.C.nombre, "errores" : [errorSolicitud(error)] }
    else:
        realizada = practica.estados.realizacion()
        context = {
            "tipo" : Areas.C.nombre,
            "practica" : practica,
            "realizada" : realizada,
        }

    template = loader.get_template(plantilla("verObservaciones"))
    return HttpResponse(template.render(context, request))
