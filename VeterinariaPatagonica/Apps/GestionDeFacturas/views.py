from datetime import datetime

from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.validators import MinValueValidator
from django.db import transaction
from django.db.models import Sum, Q
from django.db.utils import Error as ErrorBD

from VeterinariaPatagonica.forms import ExportarForm
from VeterinariaPatagonica.tools import GestorListadoQuerySet, guardarWorkbook
from VeterinariaPatagonica.errores import VeterinariaPatagonicaError
from Apps.GestionDePracticas import permisos
from Apps.GestionDeClientes.models import Cliente
from Apps.GestionDePracticas.models.practica import Practica
from Apps.GestionDePracticas.gestionDePracticas import pathVer
from .models import Factura
from .forms import *

from openpyxl import Workbook

LOGIN_URL="/login/"



class GestorListadoFacturas(GestorListadoQuerySet):

    def hacerSeleccion(self, *args, **kwargs):
        super().hacerSeleccion(*args, **kwargs)

        if self.campos["importeVentas"]["visible"]:
            self.queryset = self.queryset.annotate(
                importe_ventas=Sum("detalles_producto__subtotal")
            )

def verificarFacturacion(usuario, practica):

    if not permisos.paraPractica(usuario, Practica.Acciones.facturar, practica):
        raise VeterinariaPatagonicaError(
            "Permiso denegado",
            "El usuario %s no tiene permisos suficientes para facturar la practica solicitada (%s)" % (usuario.username, str(practica))
        )

    if not practica.esPosible(Practica.Acciones.facturar):
        raise VeterinariaPatagonicaError(
            "%s no facturable" % practica.nombreTipo().capitalize(),
            "La %s no puede facturarse" % practica.nombreTipo()
        )

    if Factura.objects.filter(practica=practica).count():
        raise VeterinariaPatagonicaError(
            "%s facturada" % practica.nombreTipo().capitalize(),
            "No puede volver a facturarse la %s" % practica.nombreTipo()
        )

def menuCrear(usuario, practica=None):
    menu = [[], []]
    poseidos = usuario.get_all_permissions()

    if practica is not None:
        if permisos.paraPractica(usuario, Practica.Acciones.ver_informacion_general, practica):
            menu[0].append( (reverse(
                "practicas:%s:ver:practica" % practica.nombreTipo(), args=(practica.id,)
            ), "Ver practica") )

        cliente = practica.cliente if not practica.cliente.baja else None
        if cliente and "GestionDeClientes.cliente_ver_habilitados" in poseidos:
            menu[0].append( (reverse("clientes:clienteVer", args=(cliente.id,)), "Ver cliente") )

    permitidas = filtrosPara(usuario, "listar")
    if permitidas is not None:
        menu[1].append(
            (reverse("facturas:listar"), "Listar facturas")
        )
    if "GestionDePagos.pago_listar" in poseidos:
        menu[1].append( (reverse("pagos:listar"), "Listar pagos") )
    return [ item for item in menu if len(item)]

def menuVer(usuario, factura):
    menu = [[], [], []]
    poseidos = usuario.get_all_permissions()

    if factura.estaPaga():
        if "GestionDePagos.pago_ver" in poseidos:
            menu[1].append( (reverse("pagos:ver", args=(factura.pago.id,)), "Ver pago") )
    else:
        if "GestionDePagos.pago_crear" in poseidos:
            menu[0].append( (reverse("pagos:crear", args=(factura.id,)), "Pagar factura") )

    practica = factura.practica
    if practica is not None:
        if permisos.paraPractica(usuario, Practica.Acciones.ver_informacion_general, practica):
            menu[1].append( (reverse(
                "practicas:%s:ver:practica" % practica.nombreTipo(), args=(practica.id,)
            ), "Ver practica") )

        cliente = practica.cliente if not practica.cliente.baja else None
        if cliente and "GestionDeClientes.cliente_ver_habilitados" in poseidos:
            menu[1].append( (reverse("clientes:clienteVer", args=(cliente.id,)), "Ver cliente") )

    permitidas = filtrosPara(usuario, "listar")
    if permitidas is not None:
        menu[2].append(
            (reverse("facturas:listar"), "Listar facturas")
        )
    if "GestionDePagos.pago_listar" in poseidos:
        menu[2].append( (reverse("pagos:listar"), "Listar pagos") )
    return [ item for item in menu if len(item)]

