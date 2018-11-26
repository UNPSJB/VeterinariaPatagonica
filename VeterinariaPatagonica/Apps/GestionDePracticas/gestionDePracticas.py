from math import ceil
from os.path import join
from datetime import datetime, timedelta, time

from django.urls import reverse
from django.db import transaction
from django.utils import timezone

from VeterinariaPatagonica.areas import Areas
from VeterinariaPatagonica.errores import VeterinariaPatagonicaError
from Apps.GestionDeProductos.models import Producto
from Apps.GestionDeServicios.models import Servicio, ServicioProducto
from Apps.GestionDeClientes.models import Cliente
from Apps.GestionDeTiposDeAtencion.models import TipoDeAtencion
from .forms import *
from .models import *
from .settings import *



PLANTILLAS = {
    "listar" : "listar",
    "ver" : "ver",
    "creada" : "ver",
    "presupuestada" : "presupuestada",
    "programada" : "programada",
    "realizada" : "realizada",
    "cancelada" : "cancelada",
    "facturada" : "facturada",
    "actualizar" : "actualizar",
    "crear" : "crear",
    "inicializar" : "inicializar",
    "realizacion" : "realizacion",
    "productos" : "productos",
    "completarPresupuesto" : "completarPresupuesto",
    "detalles" : "detalles",
}
def plantilla(nombre, subdirectorio=""):
    return join( "GestionDePracticas", subdirectorio, PLANTILLAS[nombre]+".html")



def pathModificar(tipo, id):
    return reverse(
        "%s:%s:crear:modificar" % (APP_NAME, tipo), args=(id,)
    )



def pathTerminar(tipo, id):
    return reverse(
        "%s:%s:crear:terminar" % (APP_NAME, tipo), args=(id,)
    )



def pathModificarProductos(tipo, id):
    return reverse(
        "%s:%s:crear:modificarProductos" % (APP_NAME, tipo), args=(id,)
    )



def pathInicializar(tipo, accion, id):
    return reverse(
        "%s:%s:crear:%s" %(APP_NAME, tipo, accion), args=(id,)
    )



def pathVer(tipo, id):
    return reverse(
        "%s:%s:ver" % (APP_NAME, tipo), args=(id,)
    )



def pathListar(tipo):
    return reverse(
        "%s:%s:listar" % (APP_NAME, tipo)
    )



def pathCrear(tipo):
    return reverse(
        "%s:%s:crear:nueva" % (APP_NAME, tipo)
    )



def pathDetallarRealizacion(tipo, id):
    return reverse(
        "%s:%s:realizacion" % (APP_NAME, tipo), args=(id,)
    )



def pathCompletarPresupuesto(tipo, id, accion):
    return reverse(
        "%s:%s:completarPresupuesto" % (APP_NAME, tipo), args=(id, accion)
    )



def pathActualizar(tipo, accion, id):
    return reverse(
        "%s:%s:%s" % (APP_NAME, tipo, accion), args=(id,)
    )



def errorDatos(excepcion, tipo=None, id=None, **kwargs):

    error= {
        "clase" : "error",
        "titulo" : excepcion.titulo,
        "descripcion" : excepcion.descripcion,
        "sugerencias" : []
    }

    if (tipo is not None) and (id is not None):
        error["sugerencias"].append(
            {
                "href" : pathModificar(tipo, id),
                "contenido" : "Volver a completar datos erroneos"
            }
        )
        error["sugerencias"].append(
            {
                "href" : pathTerminar(tipo, id),
                "contenido" : "Cancelar la creacion"
            }
        )

    return error



def errorSolicitud(excepcion, tipo=None, **kwargs):

    error = {
        "clase" : "error",
        "titulo" : excepcion.titulo,
        "descripcion" : excepcion.descripcion,
        "sugerencias" : []
    }

    if tipo is not None:
        error["sugerencias"].append(
            {
                "href" : pathCrear(tipo),
                "contenido" : "Crear nueva %s" % tipo
            }
        )

    return error



def errorBD(tipo=None, id=None, **kwargs):

    error = {
        "clase" : "error",
        "titulo" : "Error al guardar datos enviados",
        "descripcion" : "Ocurrio un error al intentar guardar los datos recibidos: ",
        "sugerencias" : []
    }

    if (tipo is not None) and (id is not None):
        error["sugerencias"].append(
            {
                "href" : pathTerminar(tipo, id),
                "contenido" : "Cancelar la creacion"
            }
        )

    return error



