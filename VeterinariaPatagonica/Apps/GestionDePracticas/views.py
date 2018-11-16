from os.path import join
from django.utils import timezone as djangotimezone
from django.urls import reverse
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Max
from django.core import serializers

from VeterinariaPatagonica.tools import paramsToFilter
from VeterinariaPatagonica.errores import VeterinariaPatagonicaError
from Apps.GestionDeProductos.models import Producto
from Apps.GestionDeServicios.models import Servicio, ServicioProducto
from Apps.GestionDeClientes.models import Cliente
from Apps.GestionDeTiposDeAtencion.models import TipoDeAtencion
from .forms import *
from .models import *
from .permisos import *



"""
    Los templates estan practicamente sin hacer, hay versiones incompletas y generales de
    lo que haria falta, podrian ser compartidos entre practicas y cirugias o no.

"""



PLANTILLAS = {
    "listar" : "listar",
    "ver" : "ver",
    "actualizar" : "actualizar",
    "crear" : "crear",
    "inicializar" : "inicializar",
    "detallar" : "detallar",
    "productos" : "productos",
}
def plantilla(nombre, subdirectorio=""):
    return join( "GestionDePracticas/", subdirectorio, PLANTILLAS[nombre]+".html")



# Extras ######################################################################



def idCrearPractica(session):
    """ Devuelve un identificador de alta para la sesion recibida """

    if not "practicas_crear_proxima" in session:
        session["practicas_crear_proxima"] = 0

    session["practicas_crear_proxima"] += 1

    return session["practicas_crear_proxima"]



def guardar(session, id, etiqueta, datos):
    """ Guarda 'datos' en la sesion para el alta con identificador 'id' y clave 'etiqueta' """

    clave = "practicas_crear_%d_%s" % (id, etiqueta)
    session[clave] = datos



def obtener(session, id, etiqueta):
    """ Retorna los datos con identificador 'id' y clave 'etiqueta' guardados en la sesion """

    clave = "practicas_crear_%d_%s" % (id, etiqueta)

    return session[clave]



def eliminar(session, id, etiquetas):
    """ Elimina los datos con identificador 'id' y clave 'etiqueta' guardados en la sesion """

    for etiqueta in etiquetas:
        clave = "practicas_crear_%d_%s" % (id, etiqueta)
        del session[clave]



def buscarProductos(servicios):
    """ Retorna nombre y cantidad de producto para el total de productos en 'servicios' """

    listado = []
    datos = {}

    for detalleServicio in servicios:

        if "DELETE" in detalleServicio and detalleServicio["DELETE"]:
            continue

        servicio = detalleServicio['servicio']
        cantidadServicio = detalleServicio['cantidad']

        for detalleProducto in servicio.servicio_productos.all():
            cantidadProducto = detalleProducto.cantidad
            producto = detalleProducto.producto

            if not producto in datos:
                datos[producto] = 0

            datos[producto] += cantidadServicio * cantidadProducto

    for producto, cantidad in datos.items():
        listado.append(
            {
                'producto' : producto,
                'cantidad' : cantidad
            }
        )

    return listado



def persistirPractica(session, idCreacion):
    """ Persiste una nueva practica segun los datos guardados en 'session' con id 'idCreacion' """

    tipo = obtener(session, idCreacion, "tipo")
    estadoInicial = obtener(session, idCreacion, "estadoInicial")

    practicaData = obtener(session, idCreacion, "practicaData")
    serviciosData = obtener(session, idCreacion, "serviciosData")
    productosData = obtener(session, idCreacion, "productosData")
    estadoInicialData = obtener(session, idCreacion, "estadoInicialData")

    PracticaForm = practicaFormFactory(tipo)
    ServiciosFormSet = practicaServicioFormSetFactory(tipo)
    ProductosFormSet = practicaProductoFormSetFactory(tipo)
    InicializacionForm = getInicializacionForm(estadoInicial)

    formPractica = recrearFormulario(PracticaForm, practicaData)
    practica = formPractica.save(commit=False)

    formsetServicios = recrearFormulario(ServiciosFormSet, serviciosData, instance=practica)
    formsetProductos = recrearFormulario(ProductosFormSet, productosData, instance=practica)
    formInicializacion = recrearFormulario(InicializacionForm, estadoInicialData)

    with transaction.atomic():
        practica.save()
        formsetServicios.save()
        formsetProductos.save()
        practica.hacer(formInicializacion.accion(), **formInicializacion.datos())

    return practica



