from os.path import join
from datetime import datetime, timedelta

from django.urls import reverse
from django.db import transaction
from django.db.models import Max as dbMax
from django.db.models import F as dbF
from django.utils import timezone

from VeterinariaPatagonica.tools import GestorListadoQueryset
from VeterinariaPatagonica.areas import Areas
from VeterinariaPatagonica.errores import VeterinariaPatagonicaError
from Apps.GestionDeProductos.models import Producto
from Apps.GestionDeServicios.models import Servicio, ServicioProducto
from Apps.GestionDeClientes.models import Cliente
from Apps.GestionDeTiposDeAtencion.models import TipoDeAtencion
from .forms import *
from .models import *
from .config import config

PLANTILLAS = {
    "error" : "error",

    "buscar" : "buscar",
    "listar" : "listar",

    "crear" : "crear",
    "modificar" : "modificar",
    "crearPresupuestada" : "crearPresupuestada",
    "crearProgramada" : "crearProgramada",
    "crearRealizada" : "crearRealizada",
    "productos" : "productos",

    "ver" : "ver",
    "creada" : "ver",
    "presupuestada" : "presupuestada",
    "programada" : "programada",
    "realizada" : "realizada",
    "cancelada" : "cancelada",
    "facturada" : "facturada",

    "programar" : "programar",
    "reprogramar" : "reprogramar",
    "realizar" : "realizar",
    "cancelar" : "cancelar",

    "modificarDetalles" : "modificarDetalles",
    "modificarObservaciones" : "modificarObservaciones",
    "verObservaciones" : "verObservaciones",
}
def plantilla(nombre, subdirectorio=""):
    return join( "GestionDePracticas", subdirectorio, PLANTILLAS[nombre]+".html")



def pathModificar(tipo, id):
    return reverse(
        "%s:%s:crear:modificarPractica" % (config("app_name"), tipo), args=(id,)
    )



def pathTerminar(tipo, id):
    return reverse(
        "%s:%s:crear:terminar" % (config("app_name"), tipo), args=(id,)
    )



def pathModificarProductos(tipo, id):
    return reverse(
        "%s:%s:crear:modificarProductos" % (config("app_name"), tipo), args=(id,)
    )



def pathInicializar(tipo, accion, id):
    return reverse(
        "%s:%s:crear:%s" %(config("app_name"), tipo, accion), args=(id,)
    )



def pathVer(tipo, id):
    return reverse(
        "%s:%s:ver:practica" % (config("app_name"), tipo), args=(id,)
    )



def pathListar(tipo):
    return reverse(
        "%s:%s:listar" % (config("app_name"), tipo)
    )



def pathCrear(tipo):
    return reverse(
        "%s:%s:crear:practica" % (config("app_name"), tipo)
    )



def pathDetallarRealizacion(tipo, id):
    return reverse(
        "%s:%s:modificar:detalles" % (config("app_name"), tipo), args=(id,)
    )



def pathActualizar(tipo, accion, id):
    return reverse(
        "%s:%s:actualizaciones:%s" % (config("app_name"), tipo, accion), args=(id,)
    )



