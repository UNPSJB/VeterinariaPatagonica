from django.shortcuts import render
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from .models import Mascota
from .forms import MascotaFormFactory, FiltradoForm
from VeterinariaPatagonica import tools
from dal import autocomplete
from django.db.models import Q
from django.urls import reverse_lazy
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Apps.GestionDeClientes.models import Cliente
from VeterinariaPatagonica.tools import GestorListadoQuerySet

def mascota(request):
    context = {}
    template = loader.get_template('GestionDeMascotas/GestionDeMascotas.html')
    return HttpResponse(template.render(context, request))


@permission_required('GestionDeMascotas.deshabilitar_mascota', raise_exception=True)
def dispatch(self, *args, **kwargs):
    return super(Mascota, self).dispatch(*args, **kwargs)

def menuVer(usuario, mascota):

    menu = [[],[],[]]

    if usuario.has_perm("GestionDeMascotas.mascota_modificar"):
        menu[0].append( (reverse("mascotas:mascotaModificar", args=(mascota.id,)), "Modificar mascota") )
        if mascota.baja:
            menu[0].append( (reverse("mascotas:mascotaHabilitar", args=(mascota.id,)), "Habilitar mascota") )
        else:
            menu[0].append( (reverse("mascotas:mascotaDeshabilitar", args=(mascota.id,)), "Deshabilitar mascota") )

    if usuario.has_perm("GestionDeMascotas.mascota_listar_habilitados"):
        menu[1].append( (reverse("mascotas:mascotaVerHabilitados"), "Listar mascotas habilitadas") )
    if usuario.has_perm("GestionDeMascotas.mascota_listar_no_habilitados"):
        menu[1].append( (reverse("mascotas:mascotaVerDeshabilitados"), "Listar mascotas deshabilitadas") )

    if usuario.has_perm("GestionDeMascotas.mascota_crear"):
        menu[2].append( (reverse("mascotas:mascotaCrear"), "Crear mascota") )

    return [ item for item in menu if len(item) ]

def menuListar(usuario, habilitados):
    menu = [[],[]]

    if (not habilitados) and usuario.has_perm("GestionDeMascotas.mascota_ver_habilitados"):
        menu[0].append( (reverse("mascotas:mascotaVerHabilitados"), "Listar mascotas habilitadas") )
    if habilitados and usuario.has_perm("GestionDeMascotas.mascota_ver_no_habilitados"):
        menu[0].append( (reverse("mascotas:mascotaVerDeshabilitados"), "Listar mascotas deshabilitadas") )

    if usuario.has_perm("GestionDeMascotas.mascota_crear"):
        menu[1].append( (reverse("mascotas:mascotaCrear"), "Crear Mascota") )
    return [ item for item in menu if len(item) ]

def menuModificar(usuario, mascota):

    menu = [[],[],[],[]]

    menu[0].append( (reverse("mascotas:mascotaVer", args=(mascota.id,)), "Ver mascota") )

    if mascota.baja:
        menu[1].append( (reverse("mascotas:mascotaHabilitar", args=(mascota.id,)), "Habilitar mascota") )
    else:
        menu[1].append( (reverse("mascotas:mascotaDeshabilitar", args=(mascota.id,)), "Deshabilitar mascota") )

    if usuario.has_perm("GestionDeMascotas.mascota_listar_habilitados"):
        menu[2].append( (reverse("mascotas:mascotaVerHabilitados"), "Listar mascotas habilitadas") )
    if usuario.has_perm("GestionDeMascotas.mascota_listar_no_habilitados"):
        menu[2].append( (reverse("mascotas:mascotaVerDeshabilitados"), "Listar mascotas deshabilitadas") )

    if usuario.has_perm("GestionDeMascotas.mascota_crear"):
        menu[3].append( (reverse("mascotas:mascotaCrear"), "Crear mascota") )

    return [ item for item in menu if len(item) ]