#[TODO]: tener en cuenta excepciones
def crearPractica(sesion, id):

    practica = persistirPractica(sesion, id)

    eliminar(sesion, id, [
        "tipo",
        "estadoInicial",
        "practicaData",
        "serviciosData",
        "productosData",
        "estadoInicialData",
    ])

    return practica



def recrearFormulario(Form, *args, **kwargs):
    """ Instancia y valida un formulario de clase 'Form' pasandole el resto de argumentos recibidos """

    form = Form(*args, **kwargs)
    if form.is_valid():
        return form
    else:
        raise Exception("Error al recrear el formulario %s, los datos no son validos: %s" % (Form.__name__, str(form.errors)))



"""
    El filtrado de practicas para listados y actualizaciones esta sin terminar, las variables a
    tener en cuenta para buscar practicas pueden ser:

    Cliente:
        dni/cuit
        nombres/apellido
        tipo
    Mascota:
        nombre
        raza
        especie
    TipoDeAtencion:
        nombre
    Estado:
        inicial
        actual
    Marca:
        creacion
        ultima actualizacion
    Usuario:
        creacion
        ultima actualizacion
    Servicios:
        nombre
    Productos:
        nombre

    Habria que organizar las opciones que decidamos en un formulario y agregarle el autocomplete

"""



def filtrarPracticas(formFiltrado, practicas):
    """ retorna una version filtrada del queryset 'practicas' segun el formulario 'formFiltrado' """

    if formFiltrado.is_valid():
        filtros = formFiltrado.cleaned_data

        if filtros["estado"] or filtros["desde"] or filtros["hasta"]:
            practicas = practicas.annotate(max_id=Max('estados__id'))

        return practicas.filter(paramsToFilter(filtros, Practica))

    return practicas



# Views #######################################################################



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CREAR, raise_exception=True)
def crearProductos(request, idCreacion):

    tipo = obtener(request.session, idCreacion, "tipo")
    ProductosFormSet = practicaProductoFormSetFactory(tipo)

    if request.method == "POST":

        formsetProductos = ProductosFormSet(request.POST)

        if formsetProductos.is_valid():

            guardar(request.session, idCreacion, "productosData", formsetProductos.data)
            estadoInicial = obtener(request.session, idCreacion, "estadoInicial")

            return HttpResponseRedirect(reverse("practicas:"+tipo+":crear:"+estadoInicial, args=(idCreacion,)))

    else:

        serviciosData = obtener(request.session, idCreacion, "serviciosData")
        ServiciosFormSet = practicaServicioFormSetFactory(tipo)
        formsetServicios = recrearFormulario(ServiciosFormSet, serviciosData)
        productosInitial = buscarProductos(formsetServicios.cleaned_data)

        formsetProductos = ProductosFormSet(initial=productosInitial)

    context = {
        "tipo" : tipo,
        "formset" : formsetProductos,
        "formAction" : reverse("practicas:"+tipo+":crear:productos", args=(idCreacion,)),
        "accion" : "Modificar",
    }

    template = loader.get_template(plantilla('productos'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CREAR+PERMISOS_PRESUPUESTAR, raise_exception=True)
def crearPresupuestada(request, idCreacion):

    tipo = obtener(request.session, idCreacion, "tipo")
    InicializacionForm = PresupuestadaForm

    if request.method == "POST":

        formInicializacion = InicializacionForm(request.POST)

        if formInicializacion.is_valid():

            guardar(request.session, idCreacion, "estadoInicialData", formInicializacion.data)
            practica = crearPractica(request.session, idCreacion)

            return HttpResponseRedirect(reverse("practicas:"+tipo+":ver", args=(practica.pk,)))

    else:

        formInicializacion = InicializacionForm()

    context = {
        "tipo" : tipo,
        "formEstado" : formInicializacion,
        "formAction" : reverse("practicas:"+tipo+":crear:presupuestada", args=(idCreacion,)),
        "accion" : "Crear",
    }

    #template = loader.get_template(plantilla('inicializar'))
    template = loader.get_template('GestionDePracticas/inicializar.html')
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CREAR+PERMISOS_PROGRAMAR, raise_exception=True)
def crearProgramada(request, idCreacion):

    tipo = obtener(request.session, idCreacion, "tipo")
    InicializacionForm = ProgramadaForm

    if request.method == "POST":

        formInicializacion = InicializacionForm(request.POST)

        if formInicializacion.is_valid():

            guardar(request.session, idCreacion, "estadoInicialData", formInicializacion.data)
            practica = crearPractica(request.session, idCreacion)

            return HttpResponseRedirect(reverse("practicas:"+tipo+":ver", args=(practica.pk,)))
            '''AGREGO EL ELSE PARA MANEJAR EL VALIDATIONERROR (POR FECHA INVÁLIDA) PUESTO EN EL FORM (LINEA 55)'''
        #else:
        #    print("FECHA INVALIDA")
    else:

        formInicializacion = InicializacionForm()

    print("+"*20)
    context = {
        "tipo" : tipo,
        "formEstado" : formInicializacion,
        "formAction" : reverse("practicas:"+tipo+":crear:programada", args=(idCreacion,)),
        "accion" : "Crear",
    }

    #template = loader.get_template(plantilla('inicializar'))
    template = loader.get_template('GestionDePracticas/inicializar.html')
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CREAR+PERMISOS_REALIZAR, raise_exception=True)
def crearRealizada(request, idCreacion):

    tipo = obtener(request.session, idCreacion, "tipo")

    if request.method == "POST":

        formInicializacion = RealizadaForm(request.POST)

        if formInicializacion.is_valid():

            guardar(request.session, idCreacion, "estadoInicialData", formInicializacion.data)
            practica = crearPractica(request.session, idCreacion)

            return HttpResponseRedirect(reverse("practicas:"+tipo+":detalles", args=(practica.pk,)))

    else:

        formInicializacion = RealizadaForm()

    context = {
        "tipo" : tipo,
        "formEstado" : formInicializacion,
        "formAction" : reverse("practicas:"+tipo+":crear:realizada", args=(idCreacion,)),
        "accion" : "Crear",
    }

    #template = loader.get_template(plantilla('inicializar'))
    template = loader.get_template('GestionDePracticas/inicializar.html')
    return HttpResponse(template.render(context, request))