def menuListar(usuario, accion):
    menu = [[], []]
    if accion != "exportar_xlsx":
        permitidas = filtrosPara(usuario, "exportar_xlsx")
        if permitidas is not None:
            menu[0].append(
                (reverse("facturas:exportar:xlsx"), "Exportar en xlsx")
            )
    if accion != "listar":
        permitidas = filtrosPara(usuario, "listar")
        if permitidas is not None:
            menu[1].append(
                (reverse("facturas:listar"), "Listar facturas")
            )
    if usuario.has_perm("GestionDePagos.pago_listar"):
        menu[1].append( (reverse("pagos:listar"), "Listar pagos") )
    return [ item for item in menu if len(item)]


def filtrosPara(usuario, accion):
    permisos = usuario.get_all_permissions()
    filtros = []
    retorno = None
    if usuario.has_perm("GestionDeFacturas.factura_%s_pagas" % accion):
        filtros.append( ~Q(pago=None) )
    if usuario.has_perm("GestionDeFacturas.factura_%s_no_pagas" % accion):
        filtros.append( Q(pago=None) )
    if len(filtros):
        if len(filtros) == 2:
            retorno = Q()
        else:
            retorno = filtros[0]
    return retorno



def respuestaXlsx(resultados, visibles, encabezados=None):

    filename = "facturas-%s" % datetime.now().strftime("%d%m%Y-%H%M%S-%f")
    libro = Workbook()
    hoja = libro.create_sheet(filename, 0)
    fila = 1

    if encabezados:
        columna = 1
        for encabezado in encabezados:
            celda = hoja.cell(fila, columna, encabezado)
            columna += 1
        fila += 1

    for resultado in resultados:
        columna = 1
        if visibles[0]:
            celda = hoja.cell(fila, columna, resultado.id)
            columna += 1
        if visibles[1]:
            celda = hoja.cell(fila, columna, resultado.tipo)
            columna += 1
        if visibles[2]:
            celda = hoja.cell(fila, columna, resultado.total)
            columna += 1
        if visibles[3]:
            importe = resultado.pago.importeTotal if resultado.estaPaga() else None
            celda = hoja.cell(fila, columna, importe)
            columna += 1
        if visibles[4]:
            importe = resultado.practica.precio or None
            celda = hoja.cell(fila, columna, filamporte)
            columna += 1
        if visibles[5]:
            importe = resultado.importe_ventas or 0
            celda = hoja.cell(fila, columna, filamporte)
            columna += 1
        if visibles[6]:
            cliente = resultado.cliente
            tostr = "%s: %s %s" % (cliente.dniCuit, cliente.apellidos, cliente.nombres)
            celda = hoja.cell(fila, columna, tostr)
            columna += 1
        if visibles[7]:
            celda = hoja.cell(fila, columna, resultado.fecha)
            columna += 1
        if visibles[8]:
            fecha = resultado.pago.fecha or None
            celda = hoja.cell(fila, columna, fecha)
            columna += 1
        fila += 1

    response = HttpResponse(guardarWorkbook(libro), content_type="application/ms-excel")
    response["Content-Disposition"] = "attachment; filename=%s.xlsx" % filename
    return response


def facturarPractica(request, id):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (LOGIN_URL, request.path))

    if not request.user.has_perm("GestionDeFacturas.factura_crear"):
        raise PermissionDenied()

    try:
        practica = Practica.objects.get(id=id)
        verificarFacturacion(request.user, practica)
    except VeterinariaPatagonicaError as excepcion:
        context = {
            "errores" : [excepcion.error()],
            "accion" : None ,
            "menu" : menuCrear(request.user, practica)
        }
    else:
        context = {
            "facturacion" : {
                "practica" : practicaRealizadaSelectLabel(practica),
                "cliente" : clienteSelectLabel(practica.cliente)
            },
            "errores" : [],
            "accion" : "Guardar",
            "menu" : menuCrear(request.user, practica)
        }

        if request.method == "POST":
            acciones = AccionesFacturacionForm(request.POST)
            formset = ProductosFormSet(request.POST, prefix="producto")
            form = FacturarPracticaForm(request.POST, practica=practica, formsetProductos=formset)

            if form.is_valid() and formset.is_valid():

                if acciones.accion()=="guardar":
                    try:
                        with transaction.atomic():
                            factura = form.crearFactura()
                            practica.hacer(request.user, Practica.Acciones.facturar.name)
                    except ErrorBD as error:
                        context["errores"].append({
                            "titulo":"Error al guardar datos",
                            "descripcion":"No se pudo guardar la factura en la base de datos."
                        })
                    else:
                        return HttpResponseRedirect(
                            reverse("facturas:ver", args=(factura.id,))
                        )
        else:
            acciones = AccionesFacturacionForm()
            formset = ProductosFormSet(prefix="producto")
            form = FacturarPracticaForm(practica=practica, formsetProductos=formset)

        context["form"]     = form
        context['formset']  = formset
        context['acciones']  = acciones

    template = loader.get_template("OtraGestionDeFacturas/facturarPractica.html")
    return HttpResponse(template.render(context, request))

