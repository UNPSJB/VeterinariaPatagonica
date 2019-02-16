from os.path import join

from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django import forms

from .models import TipoDeAtencion
from .forms import TipoDeAtencionForm



PLANTILLAS = {
    "habilitados" : "habilitados",
    "deshabilitados" : "deshabilitados",
    "ver" : "ver",
    "crear" : "crear",
    "modificar" : "modificar",
    "eliminar" : "eliminar"
}

def plantilla(nombre):
    return join( "GestionDeTiposDeAtencion/", PLANTILLAS[nombre]+".html")



def habilitados(request):
    """ Listado de tipos de atencion habilitados """

    tiposDeAtencion = TipoDeAtencion.objects.habilitados()

    template = loader.get_template( plantilla("habilitados") )

    context = {
        "tiposDeAtencion" : tiposDeAtencion
    }

    return HttpResponse(template.render( context, request ))



def deshabilitados(request):
    """ Listado de tipos de atencion deshabilitados """

    tiposDeAtencion = TipoDeAtencion.objects.deshabilitados()

    template = loader.get_template(plantilla("deshabilitados"))

    context = {
        "tiposDeAtencion" : tiposDeAtencion
    }

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

    if request.method == "POST":

        tipoDeAtencion.delete()
        return HttpResponseRedirect( reverse("tiposDeAtencion:deshabilitados") )

    else:

        context = { "tipoDeAtencion" : tipoDeAtencion }

        template = loader.get_template(plantilla("eliminar"))
        return HttpResponse( template.render( context, request) )
