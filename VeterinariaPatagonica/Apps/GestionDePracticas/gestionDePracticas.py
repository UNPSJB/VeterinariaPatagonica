from os.path import join as pathjoin
from datetime import timedelta, datetime
from decimal import Decimal
from math import ceil

from django.urls import reverse
from django.db import transaction
from django.db.models import Q
from django.db.utils import Error as dbError

from VeterinariaPatagonica.tools import GestorListadoQuerySet, R
from VeterinariaPatagonica.areas import Areas
from VeterinariaPatagonica.errores import VeterinariaPatagonicaError
from Apps.GestionDeProductos.models import Producto
from Apps.GestionDeServicios.models import Servicio
from Apps.GestionDeClientes.models import Cliente
from Apps.GestionDeMascotas.models import Mascota
from .forms import *
from .models import *
from .config import config
from . import permisos


def plantilla(*ruta):
    return pathjoin("GestionDePracticas", *ruta) + ".html"


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


def pathVer(tipo, id, estado=None):
    return reverse(
        "%s:%s:ver:practica" % (config("app_name"), tipo), args=(id,)
    ) + ("" if estado is None else "?estado=%d" % estado)


def pathListar(tipo):
    return reverse(
        "%s:%s:listar" % (config("app_name"), tipo)
    )


def pathListarRealizaciones():
    return reverse(
        "%s:realizaciones" % config("app_name")
    )


def pathListarTurnosPendientes(tipo):
    return reverse(
        "%s:%s:turnos" % (config("app_name"), tipo)
    )


def pathExportar(tipo, formato):
    return reverse(
        "%s:%s:exportar:%s" % (config("app_name"), tipo, formato)
    )


def pathCrear(tipo):
    return reverse(
        "%s:%s:crear:practica" % (config("app_name"), tipo)
    )


def pathModificarRealizacion(tipo, id):
    return reverse(
        "%s:%s:modificar:realizacion" % (config("app_name"), tipo), args=(id,)
    )


def pathModificarInformacionClinica(tipo, id):
    return reverse(
        "%s:%s:modificar:informacionClinica" % (config("app_name"), tipo), args=(id,)
    )


def pathVerInformacionClinica(tipo, id):
    return reverse(
        "%s:%s:ver:informacionClinica" % (config("app_name"), tipo), args=(id,)
    )


def pathActualizar(tipo, accion, id):
    return reverse(
        "%s:%s:actualizaciones:%s" % (config("app_name"), tipo, accion), args=(id,)
    )


def pathFacturar(id):
    return reverse(
        "facturas:facturarPractica", args=(id,)
    )


def pathReporte(tipo):
    return reverse(
        "%s:%s:reporte" % (config("app_name"), tipo)
    )


def errorAccion(accion=None, descripcion=None):
    titulo = "Error"
    if isinstance(accion, Practica.Acciones):
        accion = accion.value
    if type(accion)==str:
        titulo += " al %s" % accion
    if descripcion is None:
        descripcion = "Ocurrio un error, la accion no pudo completarse."
    return {
        "titulo" : titulo,
        "descripcion" : descripcion,
    }


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

    etiquetas = (
        "tipo",
        "initialPractica",
        "initialServicios",
        "initialProductos"
    )

    for etiqueta in etiquetas:
        clave = "practicas_crear_%d_%s" % (id, etiqueta)
        if clave in session:
            del session[clave]


def crearContexto(request, idCreacion, tipoPractica=None):

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


def calcularPrecio(detalles, porcentajeRecargo=0):
    recargo = 0
    precioProductos = sum([ detalle.precioTotal() for detalle in detalles["productos"] ])
    precioServicios = sum([ detalle.precioTotal() for detalle in detalles["servicios"] ])
    precio = precioProductos + precioServicios
    if porcentajeRecargo > 0:
        recargo = precio * porcentajeRecargo / Decimal(100)
    return precio + recargo


def calcularDuracion(servicios):

    return sum([
        (detalle.servicio.tiempoEstimado * detalle.cantidad) for detalle in servicios
    ])


