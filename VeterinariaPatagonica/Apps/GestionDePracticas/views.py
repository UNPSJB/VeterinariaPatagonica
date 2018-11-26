from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.decorators import login_required, permission_required

from .gestionDePracticas import *
from VeterinariaPatagonica.errores import VeterinariaPatagonicaError
from .models.practica import Practica
from .permisos import *


@login_required(redirect_field_name='proxima')
@permission_required(PERMISOS_PRESUPUESTAR, raise_exception=True)
def completarPresupuesto(request, id, accion):

    try:
        practica = Practica.objects.get(id=id)
        verificarPresupuesto(practica, accion)
    except VeterinariaPatagonicaError as error:
        context = {
            "tipo" : practica.nombreTipo(),
            "errores" : [errorSolicitud(error)],
        }
    else:
        context = { "practica" : practica, "tipo" : practica.nombreTipo(), "errores" : [] }
        hacer = Practica.Acciones(accion).name

        if request.method == "POST":
            form  = ModificarPracticaForm(request.POST, instance=practica)

            if form.is_valid():
                form.save()
                return HttpResponseRedirect(
                    pathActualizar(practica.nombreTipo(), hacer, practica.id)
                )

        else:
            form  = ModificarPracticaForm(instance=practica)

        context["accion"] = hacer.capitalize()
        context["form"] = form

    template = loader.get_template(plantilla("completarPresupuesto"))
    return HttpResponse(template.render(context, request))
