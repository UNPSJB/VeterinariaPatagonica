from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied

from VeterinariaPatagonica.tools import GestorListadoQuerySet, R
from VeterinariaPatagonica.errores import VeterinariaPatagonicaError
from Apps.GestionDePracticas import permisos
from Apps.GestionDePracticas.models.practica import Practica
from Apps.GestionDeFacturas.models import Factura
from .models import Pago
from .forms import *

LOGIN_URL="/login/"


def menuCrear(usuario, factura):
    menu = [[], []]
    poseidos = usuario.get_all_permissions()

    pago = factura.pago if factura.estaPaga() else None
    if pago and "GestionDePagos.pago_ver" in poseidos:
        menu[0].append( (reverse("pagos:ver", args=(pago.id,)), "Ver Pago") )

    if pago is None and "GestionDeFacturas.factura_ver_no_pagas" in poseidos:
        menu[0].append( (reverse("facturas:ver", args=(factura.id,)), "Ver factura") )
    elif pago is not None and "GestionDeFacturas.factura_ver_pagas" in poseidos:
        menu[0].append( (reverse("facturas:ver", args=(factura.id,)), "Ver factura") )

    practica = factura.practica
    if (practica is not None) and permisos.paraPractica(usuario, Practica.Acciones.ver_informacion_general, practica):
        menu[0].append( (reverse(
            "practicas:%s:ver:practica" % practica.nombreTipo(), args=(practica.id,)
        ), "Ver practica") )

    if "GestionDePagos.pago_listar" in poseidos:
        menu[1].append( (reverse("pagos:listar"), "Listar pagos") )

    pagas = "GestionDeFacturas.factura_listar_pagas"
    noPagas = "GestionDeFacturas.factura_listar_no_pagas"
    if (pagas in poseidos) or (noPagas in poseidos):
        menu[1].append( (reverse("facturas:listar"), "Listar facturas") )

    return [ item for item in menu if len(item)]

def menuVer(usuario, pago):
    menu = [[], []]
    poseidos = usuario.get_all_permissions()

    if "GestionDeFacturas.factura_ver_pagas" in poseidos:
        menu[0].append( (reverse("facturas:ver", args=(pago.factura.id,)), "Ver factura") )

    practica = pago.factura.practica
    if (practica is not None) and permisos.paraPractica(usuario, Practica.Acciones.ver_informacion_general, practica):
        menu[0].append( (reverse(
            "practicas:%s:ver:practica" % practica.nombreTipo(), args=(practica.id,)
        ), "Ver practica") )

    if "GestionDePagos.pago_listar" in poseidos:
        menu[1].append( (reverse("pagos:listar"), "Listar pagos") )

    pagas = "GestionDeFacturas.factura_listar_pagas"
    noPagas = "GestionDeFacturas.factura_listar_no_pagas"
    if (pagas in poseidos) or (noPagas in poseidos):
        menu[1].append( (reverse("facturas:listar"), "Listar facturas") )

    return [ item for item in menu if len(item)]

def menuListar(usuario):
    menu = [[]]
    poseidos = usuario.get_all_permissions()

    pagas = "GestionDeFacturas.factura_listar_pagas"
    noPagas = "GestionDeFacturas.factura_listar_no_pagas"
    if (pagas in poseidos) or (noPagas in poseidos):
        menu[0].append( (reverse("facturas:listar"), "Listar facturas") )

    return [ item for item in menu if len(item)]


def facturasAdeudadas(factura, tope):
    retorno = Factura.objects.filter(
        cliente=factura.cliente,
        pago=None
    ).exclude(
        id=factura.id
    ).order_by("fecha")[0:tope]
    return retorno


def buscarFactura(id):
    factura = None
    try:
        factura = Factura.objects.get(id=id)
    except Factura.DoesNotExist:
        raise VeterinariaPatagonicaError(
            "Error",
            "Factura %d no encontrada" % id
        )
    else:
        if factura.estaPaga():
            raise VeterinariaPatagonicaError(
                "Factura paga",
                "Ya se encuentra registrado el pago de la factura %d" % id
            )

    return factura


