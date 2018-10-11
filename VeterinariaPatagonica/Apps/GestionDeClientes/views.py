from django.shortcuts import render
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from .models import Cliente
from .forms import ClienteForm

def clientes(request):
    context = {}#Defino el contexto.
    template = loader.get_template('GestionDeClientes/GestionDeClientes.html')#Cargo el template desde la carpeta templates/GestionDeClientes.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeClientes.add_Cliente', raise_exception=True)
def crear(request):
    context = {'usuario' : request.user}
    if request.method == 'POST':
        formulario = ClienteForm(request.POST)
        if formulario.is_valid():
            cliente = formulario.save()
            return HttpResponseRedirect("/GestionDeClientes/ver/{}".format(cliente.id))
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = ClienteForm()
    template = loader.get_template('GestionDeClientes/formulario.html')
    return HttpResponse(template.render( context, request) )

def modificar(request, id):
    cliente = Cliente.objects.get(id=id)
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

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeClientes.delete_Cliente', raise_exception=True)
def habilitar(request, id):

    try:
        cliente = Cliente.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    cliente.baja = False
    cliente.save()

    return HttpResponseRedirect( "/GestionDeClientes/ver/{}".format(cliente.id) )

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeCliente.delete_Cliente', raise_exception=True)
def deshabilitar(request, id):

    try:
        cliente = Cliente.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    cliente.baja = True
    cliente.save()

    return HttpResponseRedirect( "/GestionDeClientes/ver/{}".format(cliente.id) )

@login_required(redirect_field_name='proxima')
@permission_required('GestionDeClientes.delete_Cliente', raise_exception=True)
def eliminar(request, id):

    try:
        cliente = Cliente.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    if request.method == 'POST':

        cliente.delete()
        return HttpResponseRedirect( "/GestionDeClientes/" )

    else:

        template = loader.get_template('GestionDeClientes/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }

        return HttpResponse( template.render( context, request) )

def ver(request, id):

    try:
        cliente = Cliente.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404("No encontrado", "El cliente con id={} no existe.".format(id))

    template = loader.get_template('GestionDeClientes/ver.html')
    contexto = {
        'cliente': cliente,
        'usuario': request.user
    }

    return HttpResponse(template.render(contexto, request))

def verHabilitados(request):
    clientes = Cliente.objects.filter(baja=False)
    template = loader.get_template('GestionDeClientes/verHabilitados.html')
    contexto = {
        'clientes' : clientes,
        'usuario' : request.user,
    }

    return  HttpResponse(template.render(contexto,request))

def verDeshabilitados(request):
    clientes = Cliente.objects.filter(baja=True)
    template = loader.get_template('GestionDeClientes/verDeshabilitados.html')
    contexto = {
        'clientes' : clientes,
        'usuario' : request.user,
    }

    return  HttpResponse(template.render(contexto,request))