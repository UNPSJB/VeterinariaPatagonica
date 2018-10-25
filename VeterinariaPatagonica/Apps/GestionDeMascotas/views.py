from django.shortcuts import render
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from .models import Mascota
from .forms import MascotaFormFactory
from django.db.models import Q

def mascota(request):
    context = {}
    template = loader.get_template('GestionDeMascotas/GestionDeMascotas.html')
    return HttpResponse(template.render(context, request))

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeMascotas.add_Mascota', raise_exception=True)
def modificar(request, id= None):
    mascota = Mascota.objects.get(id=id) if id is not None else None
    MascotaForm = MascotaFormFactory(mascota)
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
@permission_required('GestionDeMascotas.delete_Mascota', raise_exception=True)
def habilitar(request, id):

    try:
        mascota= Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    mascota.baja = False
    mascota.save()

    return HttpResponseRedirect( "/GestionDeMascotas/verHabilitados/" )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeMascotas.delete_Mascotas', raise_exception=True)
def deshabilitar(request, id):
    try:
        mascota = Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    mascota.baja = True
    mascota.save()

    return HttpResponseRedirect( "/GestionDeMascotas/verDeshabilitados/" )

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeMascotas.delete_Mascota', raise_exception=True)
def eliminar(request, id):
    try:
        mascota = Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    if request.method == 'POST':

        mascota.delete()
        return HttpResponseRedirect( "/GestionDeMascotas/" )

    else:

        template = loader.get_template('GestionDeMascotas/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }
        return HttpResponse( template.render( context, request) )

def ver(request, id):

    try:
        mascotas = Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404("No encontrado", "La mascota con patente={} no existe.".format(id))


    template = loader.get_template('GestionDeMascotas/ver.html')
    contexto = {
    'mascota': mascotas,
    'usuario': request.user
    }
    return HttpResponse(template.render(contexto, request))

def paramsToFilter(params, Modelo):
    mapper = getattr(Modelo, "MAPPER", {})
    filters = Q()
    for item in params.items():
        key = item[0]
        value = item[1]
        if key in mapper and value:
            name = mapper[key]
            filters &= name(value) if callable(name) else Q(**{name: value})
    return filters

def verHabilitados(request):
    mascotas = Mascota.objects.habilitados()
    mascotas = mascotas.filter(paramsToFilter(request.GET, Mascota))
    template = loader.get_template('GestionDeMascotas/verHabilitados.html')
    contexto = {
        'mascotas': mascotas,
        'usuario': request.user,
    }
    return HttpResponse(template.render(contexto, request))

def verDeshabilitados(request):
    mascotas = Mascota.objects.deshabilitados()
    mascotas = mascotas.filter(paramsToFilter(request.GET, Mascota))

    template = loader.get_template('GestionDeMascotas/verDeshabilitados.html')
    contexto = {
        'mascotas': mascotas,
        'usuario': request.user,
    }
    return HttpResponse(template.render(contexto, request))



def busqueda(request):
    '''
    mascotas = Mascota.objects.filter(nombre=nombre)
    template = loader.get_template('GestionDeMascotas/verDeshabilitados.html')
    contexto = {
        'mascotas': mascotas,
        'usuario': request.user,
    }
    return HttpResponse(template.render(contexto, request))

    '''
    mascotas = request.GET.get('mascota', '')
    mascotas = Mascota.objects.filter(nombre=mascota)
    return render(request, 'template_busqueda.html', {'mascotas': mascotas})


'''from django.db.models import Q
def busqueda(self):
   q = request.GET.get('q', '')

   querys = (Q(ciudad__nombre__icontains=q) | Q(ciudad__departamento__nombre__icontains=q))
   querys |= Q(nombre__icontains=q)

   eventos = Evento.objects.filter(querys)
   return render(request, 'template_busqueda.html', {'eventos': eventos}) '''