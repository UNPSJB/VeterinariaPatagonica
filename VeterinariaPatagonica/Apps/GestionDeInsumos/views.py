from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from .models import Insumo
from .forms import InsumoFormFactory


def insumos(request):
    context = {}#Defino un contexto.
    template = loader.get_template('GestionDeInsumos/GestionDeInsumos.html')#Cargo el template desde la carpeta templates/GestionDeInsumos.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeInsumos.add_Insumo', raise_exception=True)
def modificar(request, id = None):
    insumo = Insumo.objects.get(id=id) if id is not None else None
    InsumoForm = InsumoFormFactory(insumo)
    context = {'usuario' : request.user}

    if request.method == 'POST':
        formulario = InsumoForm(request.POST, instance=insumo)
        if formulario.is_valid():
            insumo = formulario.save()
            return HttpResponseRedirect("/GestionDeInsumos/ver/{}".format(insumo.id))
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = InsumoForm(instance=insumo)
    template = loader.get_template('GestionDeInsumos/formulario.html')

    return HttpResponse(template.render( context, request) )

def verHabilitados(request):
    insumos = Insumo.objects.filter(baja=False)
    template = loader.get_template('GestionDeInsumos/verHabilitados.html')
    context = {
        'insumos': insumos,
        'usuario': request.user
    }
    return HttpResponse(template.render(context, request))

def verDeshabilitados(request):
    insumos = Insumo.objects.filter(baja=True)
    template = loader.get_template('GestionDeInsumos/verDeshabilitados.html')
    context = {
        'insumos' : insumos,
        'usuario' : request.user
    }
    return HttpResponse(template.render( context, request ))

def ver(request, id):
    #import ipdb; ipdb.set_trace()
    try:
        insumo = Insumo.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404( "No encontrado", "El insumo con id={} no existe.".format(id))

    template = loader.get_template('GestionDeInsumos/ver.html')
    context = {
        'insumo': insumo,
        'usuario': request.user
    }
    return HttpResponse(template.render(context, request))


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeInsumos.delete_Insumo', raise_exception=True)
def deshabilitar(request, id):

    try:
        insumo = Insumo.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    insumo.baja = True
    insumo.save()

    return HttpResponseRedirect( "/GestionDeInsumos/verDeshabilitados/" )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeInsumos.delete_Insumo', raise_exception=True)
def habilitar(request, id):
    try:
        insumo = Insumo.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    insumo.baja = False
    insumo.save()

    return HttpResponseRedirect( "/GestionDeInsumos/verHabilitados/" )


@login_required(redirect_field_name='proxima')
@permission_required('GestionDeInsumos.delete_Insumo', raise_exception=True)
def eliminar(request, id):

    try:
        insumo = Insumo.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    if request.method == 'POST':
        insumo.delete()
        return HttpResponseRedirect( "/GestionDeInsumos/" )

    else:
        template = loader.get_template('GestionDeInsumos/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }

    return HttpResponse( template.render( context, request) )





'''
@login_required(redirect_field_name='proxima')
@permission_required('GestionDeClientes.add_Cliente', raise_exception=True)
def modificar(request, id = None):
    cliente = Cliente.objects.get(id=id) if id is not None else None
    ClienteForm = ClienteFormFactory(cliente)
    context = {'usuario': request.user}
    if request.method == 'POST':
        formulario = ClienteForm(request.POST, instance=cliente)
        if formulario.is_valid():
            cliente = formulario.save()
            return HttpResponseRedirect("/GestionDeClientes/ver/{}".format(cliente.id))
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = ClienteForm(instance=cliente)
    template = loader.get_template('GestionDeClientes/formulario.html')
    return HttpResponse(template.render(context, request))
'''

'''
@login_required(redirect_field_name='proxima')
@permission_required('GestionDeInsumos.change_Insumo', raise_exception=True)
def modificar(request, id = None):

    try:
        insumo = Insumo.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    datos = {
        'nombre' : insumo.nombre,
        'formaDePresentacion' : insumo.formaDePresentacion,
        'precioPorUnidad' : insumo.precioPorUnidad,
        'rubro' : insumo.rubro,
        'baja' : insumo.baja
    }

    if request.method == 'POST':

        formulario = ModificacionForm(request.POST, initial=datos)

        if formulario.is_valid():

            if formulario.has_changed():
                formulario.cargar(insumo).save()

            return HttpResponseRedirect("/GestionDeInsumos/ver/{}".format(insumo.id))

    else:

        formulario = ModificacionForm(datos, initial=datos)

    template = loader.get_template('GestionDeInsumos/modificar.html')
    context = {
        'formulario':formulario,
        'insumo':insumo,
        'usuario' : request.user
    }

    return HttpResponse(template.render( context, request) )
'''

















'''
def insumos(request):
    context = {}#Defino un contexto.
    template = loader.get_template('GestionDeInsumos/GestionDeInsumos.html')#Cargo el template desde la carpeta templates/GestionDeInsumos.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.
'''

'''
def alta(request):
    context = {}#Defino un contexto.
    template = loader.get_template('demos/altainsumo.html')#Cargo el template desde la carpeta demos.
    #template = loader.get_template('demos/altainsumo.html')#Cargo el template desde la carpeta demos.
    return HttpResponse(template.render(context,request))#Devuelvo la url con el template armado.
'''
