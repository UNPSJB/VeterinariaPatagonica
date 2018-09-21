from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
#from django.shortcuts import render_to_response
def servicios(request):
    context = {}#Defino el contexto.
    template = loader.get_template('GestionDeServicios/GestionDeServicios.html')#Cargo el template desde la carpeta templates/GestionDeServicios.
    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado

def alta(request):
    context = {}#Defino el contexto.
    template = loader.get_template('demos/altaservicio.html')#Cargo el template desde la carpeta demos.

    return HttpResponse(template.render(context, request))#Devuelvo la url con el template armado.
'''
def alta(request):
    return render_to_response('VeterinariaPatagonica/templates/demos/altainsumo.html',request)
'''
