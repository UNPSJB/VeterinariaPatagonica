# Create your views here.

from django.shortcuts import render
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from .models import Rubro
#from .forms import ClienteFormFactory


def rubros(request):

    pass

    
@login_required(redirect_field_name='proxima')
@permission_required('GestionDeRubros.add_Rubro', raise_exception=True)
def modificar(request, id = None):

    pass


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeRubros.delete_Rubro', raise_exception=True)
def habilitar(request, id):
    try:
        rubro = Rubro.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    rubro.baja = False
    rubro.save()

    return HttpResponseRedirect( "/GestionDeRubros/verHabilitados/" )

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeRubros.delete_Rubro', raise_exception=True)
def deshabilitar(request, id):

    try:
        rubro = Rubro.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    rubro.baja = True
    rubro.save()

    return HttpResponseRedirect( "/GestionDeRubros/verDeshabilitados/" )

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeRubros.delete_Rubro', raise_exception=True)
def eliminar(request, id):

    try:
        rubro = Rubro.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    if request.method == 'POST':

        rubro.delete()
        return HttpResponseRedirect( "/GestionDeRubros/" )

    else:

        template = loader.get_template('GestionDeRubros/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }

        return HttpResponse( template.render( context, request) )

def ver(request, id):

    try:
        rubro = Rubro.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404("No encontrado", "El rubro con id={} no existe.".format(id))

    template = loader.get_template('GestionDeRubros/ver.html')
    contexto = {
        'rubro': rubro,
        'usuario': request.user
    }

    return HttpResponse(template.render(contexto, request))

def verHabilitados(request):
    rubros = Rubro.objects.filter(baja=False)
    template = loader.get_template('GestionDeRubros/verHabilitados.html')
    contexto = {
        'rubros' : rubros,
        'usuario' : request.user,
    }

    return  HttpResponse(template.render(contexto,request))

def verDeshabilitados(request):
    rubros = Rubro.objects.filter(baja=True)
    template = loader.get_template('GestionDeRubros/verDeshabilitados.html')
    contexto = {
        'rubros' : rubros,
        'usuario' : request.user,
    }

    return  HttpResponse(template.render(contexto,request))