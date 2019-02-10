from django.template import Library
from django.urls import reverse
from Apps.GestionDeClientes.urls import app_name

register = Library()

@register.inclusion_tag("GestionDeClientes/tags/clienteUrl.html")
def clienteUrl(*args, **kwargs):

    pathNames = [app_name]
    pathNames.extend(args)

    return { "url" : reverse(":".join(pathNames), kwargs=kwargs) }