def facturar(request):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (LOGIN_URL, request.path))

    if not request.user.has_perm("GestionDeFacturas.factura_crear"):
        raise PermissionDenied()

    factura = None
    context = {
        "errores" : [],
        "accion" : "Guardar",
        "menu" : menuCrear(request.user)
    }

    if request.method == "POST":
        acciones = AccionesFacturacionForm(request.POST)
        formset = ProductosFormSet(request.POST, prefix="producto")
        form = FacturarForm(request.POST, formsetProductos=formset)

        if form.is_valid() and formset.is_valid():
            factura = form.factura()
            productos = form.productosFactura()
            practica = factura.practica

            try:
                if practica is not None:
                    verificarFacturacion(request.user, practica)
            except VeterinariaPatagonicaError as error:
                context["errores"].appned(error.diccionario())
            else:
                if acciones.accion()=="guardar":
                    try:
                        with transaction.atomic():
                            factura = form.crearFactura()
                            if practica is not None:
                                practica.hacer(request.user, Practica.Acciones.facturar.name)
                    except ErrorBD as error:
                        context["errores"].append({
                            "titulo":"Error al guardar datos",
                            "descripcion":"No se pudo guardar la factura en la base de datos."
                        })
                    else:
                        return HttpResponseRedirect(
                            reverse("facturas:ver", args=(factura.id,))
                        )
    else:
        acciones = AccionesFacturacionForm()
        formset = ProductosFormSet(prefix="producto")
        form = FacturarForm(formsetProductos=formset)

    context["form"]     = form
    context['formset']  = formset
    context['acciones']  = acciones

    template = loader.get_template("OtraGestionDeFacturas/facturar.html")
    return HttpResponse(template.render(context, request))

def listar(request):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (LOGIN_URL, request.path))

    permitidas = filtrosPara(request.user, "listar")
    if permitidas is None:
        raise PermissionDenied()
    facturas = Factura.objects.filter(permitidas)

    gestor = GestorListadoFacturas(
        campos = [
            ["id", "Número"],
            ["tipo", "Tipo"],
            ["total", "Importe"],
            ["pago", "Importe cobrado"],
            ["precioPractica", "Precio de practica"],
            ["importeVentas", "Importe por ventas"],
            ["cliente", "Cliente"],
            ["fecha", "Fecha"],
            ["fechaPago", "Fecha de pago"],
        ],
        iniciales={
            "seleccion" : (
                "tipo",
                "total",
                "pago",
                "cliente",
                "fecha",
            ),
            "paginacion" : {
                "cantidad" : 12,
            },
            "orden" : (
                ("fecha", False),
                ("total", False),
                ("tipo", True),
            ),
        },
        clases={ "filtrado" : FiltradoFacturaForm },
        queryset=facturas,
        mapaFiltrado=facturas.MAPEO_FILTRADO,
        mapaOrden=facturas.MAPEO_ORDEN,
    )

    gestor.cargar(request)
    gestor.paginacion["cantidad"].label = "Facturas por pagina"

    verPagas = request.user.has_perm("GestionDeFacturas.factura_ver_pagas")
    verNoPagas = request.user.has_perm("GestionDeFacturas.factura_ver_no_pagas")
    visibles = set()
    for factura in gestor.itemsActuales():
        if factura.estaPaga():
            if verPagas:
                visibles.add(factura.id)
        else:
            if verNoPagas:
                visibles.add(factura.id)

    template = loader.get_template("OtraGestionDeFacturas/listar.html")
    context = {
        "gestor" : gestor,
        "visibles" : visibles,
        "menu" : menuListar(request.user, "listar"),
    }

    return HttpResponse(template.render( context, request ))

def ver(request, id):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (LOGIN_URL, request.path))

    factura = Factura.objects.get(id=id)
    condicion = "pagas" if factura.estaPaga() else "no_pagas"
    if not request.user.has_perm("GestionDeFacturas.factura_ver_%s" % condicion):
        raise PermissionDenied()

    practica = factura.practica or None
    permisoVer = None
    if practica is not None:
        permisoVer =  permisos.paraPractica(
            request.user,
            Practica.Acciones.ver_informacion_general,
            practica
        )

    context = {
        "factura" : factura,
        "urlPractica" : pathVer(
            practica.nombreTipo(),
            practica.id
        ) if permisoVer else "",
        "menu" : menuVer(request.user, factura)
    }

    template = loader.get_template("OtraGestionDeFacturas/ver.html")
    return HttpResponse(template.render( context, request ))