def menuCrear(usuario, mascota):

    menu = [[],[],[],[]]

    if usuario.has_perm("GestionDeMascotas.mascota_listar_habilitados"):
        menu[0].append( (reverse("mascotas:mascotaVerHabilitados"), "Listar mascotas habilitados") )
    if usuario.has_perm("GestionDeMascotas.mascota_listar_no_habilitados"):
        menu[0].append( (reverse("mascotas:mascotaVerDeshabilitados"), "Listar mascotas deshabilitados") )

    return [ item for item in menu if len(item) ]

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeMascotas.add_Mascota', raise_exception=True)
def modificar(request, id= None, cliente_id=None):
    mascota = Mascota.objects.get(id=id) if id is not None else None
    mascota = None
    if cliente_id:
        mascota = Cliente.objects.get(pk=cliente_id)
    MascotaForm = MascotaFormFactory(mascota, mascota)

    if (id==None):
        context = {"titulo": 1, 'usuario': request.user}
    else:
        context = {"titulo": 2, 'usuario': request.user}

    if request.method == 'POST':
        formulario = MascotaForm(request.POST, instance=mascota)


        if formulario.is_valid():
            mascota = formulario.save()
            mascota.generadorDePatente(mascota.id)
            mascota = formulario.save()
            return HttpResponseRedirect("/GestionDeMascotas/ver/{}".format(mascota.id))
        else:
            context['form'] = formulario
            context['menu'] = menuModificar(request.user, mascota)
    else:
        context['form'] = MascotaForm(instance=mascota)
        context['menu'] = menuCrear(request.user, mascota)
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
        return HttpResponseRedirect( "/GestionDeMascotas/verDeshabilitados/" )
    else:
        template = loader.get_template('GestionDeMascotas/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }
        return HttpResponse( template.render( context, request) )

def ver(request, id):

    try:
        mascota = Mascota.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404("No encontrado", "La mascota con patente={} no existe.".format(id))


    template = loader.get_template('GestionDeMascotas/ver.html')
    contexto = {
        'mascota': mascota,
        'usuario': request.user,
        "menu" : menuVer(request.user, mascota)
    }
    return HttpResponse(template.render(contexto, request))



def verHabilitados(request, habilitados=True):

    mascotas = Mascota.objects.habilitados()
    gestor = GestorListadoQuerySet(
        campos=[
            ["orden_patente", "Patente"],
            ["orden_nombre", "Nombre"],
            ["orden_cliente", "Dueño"],
            ["orden_especie", "Especie"],
        ],
        clases={"filtrado" : FiltradoForm},
        queryset=mascotas,
        mapaFiltrado= Mascota.MAPPER,
        mapaOrden= mascotas.MAPEO_ORDEN
    )
  
    gestor.cargar(request)

    template = loader.get_template('GestionDeMascotas/verHabilitados.html')
    contexto = {
        "gestor" : gestor,
        "menu" : menuListar(request.user, habilitados),}
    return HttpResponse(template.render(contexto, request))

def verDeshabilitados(request, habilitados=False):
    mascotas = Mascota.objects.deshabilitados()
    gestor = GestorListadoQuerySet(
        campos=[
            ["orden_patente", "Patente"],
            ["orden_nombre", "Nombre"],
            ["orden_cliente", "Dueño"],
            ["orden_especie", "Especie"],
        ],
        clases={"filtrado" : FiltradoForm},
        queryset=mascotas,
        mapaFiltrado= Mascota.MAPPER,
        mapaOrden= mascotas.MAPEO_ORDEN
    )
  
    gestor.cargar(request)

    template = loader.get_template('GestionDeMascotas/verDeshabilitados.html')
    contexto = {
        "gestor" : gestor,
        "menu" : menuListar(request.user, habilitados),}
    return HttpResponse(template.render(contexto, request))

class clienteAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = Cliente.objects.all()

        if self.q:
            qs = qs.filter(Q(apellidos__icontains=self.q) |Q(nombres__icontains=self.q) | Q(dniCuit__icontains=self.q))

        return qs

@login_required
def ayudaContextualMascota(request):

    template = loader.get_template('GestionDeMascotas/ayudaContextualMascota.html')
    contexto = {
        'usuario': request.user,
    }

    return HttpResponse(template.render(contexto, request))
