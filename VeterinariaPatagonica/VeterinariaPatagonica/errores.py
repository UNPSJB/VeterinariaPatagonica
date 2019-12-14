from django.template import loader
from django.urls import reverse
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser



class VeterinariaPatagonicaError(Exception):

    def __init__(self, titulo="Error", descripcion="No se pudo completar la accion solicitada", **kwargs):
        super().__init__()
        self.titulo = titulo
        self.descripcion = descripcion
        self.kwargs = {}
        self.kwargs.update(kwargs)

    def error(self):
        return {
            "titulo" : self.titulo,
            "descripcion" : self.descripcion
        }



class ManejadorErrores:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):

        if not isinstance(request.user, AnonymousUser):

            if isinstance(exception, VeterinariaPatagonicaError):
                template = loader.get_template("error.html")
                context = {
                    "excepciones" : [ exception ]
                }
                return HttpResponse(template.render( context, request ))

            elif isinstance(exception, PermissionDenied):
                mensaje = "La pagina del sitio solicitada no esta permitida para el usuario '%s' de '%s'."
                template = loader.get_template("error.html")
                context = {
                    "excepciones" : [VeterinariaPatagonicaError(
                        "Permiso denegado",
                        mensaje % (request.user, request.user.grupo().name)
                    )]
                }
                return HttpResponse(template.render( context, request ))

