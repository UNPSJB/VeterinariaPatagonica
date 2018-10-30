from django.shortcuts import render
from django.template import loader
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from .models import Mascota
from .forms import MascotaFormFactory
from VeterinariaPatagonica import tools
from dal import autocomplete
from Apps.GestionDeClientes.models import Cliente


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



def verHabilitados(request):
    mascotas = Mascota.objects.habilitados()
    mascotas = mascotas.filter(tools.paramsToFilter(request.GET, Mascota))
    template = loader.get_template('GestionDeMascotas/verHabilitados.html')
    contexto = {
        'mascotas': mascotas,
        'usuario': request.user,
    }
    return HttpResponse(template.render(contexto, request))

def verDeshabilitados(request):
    mascotas = Mascota.objects.deshabilitados()
    mascotas = mascotas.filter(tools.paramsToFilter(request.GET, Mascota))

    template = loader.get_template('GestionDeMascotas/verDeshabilitados.html')
    contexto = {
        'mascotas': mascotas,
        'usuario': request.user,
    }
    return HttpResponse(template.render(contexto, request))

'''
class clienteAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = Cliente.objects.all()

        if self.q:
            qs = qs.filter(Q(apellidos__icontains=self.q) |Q(nombres__icontains=self.q) | Q(dniCuit__icontains=self.q))

        return qs
'''