def buscarProductos(servicios):

    listado = []
    datos = {}

    for detalleServicio in servicios:
        try:
            servicio = Servicio.objects.habilitados().get(id=detalleServicio["servicio"])
        except Servicio.DoesNotExist:
            raise VeterinariaPatagonicaError(
                "Error",
                "El servicio con id %d no existe o se encuentra deshabilitado" % detalleServicio["servicio"]
            )
        cantidadServicio = detalleServicio['cantidad']
        for detalleProducto in servicio.servicio_productos.all():
            if detalleProducto.producto.baja:
                raise VeterinariaPatagonicaError(
                    "Error",
                    "El producto %s (%d) del servicio %s (%d)  se encuentra deshabilitado" % (
                        detalleProducto.producto.nombre,
                        detalleProducto.producto.id,
                        servicio.nombre,
                        servicio.id,
                    )
                )
            else:
                producto = detalleProducto.producto.id
                cantidadProducto = detalleProducto.cantidad

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
    servicios  = Servicio.objects.habilitados().filter( id__in=cantidades.keys() )

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
    productos  = Producto.objects.habilitados().filter( id__in=cantidades.keys() )

    detalles = []
    for producto in productos:
        detalles.append(PracticaProducto(
            producto = producto,
            cantidad = cantidades[producto.pk],
            precio = producto.precioDeCompra
        ))

    return detalles


def obtenerDetalles(request, idCreacion):

    initialProductos = obtener(request.session, idCreacion, "initialProductos")
    productos = crearDetallesProductos(initialProductos)

    initialServicios = obtener(request.session, idCreacion, "initialServicios")
    servicios = crearDetallesServicios(initialServicios)

    return {
        "productos" : productos,
        "servicios" : servicios,
    }


def obtenerPractica(request, idCreacion):

    initial = obtener(request.session, idCreacion, "initialPractica")
    tipo = obtener(request.session, idCreacion, "tipo")
    tipo = Areas.codificar(tipo)
    practica = Practica(
        tipo=tipo,
        cliente_id=initial["cliente"],
        tipoDeAtencion_id=initial["tipoDeAtencion"]
    )
    return practica


def verificarHabilitados(practica, servicios, productos):

    if practica.cliente.baja:
        raise VeterinariaPatagonicaError(descripcion="El cliente con DNI/CUIT %s no se encuentra habilitado." % practica.cliente.dniCuit)
    if practica.mascota is not None and practica.mascota.baja:
        raise VeterinariaPatagonicaError(descripcion="La mascota con patente %s no se encuentra habilitada." % practica.mascota.patente)
    if practica.tipoDeAtencion.baja:
        raise VeterinariaPatagonicaError(descripcion="El tipo de atención '%s' (%d) no se encuentra habilitado." % (practica.tipoDeAtencion.id, practica.tipoDeAtencion.nombre))
    for detalle in servicios:
        if detalle.servicio.baja:
            raise VeterinariaPatagonicaError(descripcion="El servicio '%s' (%d) no se encuentra habilitado." % (detalle.servicio.nombre, detalle.servicio.id))
    for detalle in productos:
        if detalle.producto.baja:
            raise VeterinariaPatagonicaError(descripcion="El producto '%s' (%d) no se encuentra habilitado." % (detalle.producto.nombre, detalle.producto.id))


def persistir(usuario, practica, detalles, accion, argumentos):

    try:
        with transaction.atomic():
            practica.save(force_insert=True, usuario=usuario)
            practica.practica_servicios.set(detalles["servicios"], bulk=False)
            practica.practica_productos.set(detalles["productos"], bulk=False)
            verificarHabilitados(practica, detalles["servicios"], detalles["productos"])
    except dbError as excepcion:
        raise VeterinariaPatagonicaError(
            "Error en base de datos",
            "Ocurrio un error al intentar guardar los datos, la %s no pudo ser creada" % practica.nombreTipo()
        )
    try:
        practica.hacer(usuario, accion, **argumentos)
    except:
        practica.delete()
        raise
    return practica