# Views de consultas ##########################################################



@login_required(redirect_field_name='proxima')
def listarConsultas(request):

    TIPO = "consulta"

    formFiltrado = FiltradoForm(request.GET)
    practicas = filtrarPracticas(formFiltrado, Practica.objects.deTipo(TIPO))

    #template = loader.get_template( plantilla("listar") )
    template = loader.get_template('GestionDePracticas/listar.html')
    context = {
        "filtrado" : formFiltrado,
        "tipo" : TIPO,
        'practicas' : practicas
    }

    return HttpResponse(template.render( context, request ))



@login_required(redirect_field_name='proxima')
def verConsulta(request, id):

    TIPO = "consulta"
    practica = Practica.objects.deTipo(TIPO).get(id=id)

    context = {
        "tipo" : TIPO,
        'practica' : practica
    }
    #template = loader.get_template(plantilla('ver'))
    template = loader.get_template('GestionDePracticas/ver.html')

    return HttpResponse(template.render( context, request ))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CREAR, raise_exception=True)
def crearConsulta(request):

    TIPO = "consulta"
    ACCIONES_CONSULTAS = (
        ("presupuestada","Presupuesto"),
        ("realizada","Consulta realizada")
    )

    PracticaForm = practicaFormFactory(TIPO)
    ServiciosFormSet = practicaServicioFormSetFactory(TIPO)
    acciones = request.user.permitidos(ACCIONES_CONSULTAS)
    AccionesForm = accionesFormFactory(acciones)

    if request.method == "POST":

        formAcciones = AccionesForm(request.POST)
        formPractica = PracticaForm(request.POST, submitForm=formAcciones)

        formsetServicios = ServiciosFormSet(request.POST)

        if formPractica.is_valid() and formsetServicios.is_valid():

            idCreacion = idCrearPractica(request.session)
            estadoInicial = formAcciones.estadoInicial()

            guardar(request.session, idCreacion, "tipo", TIPO)
            guardar(request.session, idCreacion, "estadoInicial", estadoInicial)
            guardar(request.session, idCreacion, "practicaData", formPractica.data)
            guardar(request.session, idCreacion, "serviciosData", formsetServicios.data)

            return HttpResponseRedirect(reverse("practicas:consulta:crear:productos", args=(idCreacion,)))

    else:

        formPractica = PracticaForm()
        formsetServicios = ServiciosFormSet()
        formAcciones = AccionesForm()

    context = {
        "tipo" : TIPO,
        "formPractica" : formPractica,
        "formServicios" : formsetServicios,
        "formAcciones" : formAcciones,
        "formAction" : reverse("practicas:consulta:crear:nueva"),
    }

    #template = loader.get_template(plantilla('crear'))
    template = loader.get_template('GestionDePracticas/crear.html')
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_DETALLES, raise_exception=True)
def detallesConsulta(request, id):

    TIPO = "consulta"
    practica = Practica.objects.deTipo(TIPO).get(id=id)
    practica.validarEstado(Realizada)

    ServiciosFormSet = realizadaServicioFormSetFactory(TIPO)
    ProductosFormSet = realizadaProductoFormSetFactory(TIPO)
    realizada = practica.estado()

    if request.method == "POST":

        formsetServicios = ServiciosFormSet(request.POST, instance=realizada, prefix="serviciosformset")
        formsetProductos = ProductosFormSet(request.POST, instance=realizada, prefix="productosformset")

        if formsetServicios.is_valid() and formsetProductos.is_valid():

            servicios = formsetServicios.save()
            productos = formsetProductos.save()

            return HttpResponseRedirect(reverse("practicas:consulta:ver", args=(practica.pk,)))
    else:

        formsetServicios = ServiciosFormSet(instance=realizada, prefix="serviciosformset")
        formsetProductos = ProductosFormSet(instance=realizada, prefix="productosformset")

    context = {
        "tipo" : TIPO,
        "formsetServicios" : formsetServicios,
        "formsetProductos" : formsetProductos,
        "formAction" : reverse("practicas:consulta:detalles", args=(id,)),
        "accion" : "Modificar",
    }

    template = loader.get_template(plantilla('detallar'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_REALIZAR, raise_exception=True)
def realizarConsulta(request):

    TIPO = "consulta"
    formFiltrado = FiltradoForm(request.GET)
    practicas = Practica.objects.deTipo(TIPO).enEstado([Presupuestada])
    practicas = filtrarPracticas(formFiltrado, practicas)

    SeleccionForm = seleccionPracticaFormFactory(TIPO, practicas)

    if request.method == 'POST':

        formEstado = RealizadaForm(request.POST)
        formPractica = SeleccionForm(request.POST)

        if formEstado.is_valid() and formPractica.is_valid():

            #[TODO]: tener en cuenta las excepciones
            practica = formPractica.practica
            accion = formEstado.accion()
            argumentos = formEstado.datos()

            practica.hacer(accion, **argumentos)

            return HttpResponseRedirect(reverse("practicas:consulta:detalles", args=(practica.pk,)))

    else:

        formEstado = RealizadaForm()
        formPractica = SeleccionForm()

    context = {
        "tipo" : TIPO,
        "filtrado" : formFiltrado,
        "estado" : formEstado,
        "practica" : formPractica,
        "formAction" : reverse("practicas:consulta:"+formEstado.accion()),
    }

    template = loader.get_template(plantilla('actualizar'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CANCELAR, raise_exception=True)
def cancelarConsulta(request):

    TIPO = "consulta"
    formFiltrado = FiltradoForm(request.GET)
    practicas = Practica.objects.deTipo("consulta").enEstado([Presupuestada])
    practicas = filtrarPracticas(formFiltrado, practicas)

    SeleccionForm = seleccionPracticaFormFactory(TIPO, practicas)

    if request.method == 'POST':

        formEstado = CanceladaForm(request.POST)
        formPractica = SeleccionForm(request.POST)

        if formEstado.is_valid() and formPractica.is_valid():

            #[TODO]: tener en cuenta las excepciones
            practica = formPractica.practica
            accion = formEstado.accion()
            argumentos = formEstado.datos()

            practica.hacer(accion, **argumentos)

            return HttpResponseRedirect(reverse("practicas:consulta:ver", args=(practica.pk,)))

    else:

        formEstado = CanceladaForm()
        formPractica = SeleccionForm()

    context = {
        "tipo" : TIPO,
        "filtrado" : formFiltrado,
        "estado" : formEstado,
        "practica" : formPractica,
        "formAction" : reverse("practicas:consulta:"+formEstado.accion()),
    }

    template = loader.get_template(plantilla('actualizar'))
    return HttpResponse(template.render(context, request))



# Views de cirugias ###########################################################



@login_required(redirect_field_name='proxima')
def listarCirugias(request):

    TIPO = "cirugia"
    formFiltrado = FiltradoForm(request.GET)
    practicas = filtrarPracticas(formFiltrado, Practica.objects.deTipo(TIPO))


    #template = loader.get_template( plantilla("listar") )
    template = loader.get_template('GestionDePracticas/listar.html')

    context = {
        "tipo" : TIPO,
        "filtrado" : formFiltrado,
        'practicas' : practicas
    }

    return HttpResponse(template.render( context, request ))



@login_required(redirect_field_name='proxima')
def verCirugia(request, id):

    TIPO = "cirugia"
    practica = Practica.objects.deTipo(TIPO).get(id=id)

    context = {
        "tipo" : TIPO,
        'practica' : practica
    }
    #template = loader.get_template(plantilla('ver'))
    template = loader.get_template('GestionDePracticas/ver.html')

    return HttpResponse(template.render( context, request ))


@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CREAR, raise_exception=True)
def crearCirugia(request):

    TIPO = "cirugia"
    ACCIONES_CIRUGIAS = (
        ("presupuestada","Presupuesto"),
        ("programada","Turno"),
        ("realizada","Cirugia realizada")
    )

    PracticaForm = practicaFormFactory(TIPO)
    ServiciosFormSet = practicaServicioFormSetFactory(TIPO)
    acciones = request.user.permitidos(ACCIONES_CIRUGIAS)
    AccionesForm = accionesFormFactory(acciones)

    if request.method == "POST":

        formAcciones = AccionesForm(request.POST)
        formPractica = PracticaForm(request.POST, submitForm=formAcciones)

        formsetServicios = ServiciosFormSet(request.POST)

        if formPractica.is_valid() and formsetServicios.is_valid():
            idCreacion = idCrearPractica(request.session)
            estadoInicial = formAcciones.estadoInicial()

            guardar(request.session, idCreacion, "tipo", TIPO)
            guardar(request.session, idCreacion, "estadoInicial", estadoInicial)
            guardar(request.session, idCreacion, "practicaData", formPractica.data)
            guardar(request.session, idCreacion, "serviciosData", formsetServicios.data)

            return HttpResponseRedirect(reverse("practicas:cirugia:crear:productos", args=(idCreacion,)))

    else:

        formPractica = PracticaForm()
        formsetServicios = ServiciosFormSet()
        formAcciones = AccionesForm()

    context = {
        "tipo" : TIPO,
        "formPractica" : formPractica,
        "formServicios" : formsetServicios,
        "formAcciones" : formAcciones,
        "formAction" : reverse("practicas:cirugia:crear:nueva"),
    }

    #template = loader.get_template(plantilla('crear'))
    template = loader.get_template('GestionDePracticas/crear.html')
    return HttpResponse(template.render(context, request))




@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_PROGRAMAR, raise_exception=True)
def programarCirugia(request):

    TIPO = "cirugia"
    formFiltrado = FiltradoForm(request.GET)
    practicas = Practica.objects.deTipo(TIPO).enEstado([Presupuestada])
    practicas = filtrarPracticas(formFiltrado, practicas)

    SeleccionForm = seleccionPracticaFormFactory(TIPO, practicas)

    if request.method == 'POST':

        formEstado = ProgramadaForm(request.POST)
        formPractica = SeleccionForm(request.POST)

        if formEstado.is_valid() and formPractica.is_valid():

            #[TODO]: tener en cuenta las excepciones
            practica = formPractica.practica
            accion = formEstado.accion()
            argumentos = formEstado.datos()

            practica.hacer(accion, **argumentos)

            return HttpResponseRedirect(reverse("practicas:cirugia:ver", args=(practica.pk,)))

    else:

        formEstado = ProgramadaForm()
        formPractica = SeleccionForm()

    context = {
        "tipo" : TIPO,
        "filtrado" : formFiltrado,
        "estado" : formEstado,
        "practica" : formPractica,
        "formAction" : reverse("practicas:cirugia:"+formEstado.accion()),
    }

    template = loader.get_template(plantilla('actualizar'))
    return HttpResponse(template.render(context, request))