def exportar(request, formato=None):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (LOGIN_URL, request.path))

    permitidas = filtrosPara(request.user, "exportar_%s" % formato)
    if permitidas is None:
        raise PermissionDenied()
    facturas = Factura.objects.filter(permitidas)

    gestor = GestorListadoFacturas(
        campos = [
            ["id", "Número"],
            ["tipo", "Tipo"],
            ["total", "Importe"],
            ["pago", "Importe cobrado"],
            ["precioPractica", "Precio de practica"],
            ["importeVentas", "Importe por ventas"],
            ["cliente", "Cliente"],
            ["fecha", "Fecha"],
            ["fechaPago", "Fecha de pago"],
        ],
        iniciales={
            "seleccion" : (
                "tipo",
                "total",
                "pago",
                "cliente",
                "fecha",
            ),
            "paginacion" : {
                "cantidad" : 25,
            },
        },
        clases={ "filtrado" : FiltradoFacturaForm },
        queryset=facturas,
        mapaFiltrado=facturas.MAPEO_FILTRADO,
        mapaOrden=facturas.MAPEO_ORDEN,
    )

    gestor.cargar(request)
    gestor.paginacion["cantidad"].label = "Facturas por pagina"
    exportar = ExportarForm(request.GET)
    accion = exportar.accion()
    visibles = [ gestor[campo]["visible"] for campo in gestor.columnas ]
    encabezados = [ gestor[campo]["etiqueta"] for campo in gestor.columnasVisibles ]

    if formato=="xlsx":
        listar=respuestaXlsx

    if accion=="exportar_pagina":
        response = listar(gestor.itemsActuales(), visibles, encabezados)
    elif accion=="exportar_todos":
        response = listar(gestor.items(), visibles, encabezados)
    else:
        template = loader.get_template("OtraGestionDeFacturas/exportar.html")
        context = {
            "formato" : formato,
            "gestor" : gestor,
            "exportar" : exportar,
            "menu" : menuListar(request.user, "exportar_"+formato),
        }
        response = HttpResponse(template.render(context, request))
    return response


# Create your views here.

# from django.shortcuts import render
# from django.template import loader
# from django.http import Http404, HttpResponse, HttpResponseRedirect
# from django.core.exceptions import ObjectDoesNotExist
# from django.contrib.auth.decorators import login_required, permission_required
# from .models import Factura
# from .forms import FacturaForm, DetalleFacturaBaseFormSet, DetalleFactura, DetalleFacturaForm, FacturaFormFactory
# from django.forms import modelformset_factory
# from VeterinariaPatagonica import tools
# from dal import autocomplete
# from django.db.models import Q
# from Apps.GestionDeClientes.models import Cliente
# from Apps.GestionDePracticas.models import Practica
# from Apps.GestionDeProductos.models import Producto
# from django.urls import reverse
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# from decimal import Decimal
# from django.utils import timezone
# from django.db import transaction
# from VeterinariaPatagonica.errores import VeterinariaPatagonicaError




# def facturas(request):

#     context = {}#Defino el contexto.
#     template = loader.get_template('GestionDeFacturas/GestionDeFacturas.html')#Cargo el template desde la carpeta templates/GestionDeFacturas.
#     return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.

# @login_required(redirect_field_name='proxima')
# @permission_required('GestionDeFacturas.add_Factura', raise_exception=True)
# def modificar(request, id = None):
#     factura = Factura.objects.get(id=id) if id is not None else None
#     context = {'usuario': request.user}
#     form = FacturaForm(instance=factura)
#     DetalleFacturaFormset = modelformset_factory(
#         DetalleFactura,
#         DetalleFacturaForm,
#         min_num=1,
#         extra=0,
#         can_delete=True,
#         formset=DetalleFacturaBaseFormSet)
#     if request.method == 'POST':
#         form = FacturaForm(request.POST, instance=factura)
#         formset = DetalleFacturaFormset(request.POST)
#         if form.is_valid() and formset.is_valid():
#             factura = form.save()
#             instances = formset.save(commit=False)
#             factura.calcular_subtotales(instances)
#             factura.precioTotal(instances)
#             for obj in formset.deleted_objects:#Bucle for que elimina los form que tienen tildado el checkbox "eliminar"
#                 obj.delete()
#             for detalle in instances:
#                 detalle.factura = factura
#                 detalle.save()
#             if factura.practica :
#                 if factura.practica.esPosible(Practica.Acciones.facturar):#Transiciona la practica seleccionada a facturada.
#                     factura.practica.hacer(request.user, Practica.Acciones.facturar.name)
#             return HttpResponseRedirect("/GestionDeFacturas/ver/{}".format(factura.id))

