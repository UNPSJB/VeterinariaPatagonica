from django.template import loader
from django.http import HttpResponse


class VeterinariaPatagonicaError(Exception):

    def __init__(self, titulo="Error", descripcion="No se pudo completar la accion solicitada", *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.titulo = titulo
        self.descripcion = descripcion


class ManejadorErrores:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):

        if isinstance(exception, VeterinariaPatagonicaError):

            template = loader.get_template("error.html")
            context = {
                "titulo" : exception.titulo,
                "descripcion" : exception.descripcion,
            }

            return HttpResponse(template.render( context, request ))
