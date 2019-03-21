# Create your views here.

from django.shortcuts import render
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from .models import Rubro
from .forms import RubroForm
from VeterinariaPatagonica import tools
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def rubros(request):

    context = {}#Defino el contexto.
    template = loader.get_template('GestionDeRubros/GestionDeRubros.html')#Cargo el template desde la carpeta templates/GestionDeRubros.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeRubros.add_Rubro', raise_exception=True)
def modificar(request, id = None):

    rubro = Rubro.objects.get(id=id) if id is not None else None
    if (id==None):
        context = {"titulo": 1, 'usuario': request.user}
    else:
        context = {"titulo": 2, 'usuario': request.user}
    if request.method == 'POST':
        formulario = RubroForm(request.POST, instance=rubro)
        print(formulario)
        if formulario.is_valid():
            rubro = formulario.save()
            return HttpResponseRedirect("/GestionDeRubros/ver/{}".format(rubro.id))
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = RubroForm(instance=rubro)
    template = loader.get_template('GestionDeRubros/formulario.html')
    return HttpResponse(template.render(context, request))


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
        return HttpResponseRedirect( "/GestionDeRubros/verDeshabilitados/" )
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
    rubrosQuery = Rubro.objects.habilitados()
    rubrosQuery = rubrosQuery.filter(tools.paramsToFilter(request.GET, Rubro))
    template = loader.get_template('GestionDeRubros/verHabilitados.html')

    paginator = Paginator(rubrosQuery, 3)
    page = request.GET.get('page')

    try:
        rubros = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        rubros = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        rubros = paginator.page(paginator.num_pages)

    contexto = {
        'rubrosQuery' : rubrosQuery,
        'usuario' : request.user,
        'rubros': rubros,
    }

    return  HttpResponse(template.render(contexto,request))


def verDeshabilitados(request):
    rubrosQuery = Rubro.objects.deshabilitados()
    rubrosQuery = rubrosQuery.filter(tools.paramsToFilter(request.GET, Rubro))
    template = loader.get_template('GestionDeRubros/verDeshabilitados.html')

    paginator = Paginator(rubrosQuery, 3)
    page = request.GET.get('page')

    try:
        rubros = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        rubros = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        rubros = paginator.page(paginator.num_pages)

    contexto = {
        'rubrosQuery': rubrosQuery,
        'usuario': request.user,
        'rubros': rubros,
    }

    return  HttpResponse(template.render(contexto,request))
