# Create your views here.

from django.shortcuts import render
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from .models import Factura
from .forms import FacturaForm

from VeterinariaPatagonica import tools

from dal import autocomplete
from django.db.models import Q
from Apps.GestionDeClientes.models import Cliente

def facturas(request):

    context = {}#Defino el contexto.
    template = loader.get_template('GestionDeFacturas/GestionDeFacturas.html')#Cargo el template desde la carpeta templates/GestionDeFacturas.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeFacturas.add_Factura', raise_exception=True)
def modificar(request, id = None):

    factura = Factura.objects.get(id=id) if id is not None else None
    context = {'usuario': request.user}
    if request.method == 'POST':
        formulario = FacturaForm(request.POST, instance=factura)
        print(formulario)
        if formulario.is_valid():
            factura = formulario.save()
            return HttpResponseRedirect("/GestionDeFacturas/ver/{}".format(factura.id))
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = FacturaForm(instance=factura)
    template = loader.get_template('GestionDeFacturas/formulario.html')
    return HttpResponse(template.render(context, request))


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeFacturas.delete_Factura', raise_exception=True)
def habilitar(request, id):
    try:
        factura = Factura.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    factura.baja = False
    factura.save()

    return HttpResponseRedirect( "/GestionDeFacturas/verHabilitados/" )

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeFacturas.delete_Factura', raise_exception=True)
def deshabilitar(request, id):

    try:
        factura = Factura.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    factura.baja = True
    factura.save()

    return HttpResponseRedirect( "/GestionDeFacturas/verDeshabilitados/" )

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeFacturas.delete_Factura', raise_exception=True)
def eliminar(request, id):

    try:
        factura = Factura.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    if request.method == 'POST':

        factura.delete()
        return HttpResponseRedirect( "/GestionDeFacturas/" )

    else:

        template = loader.get_template('GestionDeFacturas/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }

        return HttpResponse( template.render( context, request) )

def ver(request, id):

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

def verHabilitados(request):
    facturas = Factura.objects.filter(baja=False)
    template = loader.get_template('GestionDeFacturas/verHabilitados.html')
    contexto = {
        'facturas': facturas,
        'usuario': request.user,
    }

    return  HttpResponse(template.render(contexto,request))

def verDeshabilitados(request):
    facturas = Factura.objects.filter(baja=True)
    template = loader.get_template('GestionDeFacturas/verDeshabilitados.html')
    contexto = {
        'facturas' : facturas,
        'usuario' : request.user,
    }

    return  HttpResponse(template.render(contexto,request))

class clienteAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = Cliente.objects.all()

        if self.q:
            qs = qs.filter(Q(apellidos__icontains=self.q) |Q(nombres__icontains=self.q) | Q(dniCuit__icontains=self.q))

        return qs