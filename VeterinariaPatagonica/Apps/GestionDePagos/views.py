from django.shortcuts import render
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from .models import Pago
#from .forms import PagoFormFactory
from .forms import PagoForm
from Apps.GestionDeFacturas.models import Factura
from VeterinariaPatagonica import tools
from django.utils import timezone

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def pago(request):

    context = {}#Defino el contexto.
    template = loader.get_template('GestionDePagos/GestionDePagos.html')#Cargo el template desde la carpeta templates/GestionDePagos.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.


@login_required(redirect_field_name='proxima')
@permission_required('GestionDePagos.add_Pago', raise_exception=True)
def crear(request, idFactura = None): #, factura_id=None

    factura = Factura.objects.get(id=idFactura)
    context = {'usuario': request.user}

    pagos= len(Pago.objects.filter(factura=idFactura))

    if not pagos:

        pago=Pago(importeTotal=factura.total, factura=factura)
        if request.method == 'POST':
            formulario = PagoForm(request.POST, instance=pago)
            if formulario.is_valid():
                pago = formulario.save()
                return HttpResponseRedirect("/GestionDePagos/ver/{}".format(pago.id))
            else:
                context['formulario'] = formulario
        else:
            context['formulario'] = PagoForm(instance=pago)
    else:
        print("Error, ya hay Pagos")
    template = loader.get_template('GestionDePagos/formulario.html')
    return HttpResponse(template.render(context, request))

    '''factura = None
    if factura_id:
        factura = Factura.objects.get(pk=factura_id)
    PagoForm = PagoFormFactory(pago, factura)'''





@login_required(redirect_field_name='proxima')
@permission_required('GestionDePagos.delete_Pago', raise_exception=True)
def eliminar(request, id):

    try:
        pago = Pago.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    if request.method == 'POST':

        pago.delete()
        return HttpResponseRedirect( "/GestionDePagos/" )

    else:

        template = loader.get_template('GestionDePagos/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }

        return HttpResponse( template.render( context, request) )

def ver(request, id):

    try:
        pago = Pago.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404("No encontrado", "El pago con id={} no existe.".format(id))

    template = loader.get_template('GestionDePagos/ver.html')
    contexto = {
        'pago': pago,
        'usuario': request.user
    }

    return HttpResponse(template.render(contexto, request))

def listar(request):
    pagosQuery = Pago.objects.all()
    pagos = pagosQuery.filter(tools.paramsToFilter(request.GET, Pago))
    template = loader.get_template('GestionDePagos/listar.html')


    paginator = Paginator(pagosQuery, 1)
    page = request.GET.get('page')

    try:
        pagos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pagos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pagos = paginator.page(paginator.num_pages)

    contexto = {
        'pagosQuery' : pagosQuery,
        'usuario' : request.user,
        'pagos': pagos,
    }
    return HttpResponse(template.render(contexto, request))