def accionesIniciales(usuario, area):
    retorno = set()
    for actualizacion in Practica.Acciones.iniciales(area.codigo()):
        if permisos.paraCrear(usuario, area, accion=actualizacion):
            retorno.add(actualizacion)

    return retorno


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

    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

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
    delta = timedelta(minutes=duracion)
    ahora = datetime.now().replace(second=0, microsecond=0)
    inicio = ahora + timedelta(minutes=10)
    finalizacion = inicio + delta
    busquedas = 100

    cuando = None
    while (cuando is None) and busquedas:
        horarios = Programada.horariosDisponibles(inicio, finalizacion, minimo=delta)
        if len(horarios):
            cuando = horarios[0][0]
        else:
            finalizacion = finalizacion + delta
            inicio = inicio + delta
            busquedas -= 1

    if cuando is None:
        cuando = ahora + timedelta(minutes=10)

    initial = {
        "desde" : cuando,
        "hasta" : cuando + delta,
        "duracion" : duracion,
        "adelanto" : adelanto,
    }

    if ("initial" in kwargs) and (kwargs["initial"] is not None):
        initial.update(kwargs["initial"])
    kwargs["initial"] = initial
    return ProgramadaForm(*args, precio=precio, practica=practica, minimo=datetime.now(), **kwargs)


def formReprogramar(*args, practica=None, **kwargs):

    if practica is not None:
        estado = practica.estado()
        cuando = estado.inicio
        duracion = estado.duracion()
    else:
        raise VeterinariaPatagonicaError(
            "Error",
            "No se puede crear el formulario de reprogramacion sin una practica"
        )
    initial = {
        "desde" : cuando,
        "hasta" : cuando + timedelta(minutes=duracion),
        "duracion" : duracion,
    }

    if not "initial" in kwargs:
        kwargs["initial"] = {}
    kwargs["initial"].update(initial)
    return ReprogramadaForm(*args, practica=practica, minimo=datetime.now(), **kwargs)


def formRealizar(*args, practica=None, duracion=config("duracion"), **kwargs):

    minimo = None
    finalizacion = None
    inicio = None

    if practica is not None:
        estado = practica.estado()
        if isinstance(estado, Estado):
            minimo = practica.estado().cotaInicio()
        if isinstance(estado, Programada):
            finalizacion = estado.finalizacion
            inicio = estado.inicio
            duracion = estado.duracion()
    if finalizacion is None:
        finalizacion = datetime.now().replace(second=0, microsecond=0)+timedelta(minutes=1)
    if inicio is None:
        inicio = finalizacion - timedelta(minutes=duracion)
    if minimo is not None and inicio < minimo:
        inicio = minimo.replace(second=0, microsecond=0)+timedelta(minutes=1)
        if inicio >= finalizacion:
            duracion = 1
            finalizacion = inicio + timedelta(minutes=1)
        else:
            duracion = ceil((finalizacion - inicio).seconds / 60)
            finalizacion = inicio + timedelta(minutes=duracion)

    initial = {
        "desde" : inicio,
        "hasta" : finalizacion,
        "duracion" : duracion,
    }

    if not "initial" in kwargs:
        kwargs["initial"] = {}
    kwargs["initial"].update(initial)
    ahora = datetime.now().replace(second=0, microsecond=0)+timedelta(minutes=1)
    return RealizadaForm(*args, practica=practica, minimo=minimo, maximo=ahora, **kwargs)


def itemReporte(usuario, seccion, area):
    nombre = area.nombre()
    nombrePlural = area.nombrePlural()
    if usuario.has_perm("GestionDePracticas.ver_reporte_%s" % nombre):
        seccion.append(
            (pathReporte(nombre), "Ver reporte de %s" % nombrePlural)
        )


def itemCrear(usuario, seccion, area):
    nombre = area.nombre()
    if usuario.has_perm("GestionDePracticas.crear_%s_atendida" % nombre):
        seccion.append(
            (pathCrear(nombre), "Crear %s" % nombre)
        )


