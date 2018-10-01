#from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django import forms

from .models import TipoDeAtencion
from .forms import *


def verHabilitados(peticion):

    tiposDeAtencion = TipoDeAtencion.objects.filter(baja=False)

    template = loader.get_template('GestionDeTiposDeAtencion/verHabilitados.html')
    contexto = {
        'tiposDeAtencion' : tiposDeAtencion,
        'usuario' : peticion.user
    }

    return HttpResponse(template.render( contexto, peticion ))



def verDeshabilitados(peticion):

    tiposDeAtencion = TipoDeAtencion.objects.filter(baja=True)

    template = loader.get_template('GestionDeTiposDeAtencion/verDeshabilitados.html')
    contexto = {
        'tiposDeAtencion' : tiposDeAtencion,
        'usuario' : peticion.user
    }

    return HttpResponse(template.render( contexto, peticion ))



def ver(peticion, id):

    try:
        tipoDeAtencion = TipoDeAtencion.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404( "No encontrado", "El tipo de atencion con id={} no existe.".format(id) )

    template = loader.get_template('GestionDeTiposDeAtencion/ver.html')
    contexto = {
        'tipoDeAtencion' : tipoDeAtencion,
        'usuario' : peticion.user
    }

    return HttpResponse(template.render( contexto, peticion ))



@login_required(redirect_field_name='proxima')
@permission_required('GestionDeTiposDeAtencion.add_TipoDeAtencion', raise_exception=True)
def crear(peticion):

    contexto = {
        'usuario' : peticion.user
    }

    if peticion.method == 'POST':

        formulario = CreacionForm(peticion.POST)

        if formulario.is_valid():

            tipoDeAtencion = formulario.crear()

            return HttpResponseRedirect( "/GestionDeTiposDeAtencion/ver/{}".format(tipoDeAtencion.id) )
        else:
            contexto['formulario'] = formulario

    else:

        contexto['formulario'] = CreacionForm()

    template = loader.get_template('GestionDeTiposDeAtencion/crear.html')
    return HttpResponse(template.render( contexto, peticion) )



@login_required(redirect_field_name='proxima')
@permission_required('GestionDeTiposDeAtencion.change_TipoDeAtencion', raise_exception=True)
def modificar(peticion, id):

    try:
        tipoDeAtencion = TipoDeAtencion.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    datos = {
        'nombre' : tipoDeAtencion.nombre,
        'descripcion' : tipoDeAtencion.descripcion,
        'emergencia' : tipoDeAtencion.emergencia,
        'baja' : tipoDeAtencion.baja,
        'recargo' : tipoDeAtencion.recargo,
        'lugar' : tipoDeAtencion.lugar,
        'tipo_de_servicio' : tipoDeAtencion.tipo_de_servicio,
        'inicio_franja_horaria' : tipoDeAtencion.inicio_franja_horaria,
        'fin_franja_horaria' : tipoDeAtencion.fin_franja_horaria
    }

    if peticion.method == 'POST':

        formulario = ModificacionForm(peticion.POST, initial=datos)

        if formulario.is_valid():

            if formulario.has_changed():
                formulario.cargar(tipoDeAtencion).save()

            return HttpResponseRedirect("/GestionDeTiposDeAtencion/ver/{}".format(tipoDeAtencion.id))

    else:

        formulario = ModificacionForm(datos, initial=datos)

    template = loader.get_template('GestionDeTiposDeAtencion/modificar.html')
    contexto = {
        'formulario':formulario,
        'tipoDeAtencion':tipoDeAtencion,
        'usuario' : peticion.user
    }

    return HttpResponse(template.render( contexto, peticion) )



@login_required(redirect_field_name='proxima')
@permission_required('GestionDeTiposDeAtencion.delete_TipoDeAtencion', raise_exception=True)
def deshabilitar(peticion, id):

    try:
        tipoDeAtencion = TipoDeAtencion.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    tipoDeAtencion.baja = True
    tipoDeAtencion.save()

    return HttpResponseRedirect( "/GestionDeTiposDeAtencion/ver/{}".format(tipoDeAtencion.id) )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeTiposDeAtencion.delete_TipoDeAtencion', raise_exception=True)
def habilitar(peticion, id):

    try:
        tipoDeAtencion = TipoDeAtencion.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    tipoDeAtencion.baja = False
    tipoDeAtencion.save()

    return HttpResponseRedirect( "/GestionDeTiposDeAtencion/ver/{}".format(tipoDeAtencion.id) )



@login_required(redirect_field_name='proxima')
@permission_required('GestionDeTiposDeAtencion.delete_TipoDeAtencion', raise_exception=True)
def eliminar(peticion, id):

    try:
        tipoDeAtencion = TipoDeAtencion.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    if peticion.method == 'POST':

        tipoDeAtencion.delete()
        return HttpResponseRedirect( "/GestionDeTiposDeAtencion/" )

    else:

        template = loader.get_template('GestionDeTiposDeAtencion/eliminar.html')
        contexto = {
            'usuario' : peticion.user,
            'id' : id
        }

        return HttpResponse( template.render( contexto, peticion) )
