from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django import forms

from .models import Insumo
from .forms import *


def insumos(request):
    context = {}#Defino un contexto.
    template = loader.get_template('GestionDeInsumos/GestionDeInsumos.html')#Cargo el template desde la carpeta templates/GestionDeInsumos.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.

def verHabilitados(request):
    insumos = Insumo.objects.filter(baja=False)
    template = loader.get_template('GestionDeInsumos/verHabilitados.html')
    context = {
        'insumos' : insumos,
        'usuario' : request.user
    }
    return HttpResponse(template.render( context, request ))

def verDeshabilitados(request):
    insumos = Insumo.objects.filter(baja=True)
    template = loader.get_template('GestionDeInsumos/verDeshabilitados.html')
    context = {
        'insumos' : insumos,
        'usuario' : request.user
    }
    return HttpResponse(template.render( context, request ))

def ver(request, id):
    try:
        insumo = Insumo.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404( "No encontrado", "El insumo con id={} no existe.".format(id) )
    template = loader.get_template('GestionDeInsumos/ver.html')
    context = {
        'insumo' : insumo,
        'usuario' : request.user
    }
    return HttpResponse(template.render( context, request ))

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeInsumos.add_Insumo', raise_exception=True)
def crear(request):
    context = {'usuario' : request.user}
    if request.method == 'POST':
        formulario = CreacionForm(request.POST)
        if formulario.is_valid():
            insumo = formulario.crear()
            return HttpResponseRedirect("/GestionDeInsumos/ver/{}".format(insumo.nombre) )
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = CreacionForm()
    template = loader.get_template('GestionDeInsumos/crear.html')
    return HttpResponse(template.render( context, request) )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeInsumos.change_Insumo', raise_exception=True)
def modificar(request, id):

    try:
        insumo = Insumo.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    datos = {
        'nombre' : insumo.nombre,
        'formaDePresentacion' : insumo.formaDePresentacion,
        'precioPorUnidad' : insumo.precioPorUnidad,
        'rubro' : insumo.rubro,
        'baja' : insumo.baja
    }

    if request.method == 'POST':

        formulario = ModificacionForm(request.POST, initial=datos)

        if formulario.is_valid():

            if formulario.has_changed():
                formulario.cargar(insumo).save()

            return HttpResponseRedirect("/GestionDeInsumos/ver/{}".format(insumo.id))

    else:

        formulario = ModificacionForm(datos, initial=datos)

    template = loader.get_template('GestionDeInsumos/modificar.html')
    context = {
        'formulario':formulario,
        'insumo':insumo,
        'usuario' : request.user
    }

    return HttpResponse(template.render( context, request) )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeInsumos.delete_Insumo', raise_exception=True)
def deshabilitar(request, id):

    try:
        insumo = Insumo.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    insumo.baja = True
    insumo.save()

    return HttpResponseRedirect( "GestionDeInsumos/ver/{}".format(insumo.id) )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeInsumos.delete_Insumo', raise_exception=True)
def habilitar(request, id):

    try:
        insumo = Insumo.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    insumo.baja = False
    insumo.save()

    return HttpResponseRedirect( "/GestionDeInsumos/ver/{}".format(insumo.id) )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeInsumos.delete_Insumo', raise_exception=True)
def eliminar(request, id):

    try:
        insumo = Insumo.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    if request.method == 'POST':

        insumo.delete()
        return HttpResponseRedirect( "/GestionDeInsumos/" )

    else:

        template = loader.get_template('GestionDeInsumos/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }

        return HttpResponse( template.render( context, request) )





















'''
def insumos(request):
    context = {}#Defino un contexto.
    template = loader.get_template('GestionDeInsumos/GestionDeInsumos.html')#Cargo el template desde la carpeta templates/GestionDeInsumos.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.
'''

'''
def alta(request):
    context = {}#Defino un contexto.
    template = loader.get_template('demos/altainsumo.html')#Cargo el template desde la carpeta demos.
    #template = loader.get_template('demos/altainsumo.html')#Cargo el template desde la carpeta demos.
    return HttpResponse(template.render(context,request))#Devuelvo la url con el template armado.
'''
