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
def listar(request, pagina=1):

    practicas = Practica.consultas.all()
    formFiltrado = FiltradoConsultaForm(request.GET)
    if formFiltrado.is_valid():
        practicas = practicas.filtrar(formFiltrado.filtros())
        practicas = practicas.ordenar(formFiltrado.criterio(), formFiltrado.ascendente())

    paginas = calcularPaginas(practicas)
    practicas = practicasParaPagina(practicas, pagina, paginas)

    template = loader.get_template( plantilla("listar") )
    context = {
        "tipo" : Areas.C.nombre,
        "filtrado" : formFiltrado,
        "pagina" : pagina,
        "practicas" : practicas,
        "paginas" : [ i+1 for i in range(paginas)],
        "acciones" :  list(Practica.Acciones),
        "action" : pathListar(Areas.C.nombre),
    }

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

    context = {
        "practica" : practica,
        "estado" : estado,
        "acciones" :  list(Practica.Acciones),
    }

    template = loader.get_template(plantilla(str(estado).lower()))
    return HttpResponse(template.render( context, request ))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CREAR, raise_exception=True)
def crear(request):

    context = { "tipo" : Areas.C.nombre, "errores" : [] }

    try:
        acciones = accionesIniciales(request.user, Areas.C)

        if request.method == "POST":

            formCreacion = CreacionForm(acciones, request.POST)
            formPractica = PracticaForm(request.POST)
            formsetServicios = ConsultaServicioFormSet(request.POST, prefix="servicio")

            if formPractica.is_valid() and formsetServicios.is_valid() and formCreacion.is_valid():

                verificarCreacion(formPractica, formsetServicios, formCreacion)
                idCreacion = idCrearPractica(request.session)
                accion = formCreacion.accion
                servicios = formsetServicios.cleaned_data

                guardar(request.session, idCreacion, "tipo", Areas.C.nombre)
                guardar(request.session, idCreacion, "accion", accion)
                guardar(request.session, idCreacion, "practicaData", formPractica.data)
                guardar(request.session, idCreacion, "serviciosData", servicios)

                try:
                    productos = buscarProductos(servicios)
                except VeterinariaPatagonicaError as error:
                    context["errores"].append( errorDatos(error, Areas.C.nombre, idCreacion) )
                else:
                    guardar(request.session, idCreacion, "productosData", productos)

                    if formCreacion.modificarProductos:
                        return HttpResponseRedirect(pathModificarProductos(Areas.C.nombre, idCreacion))
                    return HttpResponseRedirect(pathInicializar(Areas.C.nombre, accion, idCreacion))
        else:

            formCreacion = CreacionForm(acciones)
            formPractica = PracticaForm()
            formsetServicios = ConsultaServicioFormSet(prefix="servicio")

        context["practica"] = formPractica
        context["servicios"] = formsetServicios
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
        acciones = (Practica.Acciones[context["accion"]], )

        if request.method == "POST":

            formCreacion = CreacionForm(acciones, request.POST)
            formPractica = PracticaForm(request.POST)
            formsetServicios = ConsultaServicioFormSet(request.POST, prefix="servicio")
            if formPractica.is_valid() and formsetServicios.is_valid() and formCreacion.is_valid():

                servicios = formsetServicios.cleaned_data
                try:
                    productos = buscarProductos(servicios)
                except VeterinariaPatagonicaError as error:
                    context["errores"].append( errorDatos(error, Areas.C.nombre, idCreacion) )
                else:
                    guardar(request.session, idCreacion, "practicaData", formPractica.data)
                    guardar(request.session, idCreacion, "serviciosData", servicios)
                    guardar(request.session, idCreacion, "productosData", productos)

                    if formCreacion.modificarProductos:
                        return HttpResponseRedirect(pathModificarProductos(Areas.C.nombre, idCreacion))
                    return HttpResponseRedirect(pathInicializar(Areas.C.nombre, context["accion"], idCreacion))
        else:

            try:
                data = obtener(request.session, idCreacion, "practicaData")
            except VeterinariaPatagonicaError as error:
                context["errores"].append(errorDatos(error))
                data = None
            formPractica = PracticaForm(data)

            try:
                initial = obtener(request.session, idCreacion, "serviciosData")
            except VeterinariaPatagonicaError as error:
                context["errores"].append(errorDatos(error))
                initial = {}
            formsetServicios = ConsultaServicioFormSet(initial=initial, prefix="servicio")

            formCreacion = CreacionForm(acciones)

        context["practica"] = formPractica
        context["acciones"] = formCreacion
        context["servicios"] = formsetServicios

    template = loader.get_template(plantilla('crear'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CREAR, raise_exception=True)
def modificarProductos(request, idCreacion):

    try:
        context = contextoCreacion(request, idCreacion)
    except VeterinariaPatagonicaError as error:
        context = { "errores": [errorSolicitud(error, Areas.C.nombre)] }
    else:

        if request.method == "POST":

            formset = PracticaProductoFormSet(request.POST, prefix="producto")

            if formset.is_valid():
                guardar(request.session, context["id"], "productosData", formset.cleaned_data)
                return HttpResponseRedirect(pathInicializar(context["tipo"], context["accion"], context["id"]))

        else:
            try:
                productosInitial = obtener(request.session, context["id"], "productosData")
            except VeterinariaPatagonicaError as error:
                context["errores"].append(errorDatos(error))
                productosInitial = {}

            formset = PracticaProductoFormSet(initial=productosInitial, prefix="producto")


        context["formset"] = formset
        context["accion"] = "Continuar"

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
            precio = calcularPrecio(practica, detalles)

            if request.method == "POST":

                form = formNuevoPresupuesto(practica, request.POST)
                if form.is_valid():
                    accion = form.accion
                    datos = form.datos
                    practica.mascota = form.cleaned_data["mascota"]

                    try:
                        practica = persistir(practica, detalles, accion, datos)
                    except ErrorBD as error:
                        context["errores"].append(errorBD(**context))
                    else:
                        eliminar(request.session, idCreacion)
                        return HttpResponseRedirect(pathVer(context["tipo"], practica.pk))

            else:
                form = formNuevoPresupuesto(practica)

            context["form"] = form
            context["accion"] = "Crear presupuesto"


        except VeterinariaPatagonicaError as error:
            context["errores"].append(errorDatos(error, **context))

    template = loader.get_template(plantilla('inicializar'))
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
            detalles = obtenerDetalles(request, idCreacion)
            precio = calcularPrecio(practica, detalles)

            if request.method == "POST":

                form = formNuevaRealizacion(practica, request.POST)
                if form.is_valid():
                    accion = form.accion
                    datos = form.datos
                    practica.mascota = form.cleaned_data["mascota"]

                    try:
                        practica = persistir(practica, detalles, accion, datos)
                    except ErrorBD as error:
                        context["errores"].append(errorBD(**context))
                    else:
                        eliminar(request.session, idCreacion)
                        return HttpResponseRedirect(pathDetallarRealizacion(context["tipo"], practica.pk))

            else:
                form = formNuevaRealizacion(practica)

            context["form"] = form
            context["accion"] = "Guardar "+Areas.C.nombre

        except VeterinariaPatagonicaError as error:
            context["errores"].append(errorDatos(error, **context))

    template = loader.get_template(plantilla('inicializar'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CREAR, raise_exception=True)
def terminar(request, idCreacion):

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

        if practica.enEstado(Presupuestada) and (not practica.estado().estaCompleto()):
            return HttpResponseRedirect(pathCompletarPresupuesto(
                practica.nombreTipo(),
                practica.id,
                Practica.Acciones.realizar.value
            ))

        context = contextoModificacion(practica, "Guardar")

        if request.method == 'POST':

            form = formRealizacion(practica, request.POST)

            if form.is_valid():
                accion = form.accion
                datos = form.datos

                try:
                    practica.hacer(accion, **datos)
                except VeterinariaPatagonicaError as error:
                    context["errores"].append(errorAccion(practica, accion))
                else:
                    return HttpResponseRedirect(pathDetallarRealizacion(Areas.C.nombre, practica.pk,))

        else:
            form = formRealizacion(practica)

        context["form"] = form

    template = loader.get_template(plantilla('actualizar'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_FACTURAR, raise_exception=True)
def facturar(request, id):

    try:
        practica = Practica.consultas.get(id=id)
        verificarAccion(practica, Practica.Acciones.facturar)
    except VeterinariaPatagonicaError as error:
        context = { "tipo" : Areas.C.nombre, "errores" : [errorSolicitud(error)] }
    else:

        context = contextoModificacion(practica, "Guardar")

        if request.method == 'POST':

            form = ConfirmarFacturacionForm(request.POST)

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

            form = ConfirmarFacturacionForm()

        context["form"] = form

    template = loader.get_template(plantilla('actualizar'))
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

    template = loader.get_template(plantilla('actualizar'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_DETALLES, raise_exception=True)
def detallarRealizacion(request, id):

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
                except ErrorBD as error:
                    context["errores"] = [ errorBD() ]
                else:
                    return HttpResponseRedirect(pathVer(Areas.C.nombre, practica.pk))

        else:
            servicios = ConsultaRealizadaServicioFormSet(instancia=realizada, prefix="servicio_realizado")
            productos = PracticaRealizadaProductoFormSet(instancia=realizada, prefix="producto_utilizado")

        context["servicios"] = servicios
        context["productos"] = productos

    template = loader.get_template(plantilla("realizacion"))
    return HttpResponse(template.render(context, request))



@login_required
def detalles(request, id):

    context = {
        "tipo" : Areas.C.nombre,
        "errores" : [],
    }

    try:
        practica = Practica.consultas.get(id=id)
    except VeterinariaPatagonicaError as error:
        context["errores"].append(errorSolicitud(error))
    else:
        context["practica"] = practica

    template = loader.get_template(plantilla("detalles"))
    return HttpResponse(template.render(context, request))
