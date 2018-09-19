from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

def insumos(request):
    context = {}#Defino un contexto.
    template = loader.get_template('GestionDeInsumos/GestionDeInsumos.html')#Cargo el template desde la carpeta templates/GestionDeInsumos.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.

def alta(request):
    context = {}#Defino un contexto.
    #template = loader.get_template('VeterinariaPatagonica/templates/demos/altainsumo.html')
    template = loader.get_template('demos/altainsumo.html')#Cargo el template desde la carpeta demos.
    return HttpResponse(template.render(context,request))#Devuelvo la url con el template armado.