def errorAccion(practica=None, accion=None, **kwargs):

    if accion is None:
        accion = "modificar"

    if practica is None:
        tipo = "practica"
    else:
        tipo = practica.nombreTipo()

    detalles = kwargs["detalles"] if "detalles" in kwargs else ""

    error= {
        "clase" : "error",
        "titulo" : "Error durante modificacion de %s" % tipo,
        "descripcion" : "Ocurrio un error al intentar %s, la modificacion no pudo completarse. %s." % (accion, detalles),
        "sugerencias" : []
    }

    if (practica is not None):
        error["sugerencias"].append(
            {
                "href" : pathVer(tipo, practica.id),
                "contenido" : "Ver el estado actual de la practica"
            }
        )

    return error



def idCrearPractica(session):

    if not "practicas_crear_id_anterior" in session:
        session["practicas_crear_id_anterior"] = 0

    id = session["practicas_crear_id_anterior"] + 1
    session["practicas_crear_id_anterior"] = id

    return id



def guardar(session, id, etiqueta, datos):

    clave = "practicas_crear_%d_%s" % (id, etiqueta)
    session[clave] = datos



def obtener(session, id, etiqueta):

    clave = "practicas_crear_%d_%s" % (id, etiqueta)

    if not clave in session:
        raise VeterinariaPatagonicaError(
            "Error al recuperar datos",
            "Hubo un error al intentar recuperar datos de la sesion"
        )

    return session[clave]



def eliminar(session, id):

    claves = []
    etiquetas = (
        "tipo",
        "accion",
        "practicaData",
        "serviciosData",
        "productosData"
    )

    for etiqueta in etiquetas:
        clave = "practicas_crear_%d_%s" % (id, etiqueta)
        if clave in session:
            del session[clave]



def crearContexto(request, idCreacion, tipoPractica=None, accion=None):

    tipo = obtener(request.session, idCreacion, "tipo")
    accion = obtener(request.session, idCreacion, "accion")

    if (tipoPractica is not None) and (tipo != tipoPractica):
        raise VeterinariaPatagonicaError(
            "Solicitud erronea",
            "El pedido de creacion no es valido, no existe ninguna %s con esas caracteristicas siendo creada en esta sesion" % tipoPractica,
        )

    if (accion is not None) and (accion != accion):
        raise VeterinariaPatagonicaError(
            "Solicitud erronea",
            "El pedido de creacion no es valido, no existe ninguna %s con esas caracteristicas siendo creada en esta sesion" % tipoPractica,
        )

    return {
        "id" : idCreacion,
        "tipo" : tipo,
        "accion" : accion,
        "errores" : [],
    }



def calcularPrecio(practica, detalles):

    precioServicios = sum([ detalle.precioTotal() for detalle in detalles["servicios"] ])
    precioProductos = sum([ detalle.precioTotal() for detalle in detalles["productos"] ])
    return precioProductos + precioServicios



def buscarProductos(servicios):

    listado = []
    datos = {}

    for detalleServicio in servicios:

        servicio = Servicio.objects.get(id=detalleServicio['servicio'])
        cantidadServicio = detalleServicio['cantidad']

        for detalleProducto in servicio.servicio_productos.all():

            producto = detalleProducto.producto
            if producto.baja:
                raise VeterinariaPatagonicaError(
                    "Error",
                    "El producto '%s' (%d) del servicio '%s' (%d)  no esta habilitado" % (
                        producto.nombre,
                        producto.id,
                        servicio.nombre,
                        servicio.id,
                    )
                )

            cantidadProducto = detalleProducto.cantidad
            producto = detalleProducto.producto.id

            if producto not in datos:
                datos[producto] = 0

            datos[producto] += cantidadServicio * cantidadProducto

    for producto, cantidad in datos.items():
        listado.append({
                'producto' : producto,
                'cantidad' : cantidad
        })

    return listado



def crearDetallesServicios(datos):

    cantidades = { detalle["servicio"] : detalle["cantidad"] for detalle in datos }
    servicios  = Servicio.objects.filter( id__in=cantidades.keys() )

    if len(servicios) < len(cantidades):
        raise VeterinariaPatagonicaError(
            "Error al recuperar datos",
            "Hubo un error al intentar recuperar elementos de la base de datos"
        )

    detalles = []
    for servicio in servicios:
        detalles.append(PracticaServicio(
            servicio = servicio,
            cantidad = cantidades[servicio.pk],
            precio = servicio.precioManoDeObra
        ))

    return detalles



def crearDetallesProductos(datos):

    cantidades = { detalle["producto"] : detalle["cantidad"] for detalle in datos }
    productos  = Producto.objects.filter( id__in=cantidades.keys() )

    if len(productos) < len(cantidades):
        raise VeterinariaPatagonicaError(
            "Error al recuperar datos",
            "Hubo un error al intentar recuperar elementos de la base de datos"
        )

    detalles = []
    for producto in productos:
        detalles.append(PracticaProducto(
            producto = producto,
            cantidad = cantidades[producto.pk],
            precio = producto.precioDeCompra
        ))

    return detalles