def crear(request, id):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (LOGIN_URL, request.path))

    if not request.user.has_perm("GestionDePagos.pago_crear"):
        raise PermissionDenied()

    context = { "errores" : [], "accion" : None }

    try:
        factura = buscarFactura(id)
    except VeterinariaPatagonicaError as error:
        context["errores"].append(error)
    else:
        context["accion"] = "Guardar"
        context["menu"] = menuCrear(request.user, factura)
        context["factura"] = factura
        if request.user.has_perm("GestionDeFacturas.factura_listar"):
            otras = facturasAdeudadas(factura, 10)
            context["otrasAdeudadas"] = otras

        if request.method == "POST":
            form = PagoForm(request.POST)
            if form.is_valid():
                pago = Pago(factura=factura)
                try:
                    pago.save(force_insert=True)
                except dbError as error:
                    context["errores"].append({
                        "titulo":"Error al guardar datos",
                        "descripcion":"No se pudo guardar el pago en la base de datos."
                    })
                else:
                    return HttpResponseRedirect(
                        reverse("pagos:ver", args=(pago.id,))
                    )
        else:
            form = PagoForm()

        context["form"]    = form

    template = loader.get_template("OtraGestionDePagos/crear.html")
    return HttpResponse(template.render(context, request))


def listar(request):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (LOGIN_URL, request.path))

    if not request.user.has_perm("GestionDePagos.pago_listar"):
        raise PermissionDenied()

    pagos = Pago.objects.all()

    gestor = GestorListadoQuerySet(
        campos = [
            ["fechaPago", "Fecha de pago"],
            ["fechaFactura", "Fecha de facturación"],
            ["importe", "Importe"],
            ["cliente", "Cliente"],
            ["numeroFactura", "Numero de factura"],
            ["tipoFactura", "Tipo de factura"],
        ],
        iniciales={
            "seleccion" : (
                "fechaPago",
                "importe",
                "cliente",
                "numeroFactura",
                "tipoFactura",
            ),
            "paginacion" : {
                "cantidad" : 50
            },
            "orden" : (
                ("fechaPago", False),
                ("fechaFactura", False),
                ("tipoFactura", True)
            )
        },
        clases={ "filtrado" : FiltradoPagoForm },
        queryset=pagos,
        mapaFiltrado={
            "cliente" : lambda value: R(
                factura__cliente__apellidos__icontains=value,
                factura__cliente__nombres__icontains=value,
                factura__cliente__dniCuit__icontains=value,
            ),
            "tipo_factura" : "factura__tipo",
            "fecha_desde" : "fecha__gte",
            "fecha_hasta" : "fecha__lte",
            "importe_desde" : "factura__total__gte",
            "importe_hasta" : "factura__total__lte",
        },
        mapaOrden={
            "fechaPago" : ["fecha"],
            "fechaFactura" : ["factura__fecha"],
            "importe" : ["factura__total"],
            "cliente" : ["factura__cliente__apellidos", "factura__cliente__nombres"],
            "numeroFactura" : ["factura__id"],
            "tipoFactura" : ["factura__tipo"],
        },
    )

    gestor.cargar(request)
    gestor.paginacion["cantidad"].label = "Pagos por pagina"

    template = loader.get_template("OtraGestionDePagos/listar.html")
    context = {
        "gestor" : gestor,
        "menu" : menuListar(request.user)
    }
    return HttpResponse(template.render( context, request ))


def ver(request, id):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (LOGIN_URL, request.path))

    if not request.user.has_perm("GestionDePagos.pago_ver"):
        raise PermissionDenied()

    pago = Pago.objects.get(id=id)

    context = {
        "pago" : pago,
        "menu" : menuVer(request.user, pago)
    }

    template = loader.get_template("OtraGestionDePagos/ver.html")
    return HttpResponse(template.render( context, request ))