# Create your views here.

from django.shortcuts import render
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from .models import Factura
from .forms import FacturaForm, DetalleFacturaBaseFormSet, DetalleFactura, DetalleFacturaForm, FacturaFormFactory
from django.forms import modelformset_factory
from VeterinariaPatagonica import tools
from dal import autocomplete
from django.db.models import Q
from Apps.GestionDeClientes.models import Cliente
from Apps.GestionDePracticas.models import Practica
from Apps.GestionDeProductos.models import Producto
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from VeterinariaPatagonica.errores import VeterinariaPatagonicaError
from .forms import FacturarPracticaForm, FacturaProductoFormSet

from VeterinariaPatagonica.tools import GestorListadoQueryset



def facturas(request):

    context = {}#Defino el contexto.
    template = loader.get_template('GestionDeFacturas/GestionDeFacturas.html')#Cargo el template desde la carpeta templates/GestionDeFacturas.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeFacturas.add_Factura', raise_exception=True)
def modificar(request, id = None):
    factura = Factura.objects.get(id=id) if id is not None else None
    context = {'usuario': request.user}
    form = FacturaForm(instance=factura)
    DetalleFacturaFormset = modelformset_factory(
        DetalleFactura,
        DetalleFacturaForm,
        min_num=1,
        extra=0,
        can_delete=True,
        formset=DetalleFacturaBaseFormSet)
    if request.method == 'POST':
        form = FacturaForm(request.POST, instance=factura)
        formset = DetalleFacturaFormset(request.POST)
        if form.is_valid() and formset.is_valid():
            factura = form.save()
            instances = formset.save(commit=False)
            factura.calcular_subtotales(instances)
            factura.precioTotal(instances)
            for obj in formset.deleted_objects:#Bucle for que elimina los form que tienen tildado el checkbox "eliminar"
                obj.delete()
            for detalle in instances:
                detalle.factura = factura
                detalle.save()
            if factura.practica :
                if factura.practica.esPosible(Practica.Acciones.facturar):#Transiciona la practica seleccionada a facturada.
                    factura.practica.hacer("facturar")
            #[TODO] HACER QUE LA PRACTICA ELEGIDA DEJE DE FIGURAR.
            # factura.practica.
            return HttpResponseRedirect("/GestionDeFacturas/ver/{}".format(factura.id))
            print(factura, instances)
        context['formulario'] = form
        context['formset'] = formset
    else:
        context['formulario'] = form
        qs = DetalleFactura.objects.none() if factura is None else factura.detalleFactura.all()#si ponemos "productos" no pincha. pero el modificar no muestra los items previamente agregados.
        context["formset"] = DetalleFacturaFormset(queryset=qs)
    template = loader.get_template('GestionDeFacturas/formulario.html')
    return HttpResponse(template.render(context, request))

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeFacturas.add_Factura', raise_exception=True)
def crearFacturaPractica(request, id):
    practica = Practica.objects.get(id=id)
    context = {'usuario': request.user}
    Form = FacturaFormFactory(instance=practica)
    DetalleFacturaFormset = modelformset_factory(
        DetalleFactura,
        fields=("producto", "cantidad"), min_num=1,
        formset=DetalleFacturaBaseFormSet)
    if request.method == 'POST':
        pass
    context["practica"] = practica
    context["form"] = Form(initial={})
    context['formset'] = DetalleFacturaFormset(initial=practica.practicaproducto_set.values())
    template = loader.get_template('GestionDeFacturas/formulario.html')
    return HttpResponse(template.render(context, request))


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeFacturas.delete_Factura', raise_exception=True)
def eliminar(request, id):
    try:
        factura = Factura.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()
    if request.method == 'POST':
        factura.delete()
        return HttpResponseRedirect( "/GestionDeFacturas/listar" )
    else:
        template = loader.get_template('GestionDeFacturas/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }
        return HttpResponse( template.render( context, request) )

def ver(request, id):  #, irAPagar=1
#[TODO] ACA PINCHA. no arma el render.
#    import ipdb
#    ipdb.set_trace()
    try:
        factura = Factura.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404("No encontrado", "El factura con id={} no existe.".format(id))

    template = loader.get_template('GestionDeFacturas/ver.html')
    contexto = {
        'factura': factura,
        'usuario': request.user
    }
    return HttpResponse(template.render(contexto, request))



    '''if irAPagar:
        print("Quiere ir a crear pago")
        return HttpResponseRedirect(reverse('pagos:pagoCrearConFactura', kwargs={'factura_id': factura.id}))'''




def listar(request):

    gestor = GestorListadoQueryset(
        orden=[
            ["orden_tipo", "Tipo"],
            ["orden_cliente", "Cliente"],
            ["orden_fecha", "Fecha"],
            ["orden_total", "Total"],
            ["orden_recargo", "Recargo"],
            ["orden_descuento", "Descuento"],
        ]
    )
    facturasQuery = Factura.objects.all()
    facturasQuery = facturasQuery.filter(tools.paramsToFilter(request.GET, Factura))

    gestor.cargar(request, facturasQuery)
    # gestor.ordenar()//[TODO] ARREGLAR.

    template = loader.get_template('GestionDeFacturas/listar.html')

    paginator = Paginator(facturasQuery, 3)
    page = request.GET.get('page')

    try:
        facturas = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        facturas = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        facturas = paginator.page(paginator.num_pages)

    contexto = {
        'facturasQuery' : facturasQuery,
        'usuario' : request.user,
        'facturas': facturas,
        'gestor' : gestor,
    }

    return  HttpResponse(template.render(contexto, request))

def verPractica(request, id):
    factura = Factura.objects.get(id=id) if id is not None else None
    practica = [{
    "practica" : factura.practica,
    "precio" : factura.practica.precio
    #[TODO] agregar senia.
    }]
    return JsonResponse({'practica' : practica})


class clienteAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = Cliente.objects.all()

        if self.q:
            qs = qs.filter(Q(apellidos__icontains=self.q) |Q(nombres__icontains=self.q) | Q(dniCuit__icontains=self.q))

        return qs

class productoAutocomplete(autocomplete.Select2QuerySetView):

    def get_results(self, context):
        """Return data for the 'results' key of the response."""
        results = super().get_results(context)
        for index, result in enumerate(context['object_list']):
            results[index]["precio"] = result.precioPorUnidad
        return results

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        qs = Producto.objects.all()

        if self.q:
           qs = qs.filter(Q(descripcion__icontains=self.q) | Q(nombre__icontains=self.q) | Q(marca__icontains=self.q))

        return qs


def crearDetalles(datos):

    detalles = []
    for dato in datos:
        cantidad = dato["cantidad"]
        producto = dato["producto"]
        if cantidad and producto:
            detalles.append(DetalleFactura(
                producto = producto,
                cantidad = cantidad,
                subtotal = producto.precioPorUnidad * cantidad
            ))

    return detalles



def buscarPractica(id):

    practica = Practica.objects.get(id=id)

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

    factura = Factura(
        cliente=practica.cliente,
        fecha=timezone.now(),
        total=practica.estados.realizacion().total(),
        practica=practica,
        recargo=Decimal(0),
        descuento=Decimal(0),
    )

    return practica, factura



@login_required(redirect_field_name='proxima')
@permission_required('GestionDeFacturas.add_Factura', raise_exception=True)
def facturarPractica(request, id):

    practica, factura = buscarPractica(id)
    context = { "practica" : practica, "factura" : factura }

    if request.method == "POST":
        form = FacturarPracticaForm(request.POST, instance=factura)
        formset = FacturaProductoFormSet(request.POST, prefix="producto")

        if form.is_valid() and formset.is_valid():
            factura = form.save(commit=False)
            detalles = crearDetalles(formset.completos)

            with transaction.atomic():
                factura.save()
                factura.detalles_producto.set(detalles, bulk=False)
                practica.hacer(Practica.Acciones.facturar.name)

            return HttpResponseRedirect(
                reverse("facturas:facturaVer", args=(factura.id,))
            )

    else:
        form = FacturarPracticaForm(instance=factura)
        formset = FacturaProductoFormSet(prefix="producto")

    context["form"]     = form
    context['formset']  = formset
    context["practica"] = practica
    context["accion"]   = "Guardar"

    template = loader.get_template('GestionDeFacturas/facturarPractica.html')
    return HttpResponse(template.render(context, request))
