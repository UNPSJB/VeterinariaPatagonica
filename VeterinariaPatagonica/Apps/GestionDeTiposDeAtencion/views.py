from django.template import loader, RequestContext
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django import forms

from .models import TipoDeAtencion
from .forms import TipoDeAtencionForm



# Alguien sabe como abstraerse de la ubicacion de los
# templates como hacemos con los namespaces de las views?
PLANTILLAS = {
    'habilitados' :          'habilitados',
    'deshabilitados' :    'deshabilitados',
    'ver' :                        'ver',
    'crear' :                    'crear',
    'modificar' :             'modificar',
    'eliminar' :                'eliminar'
}

def plantilla(nombre):
    return 'GestionDeTiposDeAtencion/'+PLANTILLAS[nombre]+'.html'



def habilitados(peticion):
    """ Listado de tipos de atencion habilitados """

    tiposDeAtencion = TipoDeAtencion.objects.habilitados()

    template = loader.get_template( plantilla('habilitados') )

    contexto = {
        'tiposDeAtencion' : tiposDeAtencion
    }

    return HttpResponse(template.render( contexto, peticion ))



def deshabilitados(peticion):
    """ Listado de tipos de atencion deshabilitados """

    tiposDeAtencion = TipoDeAtencion.objects.deshabilitados()

    template = loader.get_template(plantilla('deshabilitados'))

    contexto = {
        'tiposDeAtencion' : tiposDeAtencion
    }

    return HttpResponse(template.render( contexto, peticion ))



def ver(peticion, id):
    """ Ver tipo de atencion segun <id> """

    try:
        tipoDeAtencion = TipoDeAtencion.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404( "Tipo de atencion no encontrado" )

    template = loader.get_template(plantilla('ver'))
    contexto = {
        'tipoDeAtencion' : tipoDeAtencion
    }

    return HttpResponse(template.render( contexto, peticion ))



@login_required(redirect_field_name='proxima')
@permission_required('GestionDeTiposDeAtencion.add_TipoDeAtencion', raise_exception=True)
def crear(peticion):
    """ Dar de alta un nuevo tipo de atencion """

    contexto = {}

    if peticion.method == 'POST':

        tipoDeAtencion = TipoDeAtencion()
        formulario = TipoDeAtencionForm(peticion.POST, instance=tipoDeAtencion)

        if formulario.is_valid():

            tipoDeAtencion = formulario.save()

            return HttpResponseRedirect( reverse("tiposDeAtencion:ver", args=(tipoDeAtencion.id,)) )
        else:
            contexto['formulario'] = formulario

    else:

        contexto['formulario'] = TipoDeAtencionForm()

    template = loader.get_template(plantilla('crear'))
    return HttpResponse(template.render( contexto, peticion) )



@login_required(redirect_field_name='proxima')
@permission_required('GestionDeTiposDeAtencion.change_TipoDeAtencion', raise_exception=True)
def modificar(peticion, id):
    """ Modificar tipo de atencion con clave primaria <id> """

    try:
        tipoDeAtencion = TipoDeAtencion.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404("Tipo de atencion no encontrado")

    if peticion.method == 'POST':

        formulario = TipoDeAtencionForm(peticion.POST, instance=tipoDeAtencion)

        if formulario.is_valid():

            if formulario.has_changed():
                formulario.save()

            return HttpResponseRedirect( reverse("tiposDeAtencion:ver", args=(tipoDeAtencion.id,)) )

    else:

        formulario = TipoDeAtencionForm(instance=tipoDeAtencion)

    template = loader.get_template(plantilla('modificar'))
    contexto = {
        'formulario':formulario,
        'tipoDeAtencion':tipoDeAtencion
    }

    return HttpResponse(template.render( contexto, peticion) )



@login_required(redirect_field_name='proxima')
@permission_required('GestionDeTiposDeAtencion.delete_TipoDeAtencion', raise_exception=True)
def deshabilitar(peticion, id):
    """ Deshablitar el tipo de atencion con clave primaria <id> """

    try:
        tipoDeAtencion = TipoDeAtencion.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404("Tipo de atencion no encontrado")

    tipoDeAtencion.baja = True
    tipoDeAtencion.save()

    return HttpResponseRedirect( reverse("tiposDeAtencion:ver", args=(tipoDeAtencion.id,)) )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeTiposDeAtencion.delete_TipoDeAtencion', raise_exception=True)
def habilitar(peticion, id):
    """ Hablitar el tipo de atencion con clave primaria <id> """

    try:
        tipoDeAtencion = TipoDeAtencion.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404("Tipo de atencion no encontrado")

    tipoDeAtencion.baja = False
    tipoDeAtencion.save()

    return HttpResponseRedirect( reverse("tiposDeAtencion:ver", args=(tipoDeAtencion.id,)) )



@login_required(redirect_field_name='proxima')
@permission_required('GestionDeTiposDeAtencion.delete_TipoDeAtencion', raise_exception=True)
def eliminar(peticion, id):
    """ Eliminar el tipo de atencion con clave primaria <id> """

    try:
        tipoDeAtencion = TipoDeAtencion.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404("Tipo de atencion no encontrado")

    if peticion.method == 'POST':

        tipoDeAtencion.delete()
        return HttpResponseRedirect( reverse("tiposDeAtencion:deshabilitados") )

    else:

        template = loader.get_template(plantilla('eliminar'))
        contexto = {
            'tipoDeAtencion' : tipoDeAtencion
        }

        return HttpResponse( template.render( contexto, peticion) )