def pathFacturar(id):
    return reverse(
        "facturas:facturarPractica", args=(id,)
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

    if (tipoPractica is not None) and (tipo != tipoPractica):
        raise VeterinariaPatagonicaError(
            "Solicitud erronea",
            "El pedido de creacion no es valido, no existe ninguna %s con esas caracteristicas siendo creada en esta sesion" % tipoPractica,
        )

    return {
        "id" : idCreacion,
        "tipo" : tipo,
        "errores" : [],
    }



def calcularPrecio(detalles, tipoDeAtencion=None):

    ajuste = 0
    precioServicios = sum([ detalle.precioTotal() for detalle in detalles["servicios"] ])
    precioProductos = sum([ detalle.precioTotal() for detalle in detalles["productos"] ])
    if tipoDeAtencion is not None:
        ajuste = (precioProductos + precioServicios) * tipoDeAtencion / Decimal(100)
    return precioProductos + precioServicios + ajuste



def calcularDuracion(servicios):

    return sum([
        (detalle.servicio.tiempoEstimado * detalle.cantidad) for detalle in servicios
    ])



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



def verificarCreacion(practica, accion):

    cliente = practica.cliente
    mascotas = cliente.mascota_set.habilitados()
    mascotaObligatoria = accion in (
        Practica.Acciones.programar.name,
        Practica.Acciones.realizar.name,
    )

    if mascotaObligatoria and (mascotas.count() == 0):
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



def verificarAccion(practica, accion):

    if not practica.esPosible(accion):
        raise VeterinariaPatagonicaError(
            "Solicitud erronea",
            "No se puede %s una practica que se encuentre %s" % (accion.name, practica.nombreEstado()),
        )



def formPresupuestar(*args, vigencia=config("vigencia"), **kwargs):

    hoy = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    initial = {
        "duracion" : vigencia,
        "desde" : hoy,
        "hasta" : hoy + timedelta(days=vigencia),
    }

    if ("initial" in kwargs) and (kwargs["initial"] is not None):
        initial.update(kwargs["initial"])
    kwargs["initial"] = initial

    return PresupuestadaForm(*args, mascota_required=False, **kwargs)



def formProgramar(*args, precio=0.0, duracion=config("duracion"), practica=None, **kwargs):

    adelanto = int(float(precio) * config("adelanto"))

    rango = timedelta(minutes=duracion*20)
    busquedas = 100
    inicio = timezone.now().replace(second=0, microsecond=0)
    finalizacion = inicio + rango

    cuando = None
    while (cuando is None) and busquedas:
        horarios = Programada.horariosDisponibles(inicio, finalizacion, minimo=timedelta(minutes=duracion))
        if len(horarios):
            cuando = horarios[0][0]
        else:
            finalizacion = finalizacion + rango
            inicio = inicio + rango
            busquedas -= 1

    if cuando is None:
        cuando = timezone.now().replace(second=0, microsecond=0)

    initial = {
        "desde" : cuando,
        "hasta" : cuando + timedelta(minutes=duracion),
        "duracion" : duracion,
        "adelanto" : adelanto,
    }

    if ("initial" in kwargs) and (kwargs["initial"] is not None):
        initial.update(kwargs["initial"])
    kwargs["initial"] = initial

    return ProgramadaForm(*args, precio=precio, practica=practica, **kwargs)


def formReprogramar(*args, practica=None, **kwargs):

    if practica is not None:
        estado = practica.estado()
        cuando = timezone.localtime(estado.inicio)
        duracion = estado.duracion
    else:
        cuando = timezone.now().replace(minute=0,second=0,microsecond=0) + timedelta(hours=1)
        duracion = config("duracion")

    initial = {
        "desde" : cuando,
        "hasta" : cuando + timedelta(minutes=duracion),
        "duracion" : duracion,
    }

    if not "initial" in kwargs:
        kwargs["initial"] = {}
    kwargs["initial"].update(initial)

    return ReprogramadaForm(*args, practica=practica, **kwargs)



def formRealizar(*args, practica=None, duracion=config("duracion"), **kwargs):

    finalizacion = None
    inicio = None

    if practica is not None:
        estado = practica.estado()
        if isinstance(estado, Programada):
            finalizacion = timezone.localtime(estado.finalizacion)
            inicio = timezone.localtime(estado.inicio)
            duracion = estado.duracion

    if finalizacion is None:
        finalizacion = timezone.now()
    if inicio is None:
        inicio = finalizacion - timedelta(minutes=duracion)

    initial = {
        "desde" : inicio,
        "hasta" : finalizacion,
        "duracion" : duracion,
    }

    if not "initial" in kwargs:
        kwargs["initial"] = {}
    kwargs["initial"].update(initial)

    return RealizadaForm(*args, practica=practica, **kwargs)



def crearUrls(acciones, practica, usuario):

    generadoresUrls = {
        Practica.Acciones.programar : lambda practica: pathActualizar(practica.nombreTipo(), "programar", practica.id),
        Practica.Acciones.reprogramar : lambda practica: pathActualizar(practica.nombreTipo(), "reprogramar", practica.id),
        Practica.Acciones.realizar : lambda practica: pathActualizar(practica.nombreTipo(), "realizar", practica.id),
        Practica.Acciones.cancelar : lambda practica: pathActualizar(practica.nombreTipo(), "cancelar", practica.id),
        Practica.Acciones.facturar : lambda practica: pathFacturar(practica.id),
    }

    permitidas = practica.estado().accionesPosibles().intersection( usuario.acciones() )
    retorno = []

    for accion in acciones:
        if accion in permitidas:
            generador = generadoresUrls[accion]
            retorno.append([accion, generador(practica)])

    return retorno



class GestorListadoPractica(GestorListadoQueryset):

    def ordenar(self):
        self.queryset = self.queryset.annotate(
            ultima_mod=dbMax('estado__marca')
        ).filter(
            estado__marca=dbF('ultima_mod')
        )
        super().ordenar()