def itemListarTurnos(usuario, seccion, area):
    nombre = area.nombre()
    atendidas = "GestionDePracticas.realizar_%s_programada_atendida" % nombre
    noAtendidas = "GestionDePracticas.realizar_%s_programada_no_atendida" % nombre
    if usuario.has_perm(atendidas) or usuario.has_perm(noAtendidas):
        seccion.append(
            (pathListarTurnosPendientes(nombre), "Listar turnos de %s pendientes" % nombre)
        )


def itemListarRealizaciones(usuario, seccion):

    if permisos.filtroPermitidas(usuario, Practica.Acciones.realizar) is not None:
        seccion.append(
            (pathListarRealizaciones(), "Listar practicas realizadas por %s" % usuario.username)
        )


def itemListar(usuario, seccion, area):
    nombre = area.nombre()
    if permisos.filtroPermitidas(usuario, Practica.Acciones.listar, areas=area) is not None:
        seccion.append(
            (pathListar(nombre), "Listar %ss" % nombre)
        )


def itemExportar(usuario, seccion, formato, area):
    nombre = area.nombre()
    if permisos.filtroPermitidas(usuario, Practica.Acciones["exportar_"+formato], areas=area) is not None:
        seccion.append(
            (pathExportar(nombre, formato), "Exportar %ss en formato %s" % (nombre, formato))
        )


def itemsAcciones(usuario, seccion, acciones, practica):

    generadoresUrls = {
        Practica.Acciones.modificar : lambda practica: pathModificarRealizacion(practica.nombreTipo(), practica.id),
        Practica.Acciones.ver_informacion_general : lambda practica: pathVer(practica.nombreTipo(), practica.id),
        Practica.Acciones.ver_informacion_clinica : lambda practica: pathVerInformacionClinica(practica.nombreTipo(), practica.id),
        Practica.Acciones.modificar_informacion_clinica : lambda practica: pathModificarInformacionClinica(practica.nombreTipo(), practica.id),
        Practica.Acciones.programar : lambda practica: pathActualizar(practica.nombreTipo(), Practica.Acciones.programar.name, practica.id),
        Practica.Acciones.reprogramar : lambda practica: pathActualizar(practica.nombreTipo(), Practica.Acciones.reprogramar.name, practica.id),
        Practica.Acciones.realizar : lambda practica: pathActualizar(practica.nombreTipo(), Practica.Acciones.realizar.name, practica.id),
        Practica.Acciones.cancelar : lambda practica: pathActualizar(practica.nombreTipo(), Practica.Acciones.cancelar.name, practica.id),
        Practica.Acciones.facturar : lambda practica: pathFacturar(practica.id)
    }

    posibles = practica.estado().accionesPosibles().intersection(set(acciones))
    for accion in acciones:
        if not accion in posibles:
            continue
        if permisos.paraPractica(usuario, accion, practica):
            url = generadoresUrls[accion](practica)
            seccion.append( (url, accion) )


def menuAcciones(usuario, accion, practica):

    menu = [[], [], [], [], []]
    area = Areas[practica.tipo]

    modificar = [ item for item in [
        Practica.Acciones.modificar,
        Practica.Acciones.modificar_informacion_clinica,
        Practica.Acciones.ver_informacion_clinica
    ] if item != accion ]

    actualizar = [ item for item in [
        Practica.Acciones.presupuestar,
        Practica.Acciones.programar,
        Practica.Acciones.reprogramar,
        Practica.Acciones.cancelar,
        Practica.Acciones.realizar,
        Practica.Acciones.facturar
    ] if item != accion ]

    ver = [ item for item in [
        Practica.Acciones.ver_informacion_general
    ] if item != accion ]

    itemsAcciones(
        usuario,
        menu[0],
        actualizar,
        practica
    )
    itemsAcciones(
        usuario,
        menu[1],
        modificar,
        practica
    )
    itemsAcciones(
        usuario,
        menu[2],
        ver,
        practica
    )
    itemListar(usuario, menu[3], area)
    itemCrear(usuario, menu[4], area)

    return [ item for item in menu if len(item) ]


