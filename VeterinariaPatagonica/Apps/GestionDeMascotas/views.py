from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
#from django.shortcuts import render_to_response

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django import forms

#from .models import Mascotas
from .forms import *




def mascota(request):
    context = {} #Defino un contexto
    template = loader.get_template('GestionDeMascotas/GestionDeMascotas.html')#Cargo el template desde la carpeta templates/GestionDeMascotas
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.

def alta(request):
    context = {}#Defino un contexto.
    template = loader.get_template('demos/altamascota.html')#Cargo el template desde la carpeta demos.
    #template = loader.get_template('demos/altamascota.html')#Cargo el template desde la carpeta demos.
    return HttpResponse(template.render(context,request))#Devuelvo la url con el template armado.

'''
def alta(request):
    return render_to_response('VeterinariaPatagonica/templates/demos/altamascota.html',request)
'''


def verHabilitados(peticion):

    mascota = Mascota.objects.filter(baja=False)

    template = loader.get_template('Mascota/verHabilitados.html')
    contexto = {
        'mascota' : mascota,
        'usuario' : peticion.user
    }

    return HttpResponse(template.render( contexto, peticion ))



def verDeshabilitados(peticion):
    mascota = Mascota.objects.filter(baja=True)

    template = loader.get_template('mascota/verDeshabilitados.html')
    contexto = {
        'mascota' : mascota,
        'usuario' : peticion.user
    }

    return HttpResponse(template.render( contexto, peticion ))



def ver(peticion, id):

    try:
        mascota = Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404( "No encontrado", "la mascota con id={} no existe.".format(id) )

    template = loader.get_template('GestionDeMascotas/ver.html')
    contexto = {
        'mascota' : mascota,
        'usuario' : peticion.user
    }

    return HttpResponse(template.render( contexto, peticion ))



@login_required(redirect_field_name='proxima')
@permission_required('GestionDeMascotas.add_Mascota', raise_exception=True)


def crear(peticion):

    contexto = {
        'usuario' : peticion.user
    }

    if peticion.method == 'POST':

        formulario = CreacionForm(peticion.POST)

        if formulario.is_valid():

            mascota = formulario.crear()

            return HttpResponseRedirect( "/GestionDeMascotas/ver/{}".format(mascota.id) )
        else:
            contexto['formulario'] = formulario

    else:

        contexto['formulario'] = CreacionForm()

    template = loader.get_template('GestionDeMascotas/crear.html')
    return HttpResponse(template.render( contexto, peticion) )



@login_required(redirect_field_name='proxima')
@permission_required('GestionDeMascotas.change_Mascota', raise_exception=True)


def modificar(peticion, id):

    try:
        mascota = Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    datos = {
        'nombre' : mascota.nombre,
        'raza' : mascota.raza,
        'especie': mascota.especie
    }

    if peticion.method == 'POST':

        formulario = ModificacionForm(peticion.POST, initial=datos)

        if formulario.is_valid():

            if formulario.has_changed():
                formulario.cargar(mascota).save()

            return HttpResponseRedirect("/GestionDeMascotas/ver/{}".format(mascota.id))

    else:

        formulario = ModificacionForm(datos, initial=datos)

    template = loader.get_template('GestionDeMascotas/modificar.html')
    contexto = {
        'formulario': formulario,
        'mascota': mascota,
        'usuario' : peticion.user
    }

    return HttpResponse(template.render( contexto, peticion) )



@login_required(redirect_field_name='proxima')
@permission_required('GestionDeMascotas.delete_Mascotas', raise_exception=True)

def deshabilitar(peticion, id):

    try:
        mascota = Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

        mascota.baja = True
        mascota.save()

    return HttpResponseRedirect( "/GestionDeMascotas/ver/{}".format(mascota.id) )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeMascotas.delete_Mascota', raise_exception=True)
def habilitar(peticion, id):

    try:
        mascota = Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

        mascota.baja = False
        mascota.save()

    return HttpResponseRedirect( "/GestionDeMascotas/ver/{}".format(mascota.id) )



@login_required(redirect_field_name='proxima')
@permission_required('GestionDeTiposDeAtencion.delete_TipoDeAtencion', raise_exception=True)

def eliminar(peticion, id):

    try:
        mascota = Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    if peticion.method == 'POST':

        mascota.delete()
        return HttpResponseRedirect( "/GestionDeMascotas/" )

    else:

        template = loader.get_template('GestionDeMascotas/eliminar.html')
        contexto = {
            'usuario' : peticion.user,
            'id' : id
        }

        return HttpResponse( template.render( contexto, peticion) )
