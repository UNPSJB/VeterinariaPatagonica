from os.path import join

from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django import forms

from .models import TipoDeAtencion
from .forms import TipoDeAtencionForm
from VeterinariaPatagonica.tools import GestorListadoQueryset

PLANTILLAS = {
    "habilitados" : "habilitados",
    "deshabilitados" : "deshabilitados",
    "ver" : "ver",
    "crear" : "crear",
    "modificar" : "modificar",
    "eliminar" : "eliminar",
}

def plantilla(nombre):
    return join( "GestionDeTiposDeAtencion/", PLANTILLAS[nombre]+".html")



def habilitados(request):
    """ Listado de tipos de atencion habilitados """

    gestor = GestorListadoQueryset(
        orden=[
            ["orden_nombre", "Nombre"],
            ["orden_emergencia", "Emergencia"],
            ["orden_lugar", "Lugar de atencion"],
            ["orden_recargo", "Recargo"],
            ["orden_inicio", "Franja Horaria"],
        ]
    )

    tiposDeAtencion = TipoDeAtencion.objects.habilitados()
    gestor.cargar(request, tiposDeAtencion)
    gestor.ordenar()

    template = loader.get_template( plantilla("habilitados") )
    context = {"gestor" : gestor}
    #raise Exception(str(gestor.encabezado))
    return HttpResponse(template.render( context, request ))



def deshabilitados(request):
    """ Listado de tipos de atencion deshabilitados """

    gestor = GestorListadoQueryset(
        orden=[
            ["orden_nombre", "Nombre"],
            ["orden_emergencia", "Emergencia"],
            ["orden_lugar", "Lugar de atencion"],
            ["orden_recargo", "Recargo"],
            ["orden_inicio", "Franja Horaria"],
        ]
    )

    tiposDeAtencion = TipoDeAtencion.objects.deshabilitados()
    gestor.cargar(request, tiposDeAtencion)
    gestor.ordenar()

    template = loader.get_template( plantilla("deshabilitados") )
    context = {"gestor" : gestor}
    return HttpResponse(template.render( context, request ))



def ver(request, id):
    """ Ver tipo de atencion segun <id> """

    tipoDeAtencion = TipoDeAtencion.objects.get(id=id)

    template = loader.get_template(plantilla("ver"))
    context = {
        "tipoDeAtencion" : tipoDeAtencion
    }

    return HttpResponse(template.render( context, request ))



@login_required(redirect_field_name="proxima")
@permission_required("GestionDeTiposDeAtencion.add_TipoDeAtencion", raise_exception=True)
def crear(request):
    """ Dar de alta un nuevo tipo de atencion """

    if request.method == "POST":

        tipoDeAtencion = TipoDeAtencion()
        form = TipoDeAtencionForm(request.POST, instance=tipoDeAtencion)

        if form.is_valid():

            tipoDeAtencion = form.save()

            return HttpResponseRedirect( reverse("tiposDeAtencion:ver", args=(tipoDeAtencion.id,)) )
        else:
            context = { "form" : form }

    else:

        context = { "form" : TipoDeAtencionForm() }

    template = loader.get_template(plantilla("crear"))
    return HttpResponse(template.render( context, request) )



@login_required(redirect_field_name="proxima")
@permission_required("GestionDeTiposDeAtencion.change_TipoDeAtencion", raise_exception=True)
def modificar(request, id):
    """ Modificar tipo de atencion con clave primaria <id> """

    tipoDeAtencion = TipoDeAtencion.objects.get(id=id)

    if request.method == "POST":

        form = TipoDeAtencionForm(request.POST, instance=tipoDeAtencion)

        if form.is_valid():

            if form.has_changed():
                form.save()

            return HttpResponseRedirect( reverse("tiposDeAtencion:ver", args=(tipoDeAtencion.id,)) )

    else:

        form = TipoDeAtencionForm(instance=tipoDeAtencion)

    context = {
        "form":form,
        "tipoDeAtencion":tipoDeAtencion
    }

    template = loader.get_template(plantilla("modificar"))
    return HttpResponse(template.render( context, request) )



@login_required(redirect_field_name="proxima")
@permission_required("GestionDeTiposDeAtencion.delete_TipoDeAtencion", raise_exception=True)
def deshabilitar(request, id):
    """ Deshablitar el tipo de atencion con clave primaria <id> """

    tipoDeAtencion = TipoDeAtencion.objects.get(id=id)

    tipoDeAtencion.baja = True
    tipoDeAtencion.save()

    return HttpResponseRedirect( reverse("tiposDeAtencion:ver", args=(tipoDeAtencion.id,)) )


@login_required(redirect_field_name="proxima")
@permission_required("GestionDeTiposDeAtencion.delete_TipoDeAtencion", raise_exception=True)
def habilitar(request, id):
    """ Hablitar el tipo de atencion con clave primaria <id> """

    tipoDeAtencion = TipoDeAtencion.objects.get(id=id)

    tipoDeAtencion.baja = False
    tipoDeAtencion.save()

    return HttpResponseRedirect( reverse("tiposDeAtencion:ver", args=(tipoDeAtencion.id,)) )



@login_required(redirect_field_name="proxima")
@permission_required("GestionDeTiposDeAtencion.delete_TipoDeAtencion", raise_exception=True)
def eliminar(request, id):
    """ Eliminar el tipo de atencion con clave primaria <id> """

    tipoDeAtencion = TipoDeAtencion.objects.get(id=id)
    tipoDeAtencion.delete()

    template = loader.get_template(plantilla("eliminar"))
    return HttpResponse( template.render({}, request) )

@login_required
def ayudaContextualTipoDeAtencion(request):

    template = loader.get_template('GestionDeTiposDeAtencion/GestindeTiposdeAtencin.html')
    contexto = {
        'usuario': request.user,
    }

    return HttpResponse(template.render(contexto, request))