def menuExportar(usuario, formato, area):
    menu = [[],[]]
    if formato != "xlsx":
        itemExportar(usuario, menu[0], "xlsx", area)
    itemListar(usuario, menu[1], area)
    return [ item for item in menu if len(item) ]


def enlacesHistorial(usuario, practica, actual):

    enlaces = []
    acciones = Practica.Acciones.ver_informacion_general

    if permisos.paraPractica(usuario, acciones, practica):
        for n, estado in enumerate( practica.estados.all() ):
            if (n == 0):
                continue
            url = pathVer(practica.nombreTipo(), practica.id, n) if n != actual else ""
            enlaces.append( [url, estado.related()] )

    return enlaces


class GestorListadoPractica(GestorListadoQuerySet):

    def hacerSeleccion(self, *args, **kwargs):
        super().hacerSeleccion(*args, **kwargs)

        opciones = {
            "creada_por" : True,
            "atendida_por" : True,
            "marca_creacion" : True,
            "marca_ultima_actualizacion" : True,
            "estado_actual" : True
        }

        if self.seleccionar:
            opciones["creada_por"] = self.campos["creadapor"]["visible"]
            opciones["atendida_por"] = self.campos["atendidapor"]["visible"]
            opciones["estado_actual"] = self.campos["estadoactual"]["visible"]
            opciones["marca_creacion"] = self.campos["marcacreacion"]["visible"]
            opciones["marca_ultima_actualizacion"] = self.campos["marcaultimaactualizacion"]["visible"]

        self.queryset = Estado.anotarPracticas(
            self.queryset,
            **opciones
        )


class GestorListadoRealizacion(GestorListadoQuerySet):

    def hacerSeleccion(self, *args, **kwargs):
        super().hacerSeleccion(*args, **kwargs)

        opciones = {
            "creada_por" : True,
            "atendida_por" : True,
            "marca_creacion" : True,
            "marca_ultima_actualizacion" : True,
            "estado_actual" : True,
            "realizada_por" : True,
            "horario_realizacion" : True,
            "duracion_realizacion" : True
        }

        if self.seleccionar:
            opciones["creada_por"] = self.campos["creadapor"]["visible"]
            opciones["atendida_por"] = self.campos["atendidapor"]["visible"]
            opciones["estado_actual"] = self.campos["estadoactual"]["visible"]
            opciones["marca_creacion"] = self.campos["marcacreacion"]["visible"]
            opciones["marca_ultima_actualizacion"] = self.campos["marcaultimaactualizacion"]["visible"]
            opciones["horario_realizacion"] = self.campos["iniciorealizacion"]["visible"]
            opciones["duracion_realizacion"] = self.campos["duracionrealizacion"]["visible"]

        self.queryset = Realizada.anotarPracticas(
            self.queryset,
            **opciones
        )


class GestorListadoTurnos(GestorListadoQuerySet):

    def hacerSeleccion(self, *args, **kwargs):
        super().hacerSeleccion(*args, **kwargs)

        opciones = {
            "creada_por" : True,
            "marca_creacion" : True,
            "marca_ultima_actualizacion" : True,
            "programada_por" : True,
            "horario_turno" : True,
            "duracion_turno" : True,
            "reprogramaciones" : True
        }

        if self.seleccionar:
            opciones["creada_por"] = self.campos["creadapor"]["visible"]
            opciones["marca_creacion"] = self.campos["marcacreacion"]["visible"]
            opciones["marca_ultima_actualizacion"] = self.campos["marcaultimaactualizacion"]["visible"]
            opciones["programada_por"] = self.campos["programadapor"]["visible"]
            opciones["horario_turno"] = self.campos["inicioturno"]["visible"]
            opciones["duracion_turno"] = self.campos["duracionturno"]["visible"]
            opciones["reprogramaciones"]= self.campos["reprogramaciones"]["visible"]

        self.queryset = Programada.anotarPracticas(
            self.queryset,
            **opciones
        )
