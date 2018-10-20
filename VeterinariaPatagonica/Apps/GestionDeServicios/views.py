from django.shortcuts import render
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from .models import Servicio
from .forms import *





def verHabilitados(request):
    servicio = Servicio.objects.filter(baja=False)
    template = loader.get_template('GestionDeServicios/verHabilitados.html')
    context = {
        'servicio' : servicio,
        'usuario' : request.user,
    }

    return  HttpResponse(template.render(context,request))

def verDeshabilitados(request):
    servicio = Servicio.objects.filter(baja=True)
    template = loader.get_template('GestionDeServicios/verDeshabilitados.html')
    context = {
        'servicio' : servicio,
        'usuario' : request.user,
    }
    return HttpResponse(template.render( context, request ))

def ver(request, id):
    #import ipdb; ipdb.set_trace()
    try:
        servicio = Servicio.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404( "No encontrado", "El servicio con id={} no existe.".format(id) )
    template = loader.get_template('GestionDeServicios/ver.html')
    context = {
        'servicio' : servicio,
        'usuario' : request.user
    }
    return HttpResponse(template.render( context, request ))

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeServicios.add_Servicio', raise_exception=True)
def crear(request, id = None):
    servicio = Servicio.objects.get(id=id) if id is not None else None
    ServicioForm = ServicioFormFactory(servicio)
    context = {'usuario': request.user}
    if request.method == 'POST':
        formulario = ServicioForm(request.POST, instance=servicio)
        if formulario.is_valid():
            servicio = formulario.save()
            return HttpResponseRedirect("/GestionDeServicios/ver/{}".format(servicio.id))
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = ServicioForm(instance=servicio)
    template = loader.get_template('GestionDeServicios/crear.html')
    return HttpResponse(template.render(context, request))

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeServicios.delete_Servicio', raise_exception=True)
def deshabilitar(request, id):

    try:
        servicio = Servicio.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    servicio.baja = True
    servicio.save()

    return HttpResponseRedirect( "/GestionDeServicios/ver/{}".format(servicio.id) )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeServicios.delete_Servicio', raise_exception=True)
def habilitar(request, id):

    try:
        servicio = Servicio.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    servicio.baja = False
    servicio.save()

    return HttpResponseRedirect( "/GestionDeServicios/ver/{}".format(servicio.id) )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeServicios.delete_Servicio', raise_exception=True)
def eliminar(request, id):

    try:
        servicio = Servicio.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    if request.method == 'POST':

        servicio.delete()
        return HttpResponseRedirect( "/GestionDeServicios/" )

    else:

        template = loader.get_template('GestionDeServicios/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }

        return HttpResponse( template.render( context, request) )
