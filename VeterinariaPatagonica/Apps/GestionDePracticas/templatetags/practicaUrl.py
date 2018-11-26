from django.template import Library
from django.urls import reverse

from Apps.GestionDePracticas.urls import app_name

register = Library()

@register.inclusion_tag("GestionDePracticas/tags/practicaUrl.html")
def practicaUrl(tipo, *args, **kwargs):

    pathNames = [ app_name, tipo.lower() ]
    pathNames.extend(args)

    return { "url" : reverse(":".join(pathNames), kwargs=kwargs) }
