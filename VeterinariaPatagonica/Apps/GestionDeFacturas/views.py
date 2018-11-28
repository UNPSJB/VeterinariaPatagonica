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
    facturas = Factura.objects.all()
    facturas = facturas.filter(tools.paramsToFilter(request.GET, Factura))
    template = loader.get_template('GestionDeFacturas/listar.html')
    contexto = {
        'facturas' : facturas,
        'usuario' : request.user,
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
