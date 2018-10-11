from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
#from django import forms
from django.core.exceptions import ObjectDoesNotExist

from .models import Practica
#from .forms import *

# Create your views here.
def verHabilitadas(request):
    practicas = Practica.objects.filter(baja=False)
    template = loader.get_template('GestionDePracticas/verHabilitadas.html')
    context = {
        'practicas' : practicas,
        'usuario' : request.user
    }
    return HttpResponse(template.render( context, request ))
