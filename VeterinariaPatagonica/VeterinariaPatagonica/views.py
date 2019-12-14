from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate as auth_authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response
from .forms import LoginForm
from .errores import VeterinariaPatagonicaError

LOGIN_URL = "/login/"


def index(request):

    if isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect(LOGIN_URL)

    return HttpResponse(
        loader.get_template("sitioBase.html").render(
            {},
            request
        )
    )


def login(request):

    proxima = "/"
    if ("proxima" in request.GET) and (request.GET["proxima"] is not None):
        proxima = request.GET["proxima"]

    if not isinstance(request.user, AnonymousUser):
        return HttpResponseRedirect(proxima)

    contexto = {
        "url_proxima":proxima,
        "url_actual":request.path
    }

    if request.method == "POST":
        formulario = LoginForm(request.POST)

        if formulario.is_valid():
            usr = formulario.cleaned_data["usuario"]
            pwd = formulario.cleaned_data["password"]
            usuario = auth_authenticate(request, username=usr, password=pwd)

            if usuario is not None:
                auth_login(request, usuario)
                return HttpResponseRedirect(proxima)
            else:
                formulario = LoginForm()
                template = loader.get_template("registration/login.html")
                contexto["formulario"] = formulario

    else:
        formulario = LoginForm()
        template = loader.get_template("registration/login.html")
        contexto["formulario"] = formulario

    return HttpResponse(template.render( contexto, request) )


def logout(request):

    if not isinstance(request.user, AnonymousUser):
        auth_logout(request)

    return HttpResponseRedirect(LOGIN_URL)

def ayuda(request):
    return render_to_response('manual/documentacion.html')