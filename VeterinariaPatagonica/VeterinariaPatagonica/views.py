'''
from django.shortcuts import render_to_response

from django.template import loader
from django.http import HttpResponse

    def verdemo(request):
        context = {}
        template = request.path.split('/')[-1]
        #printf(template)
        tmp = loader.get_template('demos/'+template)
        #return render_to_response("demos/" + template, request)
        return HttpResponse(tmp.render(context, request))

def base(request):
    return render_to_response('sitio_base.html',request)
'''
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.exceptions import PermissionDenied
from .forms import LoginForm
from .errores import VeterinariaPatagonicaError
# from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

def verdemo(request):
    template = request.path.split('/')[-1]
    return render_to_response("demos/" + template, request)

def base(request):
    #[BUG]no funciona con render_to_response.
    #return render_to_response("sitio_base.html",request)
    context = {}#Defino un contexto.
    template = loader.get_template('sitioBase.html')#Cargo el template del sitio base.
    return HttpResponse(template.render(context,request))#Devuelvo la url con el template armado.

@login_required
def index(request):
    return render_to_response('sitioBase.html')

# @user_passes_test(lambda u: u.is_anonymous)
def login(peticion):

    # if peticion.user.is_authenticated():
    #     print("ESTAS AUTENTICADO")

    proxima = peticion.GET.get('proxima', default='/')
    contexto = {
        'url_proxima':proxima,
        'url_actual':peticion.path
    }

    if peticion.method == 'POST':

        formulario = LoginForm(peticion.POST)

        if formulario.is_valid():

            usr = formulario.cleaned_data['usuario']
            pwd = formulario.cleaned_data['password']
            usuario = authenticate( peticion, username=usr, password=pwd )

            if usuario is not None:

                auth_login(peticion, usuario)
                return HttpResponseRedirect(proxima)

        raise PermissionDenied()

    else:

        formulario = LoginForm()
        template = loader.get_template('registration/login.html')
        contexto['formulario'] = formulario

    return HttpResponse(template.render( contexto, peticion) )

def logout(peticion):

    auth_logout(peticion)
    return HttpResponseRedirect('/login/')


def noEncontrado(request):

    template = loader.get_template("error.html")
    context = {
        "excepciones" : [VeterinariaPatagonicaError(
            "No encontrado",
            "La direccion solicitada no corresponde al sitio."
        )]
    }

    return HttpResponse(template.render( context, request ))

def ayuda(request):
    return render_to_response('manual/documentacion.html')
