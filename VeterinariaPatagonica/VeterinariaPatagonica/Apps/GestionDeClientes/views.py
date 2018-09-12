from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

def base(request):
    context = {}
    template = loader.get_template('GestionDeClientes/sitio_base.html')
    return HttpResponse(template.render(context, request))

def clientes(request):
    context = {}
    template = loader.get_template('GestionDeClientes/GestionDeClientes.html')
    return HttpResponse(template.render(context, request))