@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_REALIZAR, raise_exception=True)
def realizarCirugia(request):

    TIPO = "cirugia"
    formFiltrado = FiltradoForm(request.GET)
    practicas = Practica.objects.deTipo(TIPO).enEstado([Presupuestada, Programada])
    practicas = filtrarPracticas(formFiltrado, practicas)

    SeleccionForm = seleccionPracticaFormFactory(TIPO, practicas)

    if request.method == 'POST':

        formEstado = RealizadaForm(request.POST)
        formPractica = SeleccionForm(request.POST)

        if formEstado.is_valid() and formPractica.is_valid():

            #[TODO]: tener en cuenta las excepciones
            practica = formPractica.practica
            accion = formEstado.accion()
            argumentos = formEstado.datos()

            practica.hacer(accion, **argumentos)

            return HttpResponseRedirect(reverse("practicas:cirugia:detalles", args=(practica.pk,)))

    else:

        formEstado = RealizadaForm()
        formPractica = SeleccionForm()

    context = {
        "tipo" : TIPO,
        "filtrado" : formFiltrado,
        "estado" : formEstado,
        "practica" : formPractica,
        "formAction" : reverse("practicas:cirugia:"+formEstado.accion()),
    }

    template = loader.get_template(plantilla('actualizar'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_CANCELAR, raise_exception=True)
def cancelarCirugia(request):

    TIPO = "cirugia"
    formFiltrado = FiltradoForm(request.GET)
    practicas = Practica.objects.deTipo(TIPO).enEstado([Presupuestada, Programada])
    practicas = filtrarPracticas(formFiltrado, practicas)

    SeleccionForm = seleccionPracticaFormFactory(TIPO, practicas)

    if request.method == 'POST':

        formEstado = CanceladaForm(request.POST)
        formPractica = SeleccionForm(request.POST)

        if formEstado.is_valid() and formPractica.is_valid():

            #[TODO]: tener en cuenta las excepciones
            practica = formPractica.practica
            accion = formEstado.accion()
            argumentos = formEstado.datos()

            practica.hacer(accion, **argumentos)

            return HttpResponseRedirect(reverse("practicas:cirugia:ver", args=(practica.pk,)))

    else:

        formEstado = CanceladaForm()
        formPractica = SeleccionForm()

    context = {
        "tipo" : TIPO,
        "filtrado" : formFiltrado,
        "estado" : formEstado,
        "practica" : formPractica,
        "formAction" : reverse("practicas:cirugia:"+formEstado.accion()),
    }

    template = loader.get_template(plantilla('actualizar'))
    return HttpResponse(template.render(context, request))



@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_DETALLES, raise_exception=True)
def detallesCirugia(request, id):

    TIPO = "cirugia"
    practica = Practica.objects.deTipo(TIPO).get(id=id)
    practica.validarEstado(Realizada)

    ServiciosFormSet = realizadaServicioFormSetFactory(TIPO)
    ProductosFormSet = realizadaProductoFormSetFactory(TIPO)
    realizada = practica.estado()

    if request.method == "POST":

        formsetServicios = ServiciosFormSet(request.POST, instance=realizada, prefix="serviciosformset")
        formsetProductos = ProductosFormSet(request.POST, instance=realizada, prefix="productosformset")

        if formsetServicios.is_valid() and formsetProductos.is_valid():

            servicios = formsetServicios.save()
            productos = formsetProductos.save()

            return HttpResponseRedirect(reverse("practicas:cirugia:ver", args=(practica.pk,)))

    else:

        formsetServicios = ServiciosFormSet(instance=realizada, prefix="serviciosformset")
        formsetProductos = ProductosFormSet(instance=realizada, prefix="productosformset")

    context = {
        "tipo" : TIPO,
        "formsetServicios" : formsetServicios,
        "formsetProductos" : formsetProductos,
        "formAction" : reverse("practicas:cirugia:detalles", args=(id,)),
        "accion" : "Modificar",
    }

    template = loader.get_template(plantilla('detallar'))
    return HttpResponse(template.render(context, request))

def verAgendaCirugia(request):
    if "fecha" in request.GET:
        fecha = request.GET["fecha"]
    else:
        fecha = djangotimezone.now()
    practicas = Practica.quirurgicas.filter(turno__date=fecha)
    turnos = [
        {"turno": practica.turno,
         "duracion": practica.duracion(),
         "servicios": [servicio.nombre for servicio in practica.servicios.all()]
         }
              for practica in practicas]
    return JsonResponse({ 'turnos':  turnos})