#         context['formulario'] = form
#         context['formset'] = formset
#     else:
#         context['formulario'] = form
#         qs = DetalleFactura.objects.none() if factura is None else factura.detalleFactura.all()#si ponemos "productos" no pincha. pero el modificar no muestra los items previamente agregados.
#         context["formset"] = DetalleFacturaFormset(queryset=qs)
#     template = loader.get_template('GestionDeFacturas/formulario.html')
#     return HttpResponse(template.render(context, request))

# @login_required(redirect_field_name='proxima')
# @permission_required('GestionDeFacturas.add_Factura', raise_exception=True)
# def crearFacturaPractica(request, id):
#     practica = Practica.objects.get(id=id)
#     context = {'usuario': request.user}
#     Form = FacturaFormFactory(instance=practica)
#     DetalleFacturaFormset = modelformset_factory(
#         DetalleFactura,
#         fields=("producto", "cantidad"), min_num=1,
#         formset=DetalleFacturaBaseFormSet)
#     if request.method == 'POST':
#         pass
#     context["practica"] = practica
#     context["form"] = Form(initial={})
#     context['formset'] = DetalleFacturaFormset(initial=practica.practicaproducto_set.values())
#     template = loader.get_template('GestionDeFacturas/formulario.html')
#     return HttpResponse(template.render(context, request))


# @login_required(redirect_field_name='proxima')
# @permission_required('GestionDeFacturas.delete_Factura', raise_exception=True)
# def eliminar(request, id):
#     try:
#         factura = Factura.objects.get(id=id)
#     except ObjectDoesNotExist:
#         raise Http404()
#     if request.method == 'POST':
#         factura.delete()
#         return HttpResponseRedirect( "/GestionDeFacturas/listar" )
#     else:
#         template = loader.get_template('GestionDeFacturas/eliminar.html')
#         context = {
#             'usuario' : request.user,
#             'id' : id
#         }
#         return HttpResponse( template.render( context, request) )

# def ver(request, id):  #, irAPagar=1
# #[TODO] ACA PINCHA. no arma el render.
# #    import ipdb
# #    ipdb.set_trace()
#     try:
#         factura = Factura.objects.get(id=id)
#     except ObjectDoesNotExist:
#         raise Http404("No encontrado", "El factura con id={} no existe.".format(id))

#     template = loader.get_template('GestionDeFacturas/ver.html')
#     contexto = {
#         'factura': factura,
#         'usuario': request.user
#     }
#     return HttpResponse(template.render(contexto, request))



#     '''if irAPagar:

#         return HttpResponseRedirect(reverse('pagos:pagoCrearConFactura', kwargs={'factura_id': factura.id}))'''




# def listar(request):
#     facturasQuery = Factura.objects.all()
#     facturasQuery = facturasQuery.filter(tools.paramsToFilter(request.GET, Factura))
#     template = loader.get_template('GestionDeFacturas/listar.html')

#     paginator = Paginator(facturasQuery, 3)
#     page = request.GET.get('page')

#     try:
#         facturas = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         facturas = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         facturas = paginator.page(paginator.num_pages)

#     contexto = {
#         'facturasQuery' : facturasQuery,
#         'usuario' : request.user,
#         'facturas': facturas,
#     }

#     return  HttpResponse(template.render(contexto, request))



################################################################################



# def verPractica(request, id):
#     factura = Factura.objects.get(id=id) if id is not None else None
#     practica = [{
#     "practica" : factura.practica,
#     "precio" : factura.practica.precio
#     #[TODO] agregar senia.
#     }]
#     return JsonResponse({'practica' : practica})


# class clienteAutocomplete(autocomplete.Select2QuerySetView):

#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !

#         qs = Cliente.objects.all()

#         if self.q:
#             qs = qs.filter(Q(apellidos__icontains=self.q) |Q(nombres__icontains=self.q) | Q(dniCuit__icontains=self.q))

#         return qs

# class productoAutocomplete(autocomplete.Select2QuerySetView):

#     def get_results(self, context):
#         """Return data for the 'results' key of the response."""
#         results = super().get_results(context)
#         for index, result in enumerate(context['object_list']):
#             results[index]["precio"] = result.precioPorUnidad
#         return results

#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#         qs = Producto.objects.all()

#         if self.q:
#            qs = qs.filter(Q(descripcion__icontains=self.q) | Q(nombre__icontains=self.q) | Q(marca__icontains=self.q))

#         return qs
