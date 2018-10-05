from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

def clientes(request):
    context = {}#Defino el contexto.
    template = loader.get_template('GestionDeClientes/GestionDeClientes.html')#Cargo el template desde la carpeta templates/GestionDeClientes.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.

def alta(request):
    context = {}#Defino el contexto.
    template = loader.get_template('demos/altacliente.html')#Cargo el template desde la carpeta demos.
    return HttpResponse(template.render(context,request))#Devuelvo la url con el template armado.

def crear(request):
    pass

def modificar(request):
    pass

def hablitar(request):
    pass

def deshablitar(request):
    pass

def eliminar(request):
    pass

def ver(request):
    pass

def verHabilitados(request):
    pass

def verDeshabilitados(request):
    pass