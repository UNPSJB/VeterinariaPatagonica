from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

# Create your views here.
from django.template import loader
from django.http import HttpResponse

def mascota(request):
    context = {}
    template = loader.get_template('GestionDeMascotas/GestionDeMascotas.html')
    return HttpResponse(template.render(context, request))
