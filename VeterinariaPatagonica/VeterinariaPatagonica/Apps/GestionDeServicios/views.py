from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

# Create your views here.

def servicios(request):
    context = {}
    template = loader.get_template('GestionDeServicios/GestionDeServicios.html')
    return HttpResponse(template.render(context, request))
