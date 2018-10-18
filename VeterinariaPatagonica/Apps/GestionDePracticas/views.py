from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from .models import Practica
from .forms import *

# Create your views here.
def verCirugiasHabilitadas(request):
    cirugias = Practica.objects.all()
    template = loader.get_template('GestionDePracticas/verCirugiasHabilitadas.html')
    context = {
        'cirugias' : cirugias,
        'usuario' : request.user
    }
    return HttpResponse(template.render( context, request ))

def verConsultasHabilitadas(request):
    consultas = Practica.objects.all()
    template = loader.get_template('GestionDePracticas/verConsultasHabilitadas.html')
    context = {
        'consultas' : consultas,
        'usuario' : request.user
    }
    return HttpResponse(template.render( context, request ))

@login_required(redirect_field_name='proxima')
@permission_required('GestionDePractica.add_Practica', raise_exception=True)
def crearCirugia(request, id = None):
    cirugia = Practica.objects.get(id=id) if id is not None else None
    PracticaForm = PracticaFormFactory(cirugia)
    context = {'usuario': request.user}
    if request.method == 'POST':
        formulario = PracticaForm(request.POST, instance=cirugia)
        if formulario.is_valid():
            cirugia = formulario.save()
            return HttpResponseRedirect("/GestionDePracticas/ver/{}".format(cirugia.id))
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = PracticaForm(instance=cirugia)
    template = loader.get_template('GestionDePracticas/crearCirugia.html')
    return HttpResponse(template.render(context, request))

@login_required(redirect_field_name='proxima')
@permission_required('GestionDePractica.add_Practica', raise_exception=True)
def crearConsulta(request, id = None):
    consulta = Practica.objects.get(id=id) if id is not None else None
    PracticaForm = PracticaFormFactory(consulta)
    context = {'usuario': request.user}
    if request.method == 'POST':
        formulario = PracticaForm(request.POST, instance=consulta)
        if formulario.is_valid():
            consulta = formulario.save()
            return HttpResponseRedirect("/GestionDePracticas/ver/{}".format(consulta.id))
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = PracticaForm(instance=consulta)
    template = loader.get_template('GestionDePracticas/crearConsulta.html')
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