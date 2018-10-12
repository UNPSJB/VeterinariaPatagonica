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





@login_required(redirect_field_name='proxima')
@permission_required('GestionDeMascotas.add_Mascota', raise_exception=True)
def crear(request):

    context = {'usuario' : request.user}

    if request.method == 'POST':

        formulario = MascotaForm(request.POST)

        if formulario.is_valid():
          mascota = formulario.save()
        else:
            context ['formulario '] = formulario

    else:
        context['formulario'] = MascotaForm()
    template = loader.get_template('GestionDeMAscotas/formulario.html')
    return HttpResponseRedirect( template.render(context, request) )

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeMascotas.change_Mascota', raise_exception=True)
def modificar(request, id):
    mascota = Mascota.objects.get(id=id)
    context = {'usuario': request.user}
    if request.method == 'POST':
        formulario = MascotaForm(request.POST, instance=mascota)
        if formulario.is_valid():
            mascota = formulario.save()
            return HttpResponseRedirect("/GestionDeMascotas/ver/{}".format(mascota.id))
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = MascotaForm(instance=mascota)
    template = loader.get_template('GestionDeMascotas/formulario.html')
    return HttpResponse(template.render(context, request))

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeClientes.delete_Cliente', raise_exception=True)
def habilitar(request, id):

    try:
        mascota= Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    mascota.baja = False
    mascota.save()

    return HttpResponseRedirect( "/GestionDeMascotas/ver/{}".format(mascota.id) )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeMascotas.delete_Mascotas', raise_exception=True)
def deshabilitar(request, id):

    try:
        mascota = Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

        mascota.baja = True
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

def ver(request, id):

    try:
        mascota = Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404("No encontrado", "La mascota con id={} no existe.".format(id))


    template = loader.get_template('GestionDeMascotas/ver.html')
    contexto = {
    'cliente': mascota,
    'usuario': request.user
    }

    return HttpResponse(template.render(contexto, request))

def verHabilitados(request):
    mascotas = Mascota.objects.filter(baja=False)
    template = loader.get_template('GestionDeMascotas/verHabilitados.html')
    contexto = {
        'mascotas': mascotas,
        'usuario': request.user,
    }
    return HttpResponse(template.render(contexto, request))

def verDeshabilitados(request):
    mascotas = Mascota.objects.filter(baja=True)
    template = loader.get_template('GestionDeMascotas/verDeshabilitados.html')
    contexto = {
        'mascotas': mascotas,
        'usuario': request.user,
    }

    return HttpResponse(template.render(contexto, request))
