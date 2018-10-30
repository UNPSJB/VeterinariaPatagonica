# Create your views here.

from django.shortcuts import render
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from .models import FormaDePago
from .forms import FormaDePagoForm
from VeterinariaPatagonica import tools

def formasDePagos(request):

    context = {}#Defino el contexto.
    template = loader.get_template('GestionDeFormasDePagos/GestionDeFormasDePagos.html')#Cargo el template desde la carpeta templates/GestionDeFormasDePagos.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeFormasDePagos.add_FormaDePago', raise_exception=True)
def modificar(request, id = None):

    formaDePago = FormaDePago.objects.get(id=id) if id is not None else None
    context = {'usuario': request.user}
    if request.method == 'POST':
        formulario = FormaDePagoForm(request.POST, instance=formaDePago)
        print(formulario)
        if formulario.is_valid():
            formaDePago = formulario.save()
            return HttpResponseRedirect("/GestionDeFormasDePagos/ver/{}".format(formaDePago.id))
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = FormaDePagoForm(instance=formaDePago)
    template = loader.get_template('GestionDeFormasDePagos/formulario.html')
    return HttpResponse(template.render(context, request))


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeFormasDePagos.delete_FormasDePago', raise_exception=True)
def habilitar(request, id):
    try:
        formaDePago = FormaDePago.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    formaDePago.baja = False
    formaDePago.save()

    return HttpResponseRedirect( "/GestionDeFormasDePagos/verHabilitados/" )

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeFormasDePagos.delete_FormasDePago', raise_exception=True)
def deshabilitar(request, id):

    try:
        formaDePago = FormaDePago.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    formaDePago.baja = True
    formaDePago.save()

    return HttpResponseRedirect( "/GestionDeFormasDePagos/verDeshabilitados/" )

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeFormasDePagos.delete_FormasDePago', raise_exception=True)
def eliminar(request, id):
    try:
        formaDePago = FormaDePago.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()
    if request.method == 'POST':
        formaDePago.delete()
        return HttpResponseRedirect( "/GestionDeFormasDePagos/" )
    else:
        template = loader.get_template('GestionDeFormasDePagos/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }
        return HttpResponse( template.render( context, request) )

def ver(request, id):

    try:
        formaDePago = FormaDePago.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404("No encontrado", "El formaDePago con id={} no existe.".format(id))

    template = loader.get_template('GestionDeFormasDePagos/ver.html')
    contexto = {
        'formaDePago': formaDePago,
        'usuario': request.user
    }

    return HttpResponse(template.render(contexto, request))

def verHabilitados(request):
    formasDePagos = FormaDePago.objects.filter(baja=False)
    template = loader.get_template('GestionDeFormasDePagos/verHabilitados.html')
    contexto = {
        'formasDePagos' : formasDePagos,
        'usuario' : request.user,
    }

    return  HttpResponse(template.render(contexto,request))


def verDeshabilitados(request):
    formasDePagos = FormaDePago.objects.deshabilitados()
    formasDePagos = formasDePagos.filter(tools.paramsToFilter(request.GET, FormaDePago))
    template = loader.get_template('GestionDeFormasDePagos/verDeshabilitados.html')
    contexto = {
        'formasDePagos' : formasDePagos,
        'usuario' : request.user,
    }

    return  HttpResponse(template.render(contexto,request))


'''
def verDeshabilitados(request):
    formasDePagos = FormaDePago.objects.filter(baja=True)
    template = loader.get_template('GestionDeFormasDePagos/verDeshabilitados.html')
    contexto = {
        'formasDePagos' : formasDePagos,
        'usuario' : request.user,
    }

    return  HttpResponse(template.render(contexto,request))
'''
