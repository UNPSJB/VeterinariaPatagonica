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

def facturasAdeudadas(usuario, cliente, maxima):
    retorno = None
    if usuario.has_perm("GestionDeFacturas.factura_listar"):
        retorno = Factura.objects.filter(
            cliente=cliente,
            pago=None
        ).order_by("fecha")[0:maxima]
    return retorno


def crear(request, id):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (LOGIN_URL, request.path))

    if not request.user.has_perm("GestionDePagos.pago_crear"):
        raise PermissionDenied()

    try:
        factura = Factura.objects.get(id=id)
        if factura.estaPaga():
            raise VeterinariaPatagonicaError(
                "Factura paga",
                "Ya se encuentra registrado el pago de la factura %d" % factura.id
            )
    except VeterinariaPatagonicaError as excepcion:
        context = {
            "errores" : [excepcion.error()],
            "accion" : None ,
            "menu" : menuCrear(request.user, factura)
        }
    else:
        context = {
            "errores" : [],
            "accion" : "Guardar",
            "menu" : menuCrear(request.user, factura),
            "facturasAdeudadas" : facturasAdeudadas(request.user, factura.cliente, 5),
            "factura" : factura,
        }

        if request.method == "POST":
            form = PagoForm(request.POST)

            if form.is_valid():
                pago = Pago(
                    importeTotal=factura.total,
                    factura=factura
                )
                try:
                    pago.save(force_insert=True)
                except ErrorBD as error:
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
            ["fechaPago", "Fecha"],
            ["fechaFactura", "Fecha de facturación"],
            ["importePago", "Importe"],
            ["importeFactura", "Importe de facturación"],
            ["cliente", "Cliente"],
            ["numeroFactura", "Numero de factura"],
            ["tipoFactura", "Tipo de factura"],
        ],
        iniciales={
            "seleccion" : (
                "fechaPago",
                "importePago",
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
            "importe_desde" : "importeTotal__gte",
            "importe_hasta" : "importeTotal__lte",
        },
        mapaOrden={
            "fechaPago" : ["fecha"],
            "fechaFactura" : ["factura__fecha"],
            "importePago" : ["importeTotal"],
            "importeFactura" : ["factura__total"],
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



# from django.shortcuts import render
# from django.template import loader
# from django.http import Http404, HttpResponse, HttpResponseRedirect
# from django.core.exceptions import ObjectDoesNotExist
# from django.contrib.auth.decorators import login_required, permission_required
# from .models import Pago
# #from .forms import PagoFormFactory
# from .forms import PagoForm
# from Apps.GestionDeFacturas.models import Factura
# from VeterinariaPatagonica import tools
# from django.utils import timezone

# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# def pago(request):

#     context = {}#Defino el contexto.
#     template = loader.get_template('GestionDePagos/GestionDePagos.html')#Cargo el template desde la carpeta templates/GestionDePagos.
#     return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.


# @login_required(redirect_field_name='proxima')
# @permission_required('GestionDePagos.add_Pago', raise_exception=True)
# def crear(request, idFactura = None): #, factura_id=None

#     factura = Factura.objects.get(id=idFactura)
#     context = {'usuario': request.user}

#     pagos= len(Pago.objects.filter(factura=idFactura))

#     if not pagos:

#         pago=Pago(importeTotal=factura.sumar_total_adelanto, factura=factura)

#         if request.method == 'POST':
#             formulario = PagoForm(request.POST, instance=pago)
#             if formulario.is_valid():
#                 pago = formulario.save()
#                 return HttpResponseRedirect("/GestionDePagos/ver/{}".format(pago.id))
#             else:
#                 context['formulario'] = formulario
#         else:
#             context['formulario'] = PagoForm(instance=pago)
#     #else:

#     template = loader.get_template('GestionDePagos/formulario.html')
#     return HttpResponse(template.render(context, request))

#     '''factura = None
#     if factura_id:
#         factura = Factura.objects.get(pk=factura_id)
#     PagoForm = PagoFormFactory(pago, factura)'''





# @login_required(redirect_field_name='proxima')
# @permission_required('GestionDePagos.delete_Pago', raise_exception=True)
# def eliminar(request, id):

#     try:
#         pago = Pago.objects.get(id=id)
#     except ObjectDoesNotExist:
#         raise Http404()

#     if request.method == 'POST':

#         pago.delete()
#         return HttpResponseRedirect( "/GestionDePagos/" )

#     else:

#         template = loader.get_template('GestionDePagos/eliminar.html')
#         context = {
#             'usuario' : request.user,
#             'id' : id
#         }

#         return HttpResponse( template.render( context, request) )

# def ver(request, id):

#     try:
#         pago = Pago.objects.get(id=id)
#     except ObjectDoesNotExist:
#         raise Http404("No encontrado", "El pago con id={} no existe.".format(id))

#     template = loader.get_template('GestionDePagos/ver.html')
#     contexto = {
#         'pago': pago,
#         'usuario': request.user
#     }

#     return HttpResponse(template.render(contexto, request))

# def listar(request):
#     pagosQuery = Pago.objects.all()
#     pagos = pagosQuery.filter(tools.paramsToFilter(request.GET, Pago))
#     template = loader.get_template('GestionDePagos/listar.html')


#     paginator = Paginator(pagosQuery, 1)
#     page = request.GET.get('page')

#     try:
#         pagos = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         pagos = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         pagos = paginator.page(paginator.num_pages)

#     contexto = {
#         'pagosQuery' : pagosQuery,
#         'usuario' : request.user,
#         'pagos': pagos,
#     }
#     return HttpResponse(template.render(contexto, request))
