from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from .models import Practica
from .forms import *

# Create your views here.
def verHabilitadas(request):
    practicas = Practica.objects.all()
    template = loader.get_template('GestionDePracticas/verHabilitadas.html')
    context = {
        'practicas' : practicas,
        'usuario' : request.user
    }
    return HttpResponse(template.render( context, request ))

@login_required(redirect_field_name='proxima')
@permission_required('GestionDePractica.add_Practica', raise_exception=True)
def crear(request, id = None):
    practica = Practica.objects.get(id=id) if id is not None else None
    PracticaForm = PracticaFormFactory(practica)
    context = {'usuario': request.user}
    if request.method == 'POST':
        formulario = PracticaForm(request.POST, instance=practica)
        if formulario.is_valid():
            practica = formulario.save()
            return HttpResponseRedirect("/GestionDePracticas/ver/{}".format(practica.id))
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = PracticaForm(instance=practica)
    template = loader.get_template('GestionDePracticas/crear.html')
    return HttpResponse(template.render(context, request))

def ver(request, id):
    #import ipdb; ipdb.set_trace()
    try:
        practica = Practica.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404( "No encontrado", "La práctica con id={} no existe.".format(id) )
    template = loader.get_template('GestionDePracticas/ver.html')
    context = {
        'practica' : practica,
        'usuario' : request.user
    }
    return HttpResponse(template.render( context, request ))