def obtenerDetalles(request, idCreacion):

    productosData = obtener(request.session, idCreacion, "productosData")
    productos = crearDetallesProductos(productosData)

    serviciosData = obtener(request.session, idCreacion, "serviciosData")
    servicios = crearDetallesServicios(serviciosData)

    return {
        "productos" : productos,
        "servicios" : servicios,
    }



def obtenerPractica(request, idCreacion):

    tipo = obtener(request.session, idCreacion, "tipo")
    practica = Practica(tipo=Areas.codificar(tipo))
    practicaData = obtener(request.session, idCreacion, "practicaData")
    formPractica = PracticaForm(practicaData, instance=practica)
    if not formPractica.is_valid():
        raise VeterinariaPatagonicaError(
            "Error al recuperar datos",
            "Error al recrear el formulario, los datos no son validos."
        )

    practica = formPractica.save(commit=False)
    return practica



def persistir(practica, detalles, accion, argumentos):

    with transaction.atomic():

        practica.save(force_insert=True)
        practica.practica_servicios.set(detalles["servicios"], bulk=False)
        practica.practica_productos.set(detalles["productos"], bulk=False)
        practica.hacer(accion, **argumentos)

    return practica



def calcularPaginas(queryset):
    cantidad = ceil(queryset.count() / PRACTICAS_POR_PAGINA)
    return max(cantidad, 1)



def practicasParaPagina(queryset, pagina, paginas):

    if not (1 <= pagina <= paginas):
        raise VeterinariaPatagonicaError("Pagina no existe", "Numero de pagina %s no valido" % str(pagina))

    n = (pagina-1) * PRACTICAS_POR_PAGINA
    m = pagina * PRACTICAS_POR_PAGINA

    return queryset[n:m]



def proximaHora():
    ahora = datetime.now()
    ahora = ahora.replace(minute=0, second=0, microsecond=0)
    return ahora + timedelta(hours=1)



def accionesIniciales(user, area):

    usuario = user.acciones()
    practica = Practica.Acciones.iniciales(area.codigo)

    acciones = practica & usuario

    if not len(acciones):
        raise VeterinariaPatagonicaError(
            "Permiso denegado",
            "No tiene permisos para crear practicas de este tipo"
        )

    return acciones



def verificarCreacion(formPractica, formsetServicios, formCreacion):

    cliente = formPractica.cleaned_data["cliente"]
    mascotas = cliente.mascota_set.habilitados()
    noPresupuesto = (formCreacion.accion != Practica.Acciones.presupuestar.name)

    if noPresupuesto and (mascotas.count() == 0):
        descripcion = "El cliente %s %s (%s) no tiene mascotas habilitadas en este momento"
        descripcion = descripcion % (cliente.nombres, cliente.apellidos, cliente.dniCuit)
        raise VeterinariaPatagonicaError(
            titulo="Solicitud erronea",
            descripcion=descripcion
        )



def verificarPractica(practica):

    if practica.cliente is None:
        descripcion = "Los datos de la practica no son validos, no tiene asociado ningun cliente"
        raise VeterinariaPatagonicaError(
            titulo="Error",
            descripcion=descripcion
        )

    cliente = practica.cliente
    deshabilitado = (Cliente.objects.habilitados().filter(id=cliente.id).count() != 1)
    if deshabilitado:
        descripcion = "El cliente %s %s (%s) no esta habilitado en el sistema"
        descripcion = descripcion % (cliente.nombres, cliente.apellidos, cliente.dniCuit)
        raise VeterinariaPatagonicaError(
            titulo="Solicitud erronea",
            descripcion=descripcion
        )

    mascotas = cliente.mascota_set.habilitados()

    if mascotas.count() == 0:
        descripcion = "El cliente %s %s (%s) no tiene mascotas habilitadas en este momento"
        descripcion = descripcion % (cliente.nombres, cliente.apellidos, cliente.dniCuit)
        raise VeterinariaPatagonicaError(
            titulo="Solicitud erronea",
            descripcion=descripcion
        )



def verificarEstado(practica, estados):

    actual = practica.estado()

    if not isinstance(actual, tuple(estados)):
        descripcion = "La practica no se encuentra en un estado permitido para realizar la accion solicitada, actualmente se encuentra en estado %s" % actual
        raise VeterinariaPatagonicaError(
            titulo="Solicitud erronea",
            descripcion=descripcion,
        )



