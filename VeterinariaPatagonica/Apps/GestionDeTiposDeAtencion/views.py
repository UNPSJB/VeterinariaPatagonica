#from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django import forms

from .models import TipoDeAtencion
from .forms import *



def ver_habilitados(peticion):

    tdas = TipoDeAtencion.objects.filter(baja=False)

    template = loader.get_template('GestionDeTiposDeAtencion/ver_habilitados.html')
    contexto = {
        'tdas' : tdas,
        'usuario' : peticion.user
    }

    return HttpResponse(template.render( contexto, peticion ))



def ver_deshabilitados(peticion):

    tdas = TipoDeAtencion.objects.filter(baja=True)

    template = loader.get_template('GestionDeTiposDeAtencion/ver_deshabilitados.html')
    contexto = {
        'tdas' : tdas,
        'usuario' : peticion.user
    }

    return HttpResponse(template.render( contexto, peticion ))



def ver(peticion, id):

    try:
        tda = TipoDeAtencion.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404( "No encontrado", "El tipo de atencion con id={} no existe.".format(id) )

    template = loader.get_template('GestionDeTiposDeAtencion/ver.html')
    contexto = {
        'tda' : tda,
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

            tda = formulario.crear()

            return HttpResponseRedirect( "/gestion/tda/ver/{}".format(tda.id) )
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
        tda = TipoDeAtencion.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    datos = {
        'nombre' : tda.nombre,
        'descripcion' : tda.descripcion,
        'emergencia' : tda.emergencia,
        'baja' : tda.baja,
        'recargo' : tda.recargo,
        'lugar' : tda.lugar,
        'tipo_de_servicio' : tda.tipo_de_servicio,
        'inicio_franja_horaria' : tda.inicio_franja_horaria,
        'fin_franja_horaria' : tda.fin_franja_horaria
    }

    if peticion.method == 'POST':

        formulario = ModificacionForm(peticion.POST, initial=datos)

        if formulario.is_valid():

            if formulario.has_changed():
                formulario.cargar(tda).save()

            return HttpResponseRedirect("/gestion/tda/ver/{}".format(tda.id))

    else:

        formulario = ModificacionForm(datos, initial=datos)

    template = loader.get_template('GestionDeTiposDeAtencion/modificar.html')
    contexto = {
        'formulario':formulario,
        'tda':tda,
        'usuario' : peticion.user
    }

    return HttpResponse(template.render( contexto, peticion) )



@login_required(redirect_field_name='proxima')
@permission_required('GestionDeTiposDeAtencion.delete_TipoDeAtencion', raise_exception=True)
def deshabilitar(peticion, id):

    try:
        tda = TipoDeAtencion.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    tda.baja = True
    tda.save()

    return HttpResponseRedirect( "/gestion/tda/ver/{}".format(tda.id) )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeTiposDeAtencion.delete_TipoDeAtencion', raise_exception=True)
def habilitar(peticion, id):

    try:
        tda = TipoDeAtencion.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    tda.baja = False
    tda.save()

    return HttpResponseRedirect( "/gestion/tda/ver/{}".format(tda.id) )



@login_required(redirect_field_name='proxima')
@permission_required('GestionDeTiposDeAtencion.delete_TipoDeAtencion', raise_exception=True)
def eliminar(peticion, id):

    try:
        tda = TipoDeAtencion.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    if peticion.method == 'POST':

        tda.delete()
        return HttpResponseRedirect( "/gestion/tda/" )

    else:

        template = loader.get_template('GestionDeTiposDeAtencion/eliminar.html')
        contexto = {
            'usuario' : peticion.user,
            'id' : id
        }

        return HttpResponse( template.render( contexto, peticion) )

