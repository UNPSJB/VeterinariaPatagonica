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
        formset=DetalleFacturaBaseFormSet)
    if request.method == 'POST':
        form = FacturaForm(request.POST, instance=factura)
        formset = DetalleFacturaFormset(request.POST)
        if form.is_valid() and formset.is_valid():
            factura = form.save(commit=False)
            instances = formset.save(commit=False)
            factura.calcular_subtotales(instances)

            print(factura, instances)
        context['formulario'] = form
        context['formset'] = formset
    else:
        context['formulario'] = form
        qs = DetalleFactura.objects.none() if factura is None else factura.detalleFactura.all()
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

