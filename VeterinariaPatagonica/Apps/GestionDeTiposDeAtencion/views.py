from os.path import join as pathjoin

from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django import forms

from .models import TipoDeAtencion
from .forms import TipoDeAtencionForm, ModificacionTipoDeAtencionForm, FiltradoForm
from VeterinariaPatagonica.tools import GestorListadoQuerySet
from django.contrib.auth.decorators import login_required


LOGIN_URL = '/login/'

def plantilla(*ruta):
    return pathjoin("GestionDeTiposDeAtencion", *ruta) + ".html"


def permisosModificar(tipoDeAtencion):
    permisos = ["GestionDeTiposDeAtencion.tipodeatencion_modificar"]
    if tipoDeAtencion.baja:
        permisos.append("GestionDeTiposDeAtencion.tipodeatencion_ver_no_habilitados")
    else:
        permisos.append("GestionDeTiposDeAtencion.tipodeatencion_ver_habilitados")
    return permisos


def menuModificar(usuario, tipoDeAtencion):

    menu = [[],[],[],[]]

    menu[0].append( (reverse("tiposDeAtencion:ver", args=(tipoDeAtencion.id,)), "Ver tipo de atención") )

    if tipoDeAtencion.baja:
        menu[1].append( (reverse("tiposDeAtencion:habilitar", args=(tipoDeAtencion.id,)), "Habilitar tipo de atención") )
    else:
        menu[1].append( (reverse("tiposDeAtencion:deshabilitar", args=(tipoDeAtencion.id,)), "Deshabilitar tipo de atención") )

    if usuario.has_perm("GestionDeTiposDeAtencion.tipodeatencion_listar_habilitados"):
        menu[2].append( (reverse("tiposDeAtencion:habilitados"), "Listar tipos de atención habilitados") )
    if usuario.has_perm("GestionDeTiposDeAtencion.tipodeatencion_listar_no_habilitados"):
        menu[2].append( (reverse("tiposDeAtencion:deshabilitados"), "Listar tipos de atención deshabilitados") )

    if usuario.has_perm("GestionDeTiposDeAtencion.tipodeatencion_crear"):
        menu[3].append( (reverse("tiposDeAtencion:crear"), "Crear tipo de atención") )

    return [ item for item in menu if len(item) ]



def permisosVer(tipoDeAtencion):
    permisos = []
    if tipoDeAtencion.baja:
        permisos.append("GestionDeTiposDeAtencion.tipodeatencion_ver_no_habilitados")
    else:
        permisos.append("GestionDeTiposDeAtencion.tipodeatencion_ver_habilitados")
    return permisos



def menuVer(usuario, tipoDeAtencion):

    menu = [[],[],[]]

    if usuario.has_perm("GestionDeTiposDeAtencion.tipodeatencion_modificar"):
        menu[0].append( (reverse("tiposDeAtencion:modificar", args=(tipoDeAtencion.id,)), "Modificar tipo de atención") )
        if tipoDeAtencion.baja:
            menu[0].append( (reverse("tiposDeAtencion:habilitar", args=(tipoDeAtencion.id,)), "Habilitar tipo de atención") )
        else:
            menu[0].append( (reverse("tiposDeAtencion:deshabilitar", args=(tipoDeAtencion.id,)), "Deshabilitar tipo de atención") )

    if usuario.has_perm("GestionDeTiposDeAtencion.tipodeatencion_listar_habilitados"):
        menu[1].append( (reverse("tiposDeAtencion:habilitados"), "Listar tipos de atención habilitados") )
    if usuario.has_perm("GestionDeTiposDeAtencion.tipodeatencion_listar_no_habilitados"):
        menu[1].append( (reverse("tiposDeAtencion:deshabilitados"), "Listar tipos de atención deshabilitados") )

    if usuario.has_perm("GestionDeTiposDeAtencion.tipodeatencion_crear"):
        menu[2].append( (reverse("tiposDeAtencion:crear"), "Crear tipo de atención") )

    return [ item for item in menu if len(item) ]



def permisosListar(habilitados):
    permisos = []
    if habilitados:
        permisos.append("GestionDeTiposDeAtencion.tipodeatencion_listar_habilitados")
    else:
        permisos.append("GestionDeTiposDeAtencion.tipodeatencion_listar_no_habilitados")
    return permisos



def menuListar(usuario, habilitados):
    menu = [[],[]]

    if (not habilitados) and usuario.has_perm("GestionDeTiposDeAtencion.tipodeatencion_listar_habilitados"):
        menu[0].append( (reverse("tiposDeAtencion:habilitados"), "Listar tipos de atención habilitados") )
    if habilitados and usuario.has_perm("GestionDeTiposDeAtencion.tipodeatencion_listar_no_habilitados"):
        menu[0].append( (reverse("tiposDeAtencion:deshabilitados"), "Listar tipos de atención deshabilitados") )

    if usuario.has_perm("GestionDeTiposDeAtencion.tipodeatencion_crear"):
        menu[1].append( (reverse("tiposDeAtencion:crear"), "Crear tipo de atención") )
    return [ item for item in menu if len(item) ]



