from django.shortcuts import render
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import modelformset_factory

from .models import Servicio, ServicioProducto
from .forms import ServicioForm, ServicioProductoForm, ServicioProductoBaseFormSet
from VeterinariaPatagonica import tools

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeServicios.add_Servicio', raise_exception=True)
def modificar(request, id = None):
    servicio = Servicio.objects.get(id=id) if id is not None else None
    context = {'usuario': request.user}
    form = ServicioForm(instance=servicio)
    ServicioProductoFormset = modelformset_factory(ServicioProducto,#          Defino la forma del formset. Van a tener el checkbox eliminar, la cantidad mínima de forms en el formset
        fields=("producto", "cantidad"), min_num=1, extra=1, can_delete=True,# es de 1 y la máxima es la determinada por django (1000),
        formset=ServicioProductoBaseFormSet)#                                  además se define que siempre va a haber una tupla adicional (extra).
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        formset = ServicioProductoFormset(request.POST)
        if form.is_valid() and formset.is_valid():#Verifico si los forms del formset cumplen las restricciones definidas (Si no se lanzó un ValidationError).
            servicio = form.save()
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:#Bucle for que elimina los form que tienen tildado el checkbox "eliminar"
                obj.delete()
            for sproducto in instances:
                sproducto.servicio = servicio
                sproducto.save()
            #print(servicio, instances)
            return HttpResponseRedirect("/GestionDeServicios/ver/{}".format(servicio.id))
        context['formulario'] = form
        context["formset"] = formset
    else:
        context['formulario'] = form
        qs = ServicioProducto.objects.none() if servicio is None else servicio.servicio_productos.all()#Obtengo los productos ya cargados en el servicio, para poder mostrarlos en el formset.
        context["formset"] = ServicioProductoFormset(queryset=qs)
    template = loader.get_template('GestionDeServicios/formulario.html')
    return HttpResponse(template.render(context, request))


def verHabilitados(request):
    servicios = Servicio.objects.habilitados()
    servicios = servicios.filter(tools.paramsToFilter(request.GET, Servicio))
    template = loader.get_template('GestionDeServicios/verHabilitados.html')
    context = {
        'servicios' : servicios,
        'usuario' : request.user,
    }

    return  HttpResponse(template.render(context,request))

def verDeshabilitados(request):
    servicios = Servicio.objects.deshabilitados()
    servicios = servicios.filter(tools.paramsToFilter(request.GET, Servicio))
    template = loader.get_template('GestionDeServicios/verDeshabilitados.html')
    context = {
        'servicios' : servicios,
        'usuario' : request.user,
    }
    return  HttpResponse(template.render(context,request))

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
@permission_required('GestionDeServicios.delete_Servicio', raise_exception=True)
def deshabilitar(request, id):

    try:
        servicio = Servicio.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    servicio.baja = True
    servicio.save()

    return HttpResponseRedirect( "/GestionDeServicios/verDeshabilitados/")


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeServicios.delete_Servicio', raise_exception=True)
def habilitar(request, id):

    try:
        servicio = Servicio.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    servicio.baja = False
    servicio.save()

    return HttpResponseRedirect( "/GestionDeServicios/verHabilitados/")


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeServicios.delete_Servicio', raise_exception=True)
def eliminar(request, id):
    try:
        servicio = Servicio.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()
    if request.method == 'POST':
        servicio.delete()
        return HttpResponseRedirect( "/GestionDeServicios/verDeshabilitados" )
    else:
        template = loader.get_template('GestionDeServicios/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }
        return HttpResponse( template.render( context, request) )

#def volver(request, id):
#    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