def verificarPresupuesto(practica, accion):

    try:
        accion = Practica.Acciones(accion)
    except ValueError:
        raise VeterinariaPatagonicaError(titulo="Solicitud erronea", descripcion="La accion solicitada no es valida")

    verificarEstado(practica, [Presupuestada])
    verificarAccion(practica, accion)

    presupuesto = practica.estado()
    if presupuesto.haExpirado():
        raise VeterinariaPatagonicaError(
            titulo="Solicitud erronea",
            descripcion="El presupuesto ha expirado el dia %s" % presupuesto.vencimiento().strftime("%d/%m/%Y"),
        )

    cliente = practica.cliente
    if Cliente.objects.habilitados().filter(id=cliente.id).count() == 0:
        descripcion = "El cliente %s %s (%s) no esta habilitado"
        descripcion = descripcion % (cliente.nombres, cliente.apellidos, cliente.dniCuit)
        raise VeterinariaPatagonicaError(
            titulo="Solicitud erronea",
            descripcion=descripcion,
        )

    mascotas = cliente.mascota_set.habilitados()
    if mascotas.count() == 0:
        descripcion = "El cliente %s %s (%s) no tiene mascotas habilitadas a quienes asociar el presupuesto"
        descripcion = descripcion % (cliente.nombres, cliente.apellidos, cliente.dniCuit)
        raise VeterinariaPatagonicaError(
            titulo="Solicitud erronea",
            descripcion=descripcion,
        )



def verificarAccion(practica, accion):

    if not practica.esPosible(accion):
        raise VeterinariaPatagonicaError(
            "Solicitud erronea",
            "No se puede %s una practica que se encuentre %s" % (accion.name, practica.nombreEstado()),
        )



def turnoInitial(precio=None, duracion=None, cuando=None):

    if precio is None:
        precio = 0
    if duracion is None:
        duracion = DURACION
    if cuando is None:
        cuando = proximaHora()

    adelanto = int(float(precio) * FACTOR_ADELANTO)

    return {
        "fecha" : cuando.date(),
        "hora" : cuando.time(),
        "duracion" : duracion,
        "adelanto" : adelanto,
    }



def formNuevoPresupuesto(practica, *args, **kwargs):

    initial = {
        "diasMantenimiento" : MANTENIMIENTO,
    }

    if ("initial" in kwargs) and (kwargs["initial"] is not None):
        initial.update(kwargs["initial"])
    kwargs["initial"] = initial

    return NuevaPresupuestadaForm(practica, *args, **kwargs)



def formProgramacion(precio, *args, **kwargs):

    initial = turnoInitial(precio)

    if ("initial" in kwargs) and (kwargs["initial"] is not None):
        initial.update(kwargs["initial"])

    kwargs["initial"] = initial

    return ProgramadaForm(*args, precio=precio, **kwargs)



def formNuevaProgramacion(practica, precio, *args, **kwargs):

    initial = turnoInitial(precio)

    if ("initial" in kwargs) and (kwargs["initial"] is not None):
        initial.update(kwargs["initial"])
    kwargs["initial"] = initial

    return NuevaProgramadaForm(practica, *args, precio=precio, **kwargs)



def formReprogramacion(practica, *args, **kwargs):

    if practica is not None:
        estado = practica.estado()
        inicio = timezone.localtime(estado.inicio)

        initial = {
            "fecha" : inicio.date(),
            "hora" : inicio.time(),
            "duracion" : estado.duracion,
        }
        if not "initial" in kwargs:
            kwargs["initial"] = {}
        kwargs["initial"].update(initial)

    return ReprogramadaForm(*args, **kwargs)



def formRealizacion(practica, *args, **kwargs):

    finalizacion = timezone.now()
    inicio = finalizacion - timedelta(minutes=DURACION)

    if practica is not None:
        estado = practica.estado()
        if isinstance(estado, Programada):
            inicio = timezone.localtime(estado.inicio)
            finalizacion = timezone.localtime(estado.finalizacion)

    initial = {
        "fechaInicio" : inicio.date(),
        "horaInicio" : inicio.time(),
        "fechaFinalizacion" : finalizacion.date(),
        "horaFinalizacion" : finalizacion.time(),
    }
    if not "initial" in kwargs:
        kwargs["initial"] = {}
    kwargs["initial"].update(initial)

    return RealizadaForm(*args, **kwargs)



def formNuevaRealizacion(practica, *args, **kwargs):

    finalizacion = timezone.now()
    inicio = finalizacion - timedelta(minutes=DURACION)

    initial = {
        "fechaInicio" : inicio.date(),
        "horaInicio" : inicio.time(),
        "fechaFinalizacion" : finalizacion.date(),
        "horaFinalizacion" : finalizacion.time(),
    }

    if ("initial" in kwargs) and (kwargs["initial"] is not None):
        initial.update(kwargs["initial"])
    kwargs["initial"] = initial

    return NuevaRealizadaForm(practica, *args, **kwargs)