def listar(request, habilitados=True):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (LOGIN_URL, request.path))

    if not request.user.has_perms(permisosListar(habilitados)):
        raise PermissionDenied()

    if habilitados:
        queryset = TipoDeAtencion.objects.habilitados()
    else:
        queryset = TipoDeAtencion.objects.deshabilitados()

    gestor = GestorListadoQuerySet(
        campos = [
            ["nombre", "Nombre"],
            ["emergencia", "Emergencia"],
            ["lugar", "Lugar de atencion"],
            ["recargo", "Recargo"],
            ["iniciofranjahoraria", "Franja Horaria"],
        ],
        clases={"filtrado" : FiltradoForm},
        queryset=queryset,
        mapaFiltrado=queryset.MAPEO_FILTRADO,
        mapaOrden=queryset.MAPEO_ORDEN
    )

    gestor.cargar(request)
    gestor.paginacion["cantidad"].label = "Resultados por página"

    template = loader.get_template( plantilla("listar") )
    context = {
        "gestor" : gestor,
        "tipo" : "habilitados" if habilitados else "deshabilitados",
        "menu" : menuListar(request.user, habilitados),
    }
    return HttpResponse(template.render( context, request ))



def ver(request, id):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (LOGIN_URL, request.path))

    tipoDeAtencion = TipoDeAtencion.objects.get(id=id)
    if not request.user.has_perms(permisosVer(tipoDeAtencion)):
        raise PermissionDenied()

    context = {
        "tipoDeAtencion" : tipoDeAtencion,
        "menu" : menuVer(request.user, tipoDeAtencion)
    }

    template = loader.get_template(plantilla("ver"))
    return HttpResponse(template.render( context, request ))



def crear(request):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (LOGIN_URL, request.path))

    if not request.user.has_perm("GestionDeTiposDeAtencion.tipodeatencion_crear"):
        raise PermissionDenied()

    if request.method == "POST":
        tipoDeAtencion = TipoDeAtencion()
        form = TipoDeAtencionForm(request.POST, instance=tipoDeAtencion)

        if form.is_valid():
            tipoDeAtencion = form.save()
            return HttpResponseRedirect( reverse("tiposDeAtencion:ver", args=(tipoDeAtencion.id,)) )

    else:
        form = TipoDeAtencionForm()

    menu = [[]]
    if request.user.has_perm("GestionDeTiposDeAtencion.tipodeatencion_listar_habilitados"):
        menu[0].append( (reverse("tiposDeAtencion:habilitados"), "Listar tipos de atención habilitados") )
    if request.user.has_perm("GestionDeTiposDeAtencion.tipodeatencion_listar_no_habilitados"):
        menu[0].append( (reverse("tiposDeAtencion:deshabilitados"), "Listar tipos de atención deshabilitados") )

    context = {
        "accion" : "crear",
        "form" : form,
        "menu" : [ item for item in menu if len(item) ]
    }
    template = loader.get_template(plantilla("crear"))
    return HttpResponse(template.render( context, request) )



def modificar(request, id):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (LOGIN_URL, request.path))

    tipoDeAtencion = TipoDeAtencion.objects.get(id=id)
    if not request.user.has_perms(permisosModificar(tipoDeAtencion)):
        raise PermissionDenied()

    if request.method == "POST":
        form = ModificacionTipoDeAtencionForm(request.POST, instance=tipoDeAtencion)

        if form.is_valid():
            if form.has_changed():
                form.save()
            return HttpResponseRedirect( reverse("tiposDeAtencion:ver", args=(tipoDeAtencion.id,)) )

    else:
        form = ModificacionTipoDeAtencionForm(instance=tipoDeAtencion)

    context = {
        "accion" : "modificar",
        "form" : form,
        "menu" : menuModificar(request.user, tipoDeAtencion)
    }

    template = loader.get_template(plantilla("modificar"))
    return HttpResponse(template.render( context, request) )



def cambioEstado(request, id, baja=False):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect("%s?proxima=%s" % (LOGIN_URL, request.path))

    tipoDeAtencion = TipoDeAtencion.objects.get(id=id)
    permisos = ["GestionDeTiposDeAtencion.tipodeatencion_modificar"]
    if tipoDeAtencion.baja:
        permisos.append("GestionDeTiposDeAtencion.tipodeatencion_ver_no_habilitados")
    else:
        permisos.append("GestionDeTiposDeAtencion.tipodeatencion_ver_habilitados")

    if not request.user.has_perms(permisos):
        raise PermissionDenied()

    if tipoDeAtencion.baja != baja:
        tipoDeAtencion.baja = baja
        tipoDeAtencion.save()

    return HttpResponseRedirect( reverse("tiposDeAtencion:ver", args=(tipoDeAtencion.id,)) )


@login_required
def ayudaContextualTipoDeAtencion(request):

    template = loader.get_template('GestionDeTiposDeAtencion/ayudaContextualTiposdeAtencion.html')
    contexto = {
        'usuario': request.user,
    }

    return HttpResponse(template.render(contexto, request))