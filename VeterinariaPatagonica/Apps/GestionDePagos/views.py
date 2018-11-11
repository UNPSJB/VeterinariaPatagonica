from django.shortcuts import render
from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from .models import Pagos
from .forms import PagosForm



def Pagos(request):

    context = {}#Defino el contexto.
    template = loader.get_template('GestionDePagos/GestionDePagos.html')#Cargo el template desde la carpeta templates/GestionDePagos.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.


@login_required(redirect_field_name='proxima')
@permission_required('GestionDePagos.add_Pagos', raise_exception=True)
def modificar(request, id = None):

    pagos = Pagos.objects.get(id=id) if id is not None else None
    context = {'usuario': request.user}
    if request.method == 'POST':
        formulario = PagosForm(request.POST, instance=pagos)
        print(formulario)
        if formulario.is_valid():
            pagos = formulario.save()
            return HttpResponseRedirect("/GestionDePagos/ver/{}".format(pagos.id))
        else:
            context['formulario'] = formulario
    else:
        context['formulario'] = PagosForm(instance=pagos)
    template = loader.get_template('GestionDePagos/formulario.html')
    return HttpResponse(template.render(context, request))


@login_required(redirect_field_name='proxima')
@permission_required('GestionDePagos.delete_Pagos', raise_exception=True)
def habilitar(request, id):
    try:
        pagos = Pagos.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    pagos.baja = False
    pagos.save()

    return HttpResponseRedirect( "/GestionDePagos/verHabilitados/" )

@login_required(redirect_field_name='proxima')
@permission_required('GestionDePagos.delete_Pagos', raise_exception=True)
def deshabilitar(request, id):

    try:
        pagos = Pagos.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    pagos.baja = True
    pagos.save()

    return HttpResponseRedirect( "/GestionDePagos/verDeshabilitados/" )

@login_required(redirect_field_name='proxima')
@permission_required('GestionDePagos.delete_Pagos', raise_exception=True)
def eliminar(request, id):

    try:
        pagos = Pagos.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404()

    if request.method == 'POST':

        pagos.delete()
        return HttpResponseRedirect( "/GestionDePagos/" )

    else:

        template = loader.get_template('GestionDePagos/eliminar.html')
        context = {
            'usuario' : request.user,
            'id' : id
        }

        return HttpResponse( template.render( context, request) )

def ver(request, id):

    try:
        pagos = Pagos.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404("No encontrado", "El pago con id={} no existe.".format(id))

    template = loader.get_template('GestionDePagos/ver.html')
    contexto = {
        'pagos': pagos,
        'usuario': request.user
    }

    return HttpResponse(template.render(contexto, request))

def verHabilitados(request):
    pagos = Pagos.objects.filter(baja=False)
    template = loader.get_template('GestionDePagos/verHabilitados.html')
    contexto = {
        'pagos' : pagos,
        'usuario' : request.user,
    }

    return  HttpResponse(template.render(contexto,request))

def verDeshabilitados(request):
    pagos = Pagos.objects.filter(baja=True)
    template = loader.get_template('GestionDePagos/verDeshabilitados.html')
    contexto = {
        'pagos' : pagos,
        'usuario' : request.user,
    }

    return  HttpResponse(template.render(contexto,request))